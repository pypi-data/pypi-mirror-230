"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TrialKeeper = void 0;
const events_1 = require("events");
const promises_1 = __importDefault(require("fs/promises"));
const path_1 = __importDefault(require("path"));
const tar_1 = __importDefault(require("tar"));
const http_1 = require("common/command_channel/http");
const globals_1 = __importDefault(require("common/globals"));
const log_1 = require("common/log");
const collect_platform_info_1 = require("./collect_platform_info");
const process_1 = require("./process");
const task_scheduler_client_1 = require("./task_scheduler_client");
class TrialKeeper {
    envId;
    envInfo;
    channels;
    dirs = new Map();
    emitter = new events_1.EventEmitter();
    scheduler;
    log;
    platform;
    trials = new Map();
    gpuEnabled;
    constructor(environmentId, platform, enableGpuScheduling) {
        this.envId = environmentId;
        this.platform = platform;
        this.gpuEnabled = enableGpuScheduling;
        this.log = (0, log_1.getLogger)(`TrialKeeper.${environmentId}`);
        this.scheduler = new task_scheduler_client_1.TaskSchedulerClient(enableGpuScheduling);
        this.scheduler.onUtilityUpdate(info => {
            Object.assign(this.envInfo, info);
            this.emitter.emit('env_update', this.envInfo);
        });
        this.channels = new http_1.HttpChannelServer(this.envId, `/env/${this.envId}`);
        this.channels.onReceive((trialId, command) => {
            this.emitter.emit('command', trialId, command);
            if (command.type !== 'request_parameter' && command.type !== 'metric') {
                this.log.warning(`Unexpected command from trial ${trialId}:`, command);
            }
        });
    }
    async start() {
        this.envInfo = { id: this.envId, type: 'hot' };
        await Promise.all([
            this.scheduler.start(),
            this.channels.start(),
        ]);
        Object.assign(this.envInfo, await (0, collect_platform_info_1.collectPlatformInfo)(this.gpuEnabled));
        return this.envInfo;
    }
    async shutdown() {
        let promises = [
            this.scheduler.shutdown(),
            this.channels.shutdown(),
        ];
        const trials = Array.from(this.trials.values());
        promises = promises.concat(trials.map(trial => trial.kill()));
        await Promise.all(promises);
    }
    registerDirectory(name, path) {
        this.dirs.set(name, path);
    }
    async unpackDirectory(name, tarPath) {
        const extractDir = path_1.default.join(globals_1.default.paths.experimentRoot, 'environments', globals_1.default.args.environmentId, 'upload', name);
        await promises_1.default.mkdir(extractDir, { recursive: true });
        await tar_1.default.extract({ cwd: extractDir, file: tarPath });
        this.registerDirectory(name, extractDir);
    }
    async createTrial(options) {
        const trialId = options.id;
        const gpuEnv = await this.scheduler.schedule(trialId, options.gpuNumber, options.gpuRestrictions);
        if (gpuEnv === null) {
            this.log.info('Scheduling failed because the GPU constraint cannot be satisfied');
            return false;
        }
        const outputDir = path_1.default.join(globals_1.default.paths.experimentRoot, 'environments', this.envId, 'trials', trialId);
        await promises_1.default.mkdir(outputDir, { recursive: true });
        const trial = new process_1.TrialProcess(trialId);
        trial.onStart(timestamp => {
            this.emitter.emit('trial_start', trialId, timestamp);
        });
        trial.onStop((timestamp, exitCode, _signal) => {
            this.emitter.emit('trial_stop', trialId, timestamp, exitCode);
            this.scheduler.release(trialId);
        });
        const procOptions = {
            command: options.command,
            codeDirectory: this.dirs.get(options.codeDirectoryName),
            outputDirectory: outputDir,
            commandChannelUrl: this.channels.getChannelUrl(trialId),
            platform: this.platform,
            sequenceId: options.sequenceId,
            environmentVariables: gpuEnv,
        };
        const success = await trial.spawn(procOptions);
        if (success) {
            this.trials.set(trialId, trial);
            return true;
        }
        else {
            return false;
        }
    }
    async stopTrial(trialId) {
        await this.trials.get(trialId).kill();
    }
    async sendCommand(trialId, command) {
        this.channels.send(trialId, command);
    }
    onTrialStart(callback) {
        this.emitter.on('trial_start', callback);
    }
    onTrialStop(callback) {
        this.emitter.on('trial_stop', callback);
    }
    onReceiveCommand(commandTypeOrCallback, callbackOrNone) {
        if (callbackOrNone) {
            this.emitter.on('command', (trialId, command) => {
                if (command.type === commandTypeOrCallback) {
                    callbackOrNone(trialId, command);
                }
            });
        }
        else {
            this.emitter.on('command', commandTypeOrCallback);
        }
    }
    onEnvironmentUpdate(callback) {
        this.emitter.on('env_update', callback);
    }
}
exports.TrialKeeper = TrialKeeper;
