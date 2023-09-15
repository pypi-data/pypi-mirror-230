"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.V3asV1 = void 0;
const events_1 = require("events");
const promises_1 = require("fs/promises");
const path_1 = __importDefault(require("path"));
const promises_2 = require("timers/promises");
const deferred_1 = require("common/deferred");
const globals_1 = __importDefault(require("common/globals"));
const log_1 = require("common/log");
const factory_1 = require("./factory");
const logger = (0, log_1.getLogger)('TrainingServiceCompat');
const placeholderDetail = {
    id: '',
    status: 'UNKNOWN',
    submitTime: 0,
    workingDirectory: '_unset_',
    form: {
        sequenceId: -1,
        hyperParameters: {
            value: 'null',
            index: -1,
        }
    }
};
class V3asV1 {
    config;
    v3;
    emitter = new events_1.EventEmitter();
    runDeferred = new deferred_1.Deferred();
    startDeferred = new deferred_1.Deferred();
    trialJobs = {};
    parameters = [];
    allocatedParameters = new Map();
    environments = [];
    lastEnvId = '';
    constructor(config) {
        this.config = config;
        this.v3 = (0, factory_1.trainingServiceFactoryV3)(config);
    }
    async listTrialJobs() {
        return Object.values(this.trialJobs);
    }
    async getTrialJob(trialJobId) {
        return this.trialJobs[trialJobId];
    }
    addTrialJobMetricListener(listener) {
        this.emitter.addListener('metric', listener);
    }
    removeTrialJobMetricListener(listener) {
        this.emitter.removeListener('metric', listener);
    }
    async submitTrialJob(form) {
        await this.startDeferred.promise;
        logger.trace('submitTrialJob', form);
        let trialId = null;
        let envId = null;
        let submitTime = 0;
        if (form.id && form.envId) {
            submitTime = Date.now();
            try {
                trialId = await this.v3.createTrial(form.envId, this.config.trialCommand, 'trial_code', form.sequenceId, form.id);
                if (trialId) {
                    envId = form.envId;
                    logger.debug(`Resumed trial ${trialId} in environment ${envId}`);
                }
                else {
                    logger.warning(`Failed to resume trial ${form.id} in environment ${form.envId}`);
                }
            }
            catch (error) {
                logger.error('Exception when resuming trial', form, ':', error);
            }
        }
        if (trialId === null) {
            this.parameters.push(form.hyperParameters.value);
        }
        else {
            this.allocatedParameters.set(trialId, form.hyperParameters.value);
        }
        while (trialId === null) {
            envId = this.schedule();
            if (envId === null) {
                await (0, promises_2.setTimeout)(1000);
                continue;
            }
            submitTime = Date.now();
            try {
                trialId = await this.v3.createTrial(envId, this.config.trialCommand, 'trial_code', form.sequenceId);
            }
            catch (error) {
                logger.error('Exception when create trial', form, ':', error);
            }
        }
        let trial;
        if (this.trialJobs[trialId] === undefined) {
            trial = {
                id: trialId,
                status: 'WAITING',
                submitTime,
                workingDirectory: '_unset_',
                form: form,
                envId: envId,
            };
        }
        else {
            trial = this.trialJobs[trialId];
            trial.submitTime = submitTime;
            trial.form = form;
            trial.envId = envId;
        }
        const env = this.environments.filter(env => (env.id === trial.envId))[0];
        if (env && env['host']) {
            const envDir = `~/nni-experiments/${globals_1.default.args.experimentId}/environments/${env.id}`;
            trial.url = `${env['host']}:${envDir}/trials/${trial.id}`;
        }
        else {
            trial.url = path_1.default.join(globals_1.default.paths.experimentRoot, 'environments', env.id, 'trials', trialId);
        }
        this.trialJobs[trialId] = trial;
        return trial;
    }
    async updateTrialJob(_trialJobId, _form) {
        throw new Error('Not implemented: V3asV1.updateTrialJob()');
    }
    async cancelTrialJob(trialJobId, isEarlyStopped) {
        try {
            await this.v3.stopTrial(trialJobId);
        }
        catch (error) {
            logger.error('Exception when cancel trial', trialJobId, ':', error);
        }
        this.trialJobs[trialJobId].isEarlyStopped = Boolean(isEarlyStopped);
    }
    async getTrialFile(trialJobId, fileName) {
        let dir;
        try {
            dir = await this.v3.downloadTrialDirectory(trialJobId);
        }
        catch (error) {
            logger.error('Exception when get trial file', trialJobId, fileName, ':', error);
            return `NNI internal error. Please check log file.\n${error}`;
        }
        let logPath = null;
        if (fileName === 'trial.log') {
            logPath = path_1.default.join(dir, 'trial.log');
        }
        else if (fileName === 'stderr') {
            logPath = path_1.default.join(dir, 'trial.stderr');
        }
        else if (fileName === 'stdout') {
            logPath = path_1.default.join(dir, 'trial.stdout');
        }
        if (logPath !== null) {
            return await (0, promises_1.readFile)(logPath, { encoding: 'utf8' });
        }
        else {
            return await (0, promises_1.readFile)(path_1.default.join(dir, fileName));
        }
    }
    async setClusterMetadata(_key, _value) {
        throw new Error('Not implemented: V3asV1.setClusterMetadata()');
    }
    async getClusterMetadata(_key) {
        throw new Error('Not implemented: V3asV1.getClusterMetadata()');
    }
    async getTrialOutputLocalPath(trialJobId) {
        return path_1.default.join(globals_1.default.paths.experimentRoot, 'trials', trialJobId, 'output');
    }
    async fetchTrialOutput(_trialJobId, _subpath) {
    }
    async cleanUp() {
        try {
            await this.v3.stop();
        }
        catch (error) {
            logger.error('Exception when stop:', error);
        }
        this.runDeferred.resolve();
    }
    run() {
        this.start().catch(error => {
            logger.error('Training srevice initialize failed:', error);
            globals_1.default.shutdown.initiate('training service initialize failed');
        });
        return this.runDeferred.promise;
    }
    async start() {
        await this.v3.init();
        this.v3.onRequestParameter(async (trialId) => {
            if (this.allocatedParameters.has(trialId)) {
                await this.v3.sendParameter(trialId, this.allocatedParameters.get(trialId));
                this.allocatedParameters.delete(trialId);
            }
            else if (this.parameters.length > 0) {
                await this.v3.sendParameter(trialId, this.parameters.shift());
            }
            else {
                logger.error('No parameters available');
            }
        });
        this.v3.onMetric(async (trialId, metric) => {
            this.emitter.emit('metric', { id: trialId, data: metric });
        });
        this.v3.onTrialStart(async (trialId, timestamp) => {
            if (this.trialJobs[trialId] === undefined) {
                this.trialJobs[trialId] = structuredClone(placeholderDetail);
                this.trialJobs[trialId].id = trialId;
            }
            this.trialJobs[trialId].status = 'RUNNING';
            this.trialJobs[trialId].startTime = timestamp;
        });
        this.v3.onTrialEnd(async (trialId, timestamp, exitCode) => {
            const trial = this.trialJobs[trialId];
            if (exitCode === 0) {
                trial.status = 'SUCCEEDED';
            }
            else if (exitCode !== null) {
                trial.status = 'FAILED';
            }
            else if (trial.isEarlyStopped) {
                trial.status = 'EARLY_STOPPED';
            }
            else {
                trial.status = 'USER_CANCELED';
            }
            trial.endTime = timestamp;
        });
        this.v3.onEnvironmentUpdate(async (environments) => {
            this.environments = environments;
        });
        this.environments = await this.v3.start();
        await this.v3.uploadDirectory('trial_code', this.config.trialCodeDirectory);
        this.startDeferred.resolve();
    }
    schedule() {
        if (this.environments.length === 0) {
            return null;
        }
        const prevIndex = this.environments.findIndex((env) => env.id === this.lastEnvId);
        const index = (prevIndex + 1) % this.environments.length;
        this.lastEnvId = this.environments[index].id;
        return this.lastEnvId;
    }
}
exports.V3asV1 = V3asV1;
