"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AMLEnvironmentService = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const ioc_shim_1 = require("common/ioc_shim");
const log_1 = require("common/log");
const util_1 = require("training_service/common/util");
const amlClient_1 = require("../aml/amlClient");
const amlConfig_1 = require("../aml/amlConfig");
const environment_1 = require("../environment");
const amlCommandChannel_1 = require("../channels/amlCommandChannel");
const sharedStorage_1 = require("../sharedStorage");
class AMLEnvironmentService extends environment_1.EnvironmentService {
    log = (0, log_1.getLogger)('AMLEnvironmentService');
    experimentId;
    experimentRootDir;
    config;
    constructor(config, info) {
        super();
        this.experimentId = info.experimentId;
        this.experimentRootDir = info.logDir;
        this.config = config;
        (0, util_1.validateCodeDir)(this.config.trialCodeDirectory);
    }
    get hasStorageService() {
        return false;
    }
    initCommandChannel(eventEmitter) {
        this.commandChannel = new amlCommandChannel_1.AMLCommandChannel(eventEmitter);
    }
    createEnvironmentInformation(envId, envName) {
        return new amlConfig_1.AMLEnvironmentInformation(envId, envName);
    }
    get getName() {
        return 'aml';
    }
    async refreshEnvironmentsStatus(environments) {
        environments.forEach(async (environment) => {
            const amlClient = environment.amlClient;
            if (!amlClient) {
                return Promise.reject('AML client not initialized!');
            }
            const newStatus = await amlClient.updateStatus(environment.status);
            switch (newStatus.toUpperCase()) {
                case 'WAITING':
                case 'QUEUED':
                    environment.setStatus('WAITING');
                    break;
                case 'RUNNING':
                    environment.setStatus('RUNNING');
                    break;
                case 'COMPLETED':
                case 'SUCCEEDED':
                    environment.setStatus('SUCCEEDED');
                    break;
                case 'FAILED':
                    environment.setStatus('FAILED');
                    return Promise.reject(`AML: job ${environment.envId} is failed!`);
                case 'STOPPED':
                case 'STOPPING':
                    environment.setStatus('USER_CANCELED');
                    break;
                default:
                    environment.setStatus('UNKNOWN');
            }
        });
    }
    async startEnvironment(environment) {
        const amlEnvironment = environment;
        const environmentLocalTempFolder = path_1.default.join(this.experimentRootDir, "environment-temp");
        if (!fs_1.default.existsSync(environmentLocalTempFolder)) {
            await fs_1.default.promises.mkdir(environmentLocalTempFolder, { recursive: true });
        }
        if (amlEnvironment.useSharedStorage) {
            const environmentRoot = ioc_shim_1.IocShim.get(sharedStorage_1.SharedStorageService).remoteWorkingRoot;
            const remoteMountCommand = ioc_shim_1.IocShim.get(sharedStorage_1.SharedStorageService).remoteMountCommand;
            amlEnvironment.command = `${remoteMountCommand} && cd ${environmentRoot} && ${amlEnvironment.command}`.replace(/"/g, `\\"`);
        }
        else {
            amlEnvironment.command = `mv envs outputs/envs && cd outputs && ${amlEnvironment.command}`;
        }
        amlEnvironment.command = `import os\nos.system('${amlEnvironment.command}')`;
        amlEnvironment.maxTrialNumberPerGpu = this.config.maxTrialNumberPerGpu;
        await fs_1.default.promises.writeFile(path_1.default.join(environmentLocalTempFolder, 'nni_script.py'), amlEnvironment.command, { encoding: 'utf8' });
        const amlClient = new amlClient_1.AMLClient(this.config.subscriptionId, this.config.resourceGroup, this.config.workspaceName, this.experimentId, this.config.computeTarget, this.config.dockerImage, 'nni_script.py', environmentLocalTempFolder);
        this.log.debug('aml: before amlClient submit');
        amlEnvironment.id = await amlClient.submit();
        this.log.debug('aml: before getTrackingUrl');
        amlEnvironment.trackingUrl = await amlClient.getTrackingUrl();
        this.log.debug('aml: after getTrackingUrl');
        amlEnvironment.amlClient = amlClient;
    }
    async stopEnvironment(environment) {
        const amlEnvironment = environment;
        const amlClient = amlEnvironment.amlClient;
        if (!amlClient) {
            throw new Error('AML client not initialized!');
        }
        const result = await amlClient.stop();
        if (result) {
            this.log.info(`Stop aml run ${environment.id} success!`);
        }
        else {
            this.log.info(`Stop aml run ${environment.id} failed!`);
        }
    }
}
exports.AMLEnvironmentService = AMLEnvironmentService;
