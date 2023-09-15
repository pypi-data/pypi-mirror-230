"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RemoteTrainingServiceV3 = void 0;
const node_events_1 = require("node:events");
const index_1 = require("common/command_channel/websocket/index");
const log_1 = require("common/log");
const tarball_1 = require("common/tarball");
const worker_1 = require("./worker");
class RemoteTrainingServiceV3 {
    id;
    config;
    emitter = new node_events_1.EventEmitter();
    lastWorkerIndex = 0;
    log;
    server;
    uploadedDirs = new Set();
    workers = [];
    workersByChannel = new Map();
    workersByEnv = new Map();
    workersByTrial = new Map();
    constructor(trainingServiceId, config) {
        this.id = trainingServiceId;
        this.config = config;
        this.log = (0, log_1.getLogger)(`RemoteV3.${this.id}`);
        this.log.debug('Training sevice config:', config);
        this.server = new index_1.WsChannelServer(this.id, `/platform/${this.id}`);
        this.server.on('connection', (channelId, channel) => {
            const worker = this.workersByChannel.get(channelId);
            if (worker) {
                worker.setChannel(channel);
                channel.onClose(reason => {
                    this.log.error('Worker channel closed unexpectedly:', reason);
                });
                channel.onError(error => {
                    this.log.error('Worker channel error:', error);
                    this.restartWorker(worker);
                });
            }
            else {
                this.log.error('Incoming connection from unexpected worker', channelId);
            }
        });
    }
    async init() {
        return;
    }
    async start() {
        this.log.info('Starting remote training service...');
        await this.server.start();
        await Promise.all(this.config.machineList.map(workerConfig => this.launchWorker(workerConfig)));
        this.log.info('Remote training service started');
        return this.workers.map(worker => worker.env);
    }
    async stop() {
        await Promise.allSettled(this.workers.map(worker => worker.stop()));
        this.log.info('All workers stopped');
    }
    async uploadDirectory(name, path) {
        this.log.info(`Upload directory ${name} = ${path}`);
        const tar = await (0, tarball_1.createTarball)(name, path);
        this.uploadedDirs.add(name);
        const workers = Array.from(this.workers);
        const results = await Promise.allSettled(workers.map(worker => worker.upload(name, tar)));
        let fail = false;
        results.forEach((result, i) => {
            if (result.status === 'rejected') {
                this.log.error(`Worker ${workers[i].envId} failed to upload ${name}:`, result.reason);
                this.stopWorker(workers[i], false);
                fail = true;
            }
        });
        if (fail) {
            this.emitEnvUpdate();
        }
    }
    async createTrial(envId, trialCommand, directoryName, sequenceId, trialId) {
        const worker = this.workersByEnv.get(envId);
        if (!worker) {
            this.log.warning('Cannot create trial. Bad environment ID:', envId);
            return null;
        }
        trialId = trialId ?? uuid();
        let gpuNumber = this.config.trialGpuNumber;
        if (gpuNumber) {
            gpuNumber /= worker.config.maxTrialNumberPerGpu;
        }
        const opts = {
            id: trialId,
            command: trialCommand,
            codeDirectoryName: directoryName,
            sequenceId,
            gpuNumber,
            gpuRestrictions: {
                onlyUseIndices: worker.config.gpuIndices,
                rejectActive: !worker.config.useActiveGpu,
            },
        };
        const success = await worker.trialKeeper.createTrial(opts);
        if (success) {
            this.log.info(`Created trial ${trialId} on worker ${worker.channelId}`);
            this.workersByTrial.set(trialId, worker);
            return trialId;
        }
        else {
            this.log.warning('Failed to create trial');
            return null;
        }
    }
    async stopTrial(trialId) {
        this.log.info('Stop trial', trialId);
        const worker = this.workersByTrial.get(trialId);
        await worker?.trialKeeper.stopTrial(trialId);
    }
    async sendParameter(trialId, parameter) {
        this.log.info('Trial parameter:', trialId, parameter);
        const worker = this.workersByTrial.get(trialId);
        if (!worker) {
            this.log.error(`Worker of trial ${trialId} is not working`);
            return;
        }
        const command = { type: 'parameter', parameter };
        await worker.trialKeeper.sendCommand(trialId, command);
    }
    onTrialStart(callback) {
        this.emitter.on('trial_start', callback);
    }
    onTrialEnd(callback) {
        this.emitter.on('trial_stop', callback);
    }
    onRequestParameter(callback) {
        this.emitter.on('request_parameter', callback);
    }
    onMetric(callback) {
        this.emitter.on('metric', callback);
    }
    onEnvironmentUpdate(callback) {
        this.emitter.on('env_update', callback);
    }
    emitEnvUpdate() {
        this.emitter.emit('env_update', this.workers.map(worker => worker.env));
    }
    async launchWorker(config) {
        this.lastWorkerIndex += 1;
        const channelId = String(this.lastWorkerIndex);
        const worker = new worker_1.Worker(this.id, channelId, config, this.server.getChannelUrl(channelId, this.config.nniManagerIp), Boolean(this.config.trialGpuNumber));
        this.workers.push(worker);
        this.workersByChannel.set(worker.channelId, worker);
        this.workersByEnv.set(worker.envId, worker);
        worker.trialKeeper.onTrialStart((trialId, timestamp) => {
            this.emitter.emit('trial_start', trialId, timestamp);
        });
        worker.trialKeeper.onTrialStop((trialId, timestamp, exitCode) => {
            this.emitter.emit('trial_stop', trialId, timestamp, exitCode);
        });
        worker.trialKeeper.onReceiveCommand('request_parameter', (trialId, _command) => {
            this.emitter.emit('request_parameter', trialId);
        });
        worker.trialKeeper.onReceiveCommand('metric', (trialId, command) => {
            this.emitter.emit('metric', trialId, command['metric']);
        });
        worker.trialKeeper.onEnvironmentUpdate(env => {
            worker.env = env;
            this.emitEnvUpdate();
        });
        await worker.start();
        return worker;
    }
    stopWorker(oldWorker, emitEnvUpdate) {
        this.workers = this.workers.filter(worker => (worker !== oldWorker));
        if (emitEnvUpdate) {
            this.emitEnvUpdate();
        }
        this.workersByChannel.delete(oldWorker.channelId);
        this.workersByEnv.delete(oldWorker.envId);
        const now = Date.now();
        this.workersByTrial.forEach((worker, trialId) => {
            if (worker === oldWorker) {
                this.emitter.emit('trial_stop', trialId, now, null);
                this.workersByTrial.delete(trialId);
            }
        });
    }
    async restartWorker(oldWorker) {
        this.stopWorker(oldWorker, true);
        try {
            const worker = await this.launchWorker(oldWorker.config);
            for (const dirName of this.uploadedDirs) {
                const tar = (0, tarball_1.getTarballPath)(dirName);
                await worker.upload(dirName, tar);
            }
        }
        catch (error) {
            this.log.error(`Failed to recover worker ${oldWorker.config.host}:`, error);
            return;
        }
        this.emitEnvUpdate();
        this.log.info(`Worker ${oldWorker.config.host} has been recovered`);
    }
    async downloadTrialDirectory(trialId) {
        const worker = this.workersByTrial.get(trialId);
        if (worker) {
            return await worker.downloadTrialLog(trialId);
        }
        else {
            this.log.error('Failed to download trial log: cannot find worker for trial', trialId);
            throw new Error(`The worker of trial ${trialId} is not working`);
        }
    }
}
exports.RemoteTrainingServiceV3 = RemoteTrainingServiceV3;
const utils_1 = require("common/utils");
function uuid() {
    return (0, utils_1.uniqueString)(5);
}
