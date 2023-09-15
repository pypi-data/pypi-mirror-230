"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.LocalTrainingServiceV3 = void 0;
const node_path_1 = __importDefault(require("node:path"));
const globals_1 = require("common/globals");
const log_1 = require("common/log");
const keeper_1 = require("common/trial_keeper/keeper");
class LocalTrainingServiceV3 {
    config;
    env;
    log;
    trialKeeper;
    constructor(trainingServiceId, config) {
        this.log = (0, log_1.getLogger)(`LocalV3.${trainingServiceId}`);
        this.log.debug('Training sevice config:', config);
        this.config = config;
        this.env = { id: `${trainingServiceId}-env` };
        this.trialKeeper = new keeper_1.TrialKeeper(this.env.id, 'local', Boolean(config.trialGpuNumber));
    }
    async init() {
        return;
    }
    async start() {
        this.log.info('Start');
        await this.trialKeeper.start();
        return [this.env];
    }
    async stop() {
        await this.trialKeeper.shutdown();
        this.log.info('All trials stopped');
    }
    async uploadDirectory(directoryName, path) {
        this.log.info(`Register directory ${directoryName} = ${path}`);
        this.trialKeeper.registerDirectory(directoryName, path);
    }
    async createTrial(_envId, trialCommand, directoryName, sequenceId, trialId) {
        trialId = trialId ?? uuid();
        let gpuNumber = this.config.trialGpuNumber;
        if (gpuNumber) {
            gpuNumber /= this.config.maxTrialNumberPerGpu;
        }
        const opts = {
            id: trialId,
            command: trialCommand,
            codeDirectoryName: directoryName,
            sequenceId,
            gpuNumber,
            gpuRestrictions: {
                onlyUseIndices: this.config.gpuIndices,
                rejectActive: !this.config.useActiveGpu,
            },
        };
        const success = await this.trialKeeper.createTrial(opts);
        if (success) {
            this.log.info('Created trial', trialId);
            return trialId;
        }
        else {
            this.log.warning('Failed to create trial');
            return null;
        }
    }
    async stopTrial(trialId) {
        this.log.info('Stop trial', trialId);
        await this.trialKeeper.stopTrial(trialId);
    }
    async sendParameter(trialId, parameter) {
        this.log.info('Trial parameter:', trialId, parameter);
        const command = { type: 'parameter', parameter };
        await this.trialKeeper.sendCommand(trialId, command);
    }
    onTrialStart(callback) {
        this.trialKeeper.onTrialStart(callback);
    }
    onTrialEnd(callback) {
        this.trialKeeper.onTrialStop(callback);
    }
    onRequestParameter(callback) {
        this.trialKeeper.onReceiveCommand('request_parameter', (trialId, _command) => {
            callback(trialId);
        });
    }
    onMetric(callback) {
        this.trialKeeper.onReceiveCommand('metric', (trialId, command) => {
            callback(trialId, command['metric']);
        });
    }
    onEnvironmentUpdate(_callback) {
    }
    async downloadTrialDirectory(trialId) {
        return node_path_1.default.join(globals_1.globals.paths.experimentRoot, 'environments', this.env.id, 'trials', trialId);
    }
}
exports.LocalTrainingServiceV3 = LocalTrainingServiceV3;
const utils_1 = require("common/utils");
function uuid() {
    return (0, utils_1.uniqueString)(5);
}
