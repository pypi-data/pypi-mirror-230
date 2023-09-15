"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Worker = void 0;
const promises_1 = __importDefault(require("node:fs/promises"));
const node_path_1 = __importDefault(require("node:path"));
const globals_1 = require("common/globals");
const log_1 = require("common/log");
const pythonScript_1 = require("common/pythonScript");
const rpc_1 = require("common/trial_keeper/rpc");
const ssh_1 = require("./ssh");
class Worker {
    channel;
    channelUrl;
    log;
    python;
    remoteTrialKeeperDir;
    ssh;
    trainingServiceId;
    uploadDir;
    channelId;
    config;
    env;
    trialKeeper;
    get envId() {
        return `${this.trainingServiceId}-worker${this.channelId}`;
    }
    constructor(trainingServiceId, channelId, config, channelUrl, enableGpuScheduling) {
        this.log = (0, log_1.getLogger)(`RemoteV3.Worker.${channelId}`);
        this.trainingServiceId = trainingServiceId;
        this.channelId = channelId;
        this.config = config;
        this.channelUrl = channelUrl;
        this.env = { id: this.envId, host: config.host };
        this.trialKeeper = new rpc_1.RemoteTrialKeeper(this.envId, 'remote', enableGpuScheduling);
        this.ssh = new ssh_1.Ssh(channelId, config);
    }
    setChannel(channel) {
        this.channel = channel;
        this.trialKeeper.setChannel(channel);
        channel.onLost(async () => {
            if (!await this.checkAlive()) {
                this.log.error('Trial keeper failed');
                channel.terminate('Trial keeper failed');
            }
        });
    }
    async start() {
        this.log.info('Initializing SSH worker', this.config.host);
        await this.ssh.connect();
        this.python = await this.findPython();
        this.log.info('Installing nni and dependencies...');
        await this.ssh.run(`${this.python} -m pip install nni --upgrade`);
        const remoteVersion = await this.ssh.run(`${this.python} -c "import nni ; print(nni.__version__)"`);
        this.log.info(`Installed nni v${remoteVersion}`);
        const localVersion = await (0, pythonScript_1.runPythonScript)('import nni ; print(nni.__version__)');
        if (localVersion.trim() !== remoteVersion.trim()) {
            this.log.error(`NNI version mismatch. Local: ${localVersion.trim()} ; SSH server: ${remoteVersion}`);
        }
        await this.launchTrialKeeperDaemon();
        this.env = await this.trialKeeper.start();
        this.env['host'] = this.config.host;
        this.log.info(`Worker ${this.config.host} initialized`);
    }
    async stop() {
        this.log.info('Stop worker', this.config.host);
        await this.trialKeeper.shutdown();
        this.channel.close('shutdown');
    }
    async upload(name, tar) {
        this.log.info('Uploading', name);
        const remotePath = node_path_1.default.join(this.uploadDir, `${name}.tgz`);
        await this.ssh.upload(tar, remotePath);
        await this.trialKeeper.unpackDirectory(name, remotePath);
        this.log.info('Upload success');
    }
    async findPython() {
        let python = await this.findInitPython();
        if (this.config.pythonPath) {
            python = await this.updatePath(python);
        }
        return python;
    }
    async findInitPython() {
        const candidates = [];
        if (this.config.pythonPath) {
            if (!this.config.pythonPath.includes('\\')) {
                candidates.push(this.config.pythonPath + '/python');
                candidates.push(this.config.pythonPath + '/python3');
            }
            if (!this.config.pythonPath.includes('/')) {
                candidates.push(this.config.pythonPath + '\\python');
            }
            candidates.push(this.config.pythonPath);
        }
        candidates.push('python');
        candidates.push('python3');
        let python2;
        for (const python of candidates) {
            const result = await this.ssh.exec(python + ' --version');
            if (result.code !== 0) {
                continue;
            }
            if (this.config.pythonPath) {
                if (result.stdout.startsWith('Python 2')) {
                    python2 = python;
                }
                else {
                    this.log.debug('Python for initializing:', python);
                    return python;
                }
            }
            else {
                this.log.info('Use following python command:', python);
                return python;
            }
        }
        if (python2) {
            this.log.warning('Cannot find python 3, using python 2 for initializing:', python2);
            return python2;
        }
        this.log.error('Cannot find python on SSH server');
        throw new Error(`Cannot find python on SSH server ${this.config.host}`);
    }
    async updatePath(python) {
        if (python === this.config.pythonPath) {
            this.log.error('python_path should be the directory rather than the executable, please check your config');
            return python;
        }
        const os = await this.ssh.run(`${python} -c "import sys ; print(sys.platform)"`);
        const envJson = await this.ssh.run(`${python} -c "import json,os ; print(json.dumps(dict(os.environ)))"`);
        const env = JSON.parse(envJson);
        const delimiter = (os === 'win32' ? ';' : ':');
        this.ssh.setPath(this.config.pythonPath + delimiter + env['PATH']);
        for (const newPython of ['python', 'python3']) {
            const result = await this.ssh.exec(newPython + ' --version');
            if (result.code === 0 && !result.stdout.startsWith('Python 2')) {
                return newPython;
            }
        }
        this.log.error('Cannot find python after adding python_path', this.config.pythonPath);
        throw new Error(`Cannot find python after adding ${this.config.pythonPath} to PATH`);
    }
    async launchTrialKeeperDaemon() {
        const prepareCommand = [
            this.python,
            '-m nni.tools.nni_manager_scripts.create_trial_keeper_dir',
            globals_1.globals.args.experimentId,
            this.envId,
        ].join(' ');
        const trialKeeperDir = await this.ssh.run(prepareCommand);
        const launcherConfig = {
            environmentId: this.envId,
            experimentId: globals_1.globals.args.experimentId,
            logLevel: globals_1.globals.args.logLevel,
            managerCommandChannel: this.channelUrl,
            platform: 'remote',
        };
        this.log.debug('Trial keeper launcher config:', launcherConfig);
        await this.ssh.writeFile(node_path_1.default.join(trialKeeperDir, 'launcher_config.json'), JSON.stringify(launcherConfig));
        const launchCommand = `${this.python} -m nni.tools.nni_manager_scripts.launch_trial_keeper ${trialKeeperDir}`;
        const result = JSON.parse(await this.ssh.run(launchCommand));
        if (!result.success) {
            this.log.error('Failed to launch trial keeper daemon:', result);
            throw new Error('Failed to launch trial keeper daemon');
        }
        this.uploadDir = result.uploadDirectory;
        this.remoteTrialKeeperDir = result.trialKeeperDirectory;
    }
    async checkAlive() {
        try {
            const command = [
                this.python,
                '-m',
                'nni.tools.nni_manager_scripts.check_trial_keeper_alive',
                this.remoteTrialKeeperDir
            ].join(' ');
            const alive = JSON.parse(await this.ssh.run(command));
            if (alive.alive) {
                return true;
            }
            else {
                this.log.error('Trial keeper not alive:', alive);
                return false;
            }
        }
        catch (error) {
            this.log.error('Failed to check trail keeper status:', error);
            return false;
        }
    }
    async downloadTrialLog(trialId) {
        this.log.debug('Downloading trial log:', trialId);
        const localDir = node_path_1.default.join(globals_1.globals.paths.experimentRoot, 'trials', trialId);
        const remoteDir = node_path_1.default.join(node_path_1.default.dirname(this.uploadDir), 'trials', trialId);
        await promises_1.default.mkdir(localDir, { recursive: true });
        for (const file of ['trial.log', 'trial.stdout', 'trial.stderr']) {
            try {
                await this.ssh.download(node_path_1.default.join(remoteDir, file), node_path_1.default.join(localDir, file));
            }
            catch (error) {
                this.log.warning(`Cannot download ${file} of ${trialId}`);
            }
        }
        return localDir;
    }
}
exports.Worker = Worker;
