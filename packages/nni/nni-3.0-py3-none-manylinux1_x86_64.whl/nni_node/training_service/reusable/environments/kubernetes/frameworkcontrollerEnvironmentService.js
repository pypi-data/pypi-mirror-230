'use strict';
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.FrameworkControllerEnvironmentService = void 0;
const child_process_promise_1 = __importDefault(require("child-process-promise"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const experimentConfig_1 = require("../../../../common/experimentConfig");
const kubernetesEnvironmentService_1 = require("./kubernetesEnvironmentService");
const frameworkcontrollerApiClient_1 = require("../../../kubernetes/frameworkcontroller/frameworkcontrollerApiClient");
class FrameworkControllerEnvironmentService extends kubernetesEnvironmentService_1.KubernetesEnvironmentService {
    config;
    createStoragePromise;
    fcContainerPortMap = new Map();
    constructor(config, info) {
        super(config, info);
        this.experimentId = info.experimentId;
        this.config = config;
        this.kubernetesCRDClient = frameworkcontrollerApiClient_1.FrameworkControllerClientFactory.createClient(this.config.namespace);
        this.genericK8sClient.setNamespace = this.config.namespace ?? "default";
        if (this.config.storage.storageType === 'azureStorage') {
            if (this.config.storage.azureShare === undefined ||
                this.config.storage.azureAccount === undefined ||
                this.config.storage.keyVaultName === undefined ||
                this.config.storage.keyVaultKey === undefined) {
                throw new Error("Azure storage configuration error!");
            }
            this.azureStorageAccountName = this.config.storage.azureAccount;
            this.azureStorageShare = this.config.storage.azureShare;
            this.createStoragePromise = this.createAzureStorage(this.config.storage.keyVaultName, this.config.storage.keyVaultKey);
        }
        else if (this.config.storage.storageType === 'nfs') {
            if (this.config.storage.server === undefined ||
                this.config.storage.path === undefined) {
                throw new Error("NFS storage configuration error!");
            }
            this.createStoragePromise = this.createNFSStorage(this.config.storage.server, this.config.storage.path);
        }
    }
    get environmentMaintenceLoopInterval() {
        return 5000;
    }
    get hasStorageService() {
        return false;
    }
    get getName() {
        return 'frameworkcontroller';
    }
    async startEnvironment(environment) {
        if (this.kubernetesCRDClient === undefined) {
            throw new Error("kubernetesCRDClient not initialized!");
        }
        if (this.createStoragePromise) {
            await this.createStoragePromise;
        }
        let configTaskRoles = undefined;
        configTaskRoles = this.config.taskRoles;
        this.generateContainerPort(configTaskRoles);
        const expFolder = `${this.CONTAINER_MOUNT_PATH}/nni/${this.experimentId}`;
        environment.command = `cd ${expFolder} && ${environment.command} \
1>${expFolder}/envs/${environment.id}/trialrunner_stdout 2>${expFolder}/envs/${environment.id}/trialrunner_stderr`;
        environment.maxTrialNumberPerGpu = this.config.maxTrialNumberPerGpu;
        const frameworkcontrollerJobName = `nniexp${this.experimentId}env${environment.id}`.toLowerCase();
        const command = this.generateCommandScript(this.config.taskRoles, environment.command);
        await fs.promises.writeFile(path.join(this.environmentLocalTempFolder, `${environment.id}_run.sh`), command, { encoding: 'utf8' });
        const trialJobOutputUrl = await this.uploadFolder(this.environmentLocalTempFolder, `nni/${this.experimentId}`);
        environment.trackingUrl = trialJobOutputUrl;
        const frameworkcontrollerJobConfig = await this.prepareFrameworkControllerConfig(environment.id, this.environmentWorkingFolder, frameworkcontrollerJobName);
        await this.kubernetesCRDClient.createKubernetesJob(frameworkcontrollerJobConfig);
    }
    async uploadFolder(srcDirectory, destDirectory) {
        if (this.config.storage.storageType === 'azureStorage') {
            if (this.azureStorageClient === undefined) {
                throw new Error('azureStorageClient is not initialized');
            }
            return await this.uploadFolderToAzureStorage(srcDirectory, destDirectory, 2);
        }
        else {
            try {
                await child_process_promise_1.default.exec(`mkdir -p ${this.nfsRootDir}/${destDirectory}`);
                await child_process_promise_1.default.exec(`cp -r ${srcDirectory}/* ${this.nfsRootDir}/${destDirectory}`);
            }
            catch (uploadError) {
                return Promise.reject(uploadError);
            }
            return `nfs://${this.config.storage.server}:${destDirectory}`;
        }
    }
    generateCommandScript(taskRoles, command) {
        let portScript = '';
        for (const taskRole of taskRoles) {
            portScript += `FB_${taskRole.name.toUpperCase()}_PORT=${this.fcContainerPortMap.get(taskRole.name)} `;
        }
        return `${portScript} . /mnt/frameworkbarrier/injector.sh && ${command}`;
    }
    async prepareFrameworkControllerConfig(envId, trialWorkingFolder, frameworkcontrollerJobName) {
        const podResources = [];
        for (const taskRole of this.config.taskRoles) {
            const resource = {};
            resource.requests = this.generatePodResource((0, experimentConfig_1.toMegaBytes)(taskRole.memorySize), taskRole.cpuNumber, taskRole.gpuNumber);
            resource.limits = { ...resource.requests };
            podResources.push(resource);
        }
        const frameworkcontrollerJobConfig = await this.generateFrameworkControllerJobConfig(envId, trialWorkingFolder, frameworkcontrollerJobName, podResources);
        return Promise.resolve(frameworkcontrollerJobConfig);
    }
    generateContainerPort(taskRoles) {
        if (taskRoles === undefined) {
            throw new Error('frameworkcontroller trial config is not initialized');
        }
        let port = 4000;
        for (const index of taskRoles.keys()) {
            this.fcContainerPortMap.set(taskRoles[index].name, port);
            port += 1;
        }
    }
    async generateFrameworkControllerJobConfig(envId, trialWorkingFolder, frameworkcontrollerJobName, podResources) {
        const taskRoles = [];
        for (const index of this.config.taskRoles.keys()) {
            const containerPort = this.fcContainerPortMap.get(this.config.taskRoles[index].name);
            if (containerPort === undefined) {
                throw new Error('Container port is not initialized');
            }
            const taskRole = this.generateTaskRoleConfig(trialWorkingFolder, this.config.taskRoles[index].dockerImage, `${envId}_run.sh`, podResources[index], containerPort, await this.createRegistrySecret(this.config.taskRoles[index].privateRegistryAuthPath));
            taskRoles.push({
                name: this.config.taskRoles[index].name,
                taskNumber: this.config.taskRoles[index].taskNumber,
                frameworkAttemptCompletionPolicy: {
                    minFailedTaskCount: this.config.taskRoles[index].frameworkAttemptCompletionPolicy.minFailedTaskCount,
                    minSucceededTaskCount: this.config.taskRoles[index].frameworkAttemptCompletionPolicy.minSucceedTaskCount
                },
                task: taskRole
            });
        }
        return Promise.resolve({
            apiVersion: `frameworkcontroller.microsoft.com/v1`,
            kind: 'Framework',
            metadata: {
                name: frameworkcontrollerJobName,
                namespace: this.config.namespace ?? "default",
                labels: {
                    app: this.NNI_KUBERNETES_TRIAL_LABEL,
                    expId: this.experimentId,
                    envId: envId
                }
            },
            spec: {
                executionType: 'Start',
                taskRoles: taskRoles
            }
        });
    }
    generateTaskRoleConfig(trialWorkingFolder, replicaImage, runScriptFile, podResources, containerPort, privateRegistrySecretName) {
        const volumeSpecMap = new Map();
        if (this.config.storage.storageType === 'azureStorage') {
            volumeSpecMap.set('nniVolumes', [
                {
                    name: 'nni-vol',
                    azureFile: {
                        secretName: `${this.azureStorageSecretName}`,
                        shareName: `${this.azureStorageShare}`,
                        readonly: false
                    }
                }, {
                    name: 'frameworkbarrier-volume',
                    emptyDir: {}
                }
            ]);
        }
        else {
            volumeSpecMap.set('nniVolumes', [
                {
                    name: 'nni-vol',
                    nfs: {
                        server: `${this.config.storage.server}`,
                        path: `${this.config.storage.path}`
                    }
                }, {
                    name: 'frameworkbarrier-volume',
                    emptyDir: {}
                }
            ]);
        }
        const containers = [
            {
                name: 'framework',
                image: replicaImage,
                command: ['sh', `${path.join(trialWorkingFolder, runScriptFile)}`],
                volumeMounts: [
                    {
                        name: 'nni-vol',
                        mountPath: this.CONTAINER_MOUNT_PATH
                    }, {
                        name: 'frameworkbarrier-volume',
                        mountPath: '/mnt/frameworkbarrier'
                    }
                ],
                resources: podResources,
                ports: [{
                        containerPort: containerPort
                    }]
            }
        ];
        const initContainers = [
            {
                name: 'frameworkbarrier',
                image: 'frameworkcontroller/frameworkbarrier',
                volumeMounts: [
                    {
                        name: 'frameworkbarrier-volume',
                        mountPath: '/mnt/frameworkbarrier'
                    }
                ]
            }
        ];
        const spec = {
            containers: containers,
            initContainers: initContainers,
            restartPolicy: 'OnFailure',
            volumes: volumeSpecMap.get('nniVolumes'),
            hostNetwork: false
        };
        if (privateRegistrySecretName) {
            spec.imagePullSecrets = [
                {
                    name: privateRegistrySecretName
                }
            ];
        }
        if (this.config.serviceAccountName !== undefined) {
            spec.serviceAccountName = this.config.serviceAccountName;
        }
        return {
            pod: {
                spec: spec
            }
        };
    }
    async refreshEnvironmentsStatus(environments) {
        environments.forEach(async (environment) => {
            if (this.kubernetesCRDClient === undefined) {
                throw new Error("kubernetesCRDClient undefined");
            }
            const kubeflowJobName = `nniexp${this.experimentId}env${environment.id}`.toLowerCase();
            const kubernetesJobInfo = await this.kubernetesCRDClient.getKubernetesJob(kubeflowJobName);
            if (kubernetesJobInfo.status && kubernetesJobInfo.status.state) {
                const frameworkJobType = kubernetesJobInfo.status.state;
                switch (frameworkJobType) {
                    case 'AttemptCreationPending':
                    case 'AttemptCreationRequested':
                    case 'AttemptPreparing':
                        environment.setStatus('WAITING');
                        break;
                    case 'AttemptRunning':
                        environment.setStatus('RUNNING');
                        break;
                    case 'Completed': {
                        const completedJobType = kubernetesJobInfo.status.attemptStatus.completionStatus.type.name;
                        switch (completedJobType) {
                            case 'Succeeded':
                                environment.setStatus('SUCCEEDED');
                                break;
                            case 'Failed':
                                environment.setStatus('FAILED');
                                break;
                            default:
                        }
                        break;
                    }
                    default:
                }
            }
        });
    }
}
exports.FrameworkControllerEnvironmentService = FrameworkControllerEnvironmentService;
