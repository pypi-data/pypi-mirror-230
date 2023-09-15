"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KubeflowEnvironmentService = void 0;
const child_process_promise_1 = __importDefault(require("child-process-promise"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const experimentConfig_1 = require("common/experimentConfig");
const kubernetesEnvironmentService_1 = require("./kubernetesEnvironmentService");
const kubeflowApiClient_1 = require("training_service/kubernetes/kubeflow/kubeflowApiClient");
const kubeflowConfig_1 = require("training_service/kubernetes/kubeflow/kubeflowConfig");
const kubernetesConfig_1 = require("training_service/kubernetes/kubernetesConfig");
class KubeflowEnvironmentService extends kubernetesEnvironmentService_1.KubernetesEnvironmentService {
    config;
    createStoragePromise;
    constructor(config, info) {
        super(config, info);
        this.experimentId = info.experimentId;
        this.config = config;
        this.kubernetesCRDClient = kubeflowApiClient_1.KubeflowOperatorClientFactory.createClient(this.config.operator, this.config.apiVersion);
        this.kubernetesCRDClient.namespace = this.config.namespace ?? "default";
        if (this.config.storage.storageType === 'azureStorage') {
            if (this.config.storage.azureShare === undefined ||
                this.config.storage.azureAccount === undefined ||
                this.config.storage.keyVaultName === undefined ||
                this.config.storage.keyVaultKey === undefined) {
                throw new Error("Azure storage configuration error!");
            }
            const azureStorage = new kubernetesConfig_1.AzureStorage(this.config.storage.azureShare, this.config.storage.azureAccount);
            const keyValutConfig = new kubernetesConfig_1.KeyVaultConfig(this.config.storage.keyVaultName, this.config.storage.keyVaultKey);
            const azureKubeflowClusterConfig = new kubeflowConfig_1.KubeflowClusterConfigAzure(this.config.operator, this.config.apiVersion, keyValutConfig, azureStorage);
            this.azureStorageAccountName = azureKubeflowClusterConfig.azureStorage.accountName;
            this.azureStorageShare = azureKubeflowClusterConfig.azureStorage.azureShare;
            this.genericK8sClient.setNamespace = this.config.namespace ?? "default";
            this.createStoragePromise = this.createAzureStorage(azureKubeflowClusterConfig.keyVault.vaultName, azureKubeflowClusterConfig.keyVault.name);
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
        return 'kubeflow';
    }
    async startEnvironment(environment) {
        if (this.kubernetesCRDClient === undefined) {
            throw new Error("kubernetesCRDClient not initialized!");
        }
        if (this.createStoragePromise) {
            await this.createStoragePromise;
        }
        const expFolder = `${this.CONTAINER_MOUNT_PATH}/nni/${this.experimentId}`;
        environment.command = `cd ${expFolder} && ${environment.command} \
1>${expFolder}/envs/${environment.id}/trialrunner_stdout 2>${expFolder}/envs/${environment.id}/trialrunner_stderr`;
        environment.maxTrialNumberPerGpu = this.config.maxTrialNumberPerGpu;
        const kubeflowJobName = `nniexp${this.experimentId}env${environment.id}`.toLowerCase();
        await fs_1.default.promises.writeFile(path_1.default.join(this.environmentLocalTempFolder, `${environment.id}_run.sh`), environment.command, { encoding: 'utf8' });
        const trialJobOutputUrl = await this.uploadFolder(this.environmentLocalTempFolder, `nni/${this.experimentId}`);
        environment.trackingUrl = trialJobOutputUrl;
        const kubeflowJobConfig = await this.prepareKubeflowConfig(environment.id, kubeflowJobName);
        await this.kubernetesCRDClient.createKubernetesJob(kubeflowJobConfig);
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
    async prepareKubeflowConfig(envId, kubeflowJobName) {
        const workerPodResources = {};
        if (this.config.worker !== undefined) {
            workerPodResources.requests = this.generatePodResource((0, experimentConfig_1.toMegaBytes)(this.config.worker.memorySize), this.config.worker.cpuNumber, this.config.worker.gpuNumber);
        }
        workerPodResources.limits = { ...workerPodResources.requests };
        const nonWorkerResources = {};
        if (this.config.operator === 'tf-operator') {
            if (this.config.ps !== undefined) {
                nonWorkerResources.requests = this.generatePodResource((0, experimentConfig_1.toMegaBytes)(this.config.ps.memorySize), this.config.ps.cpuNumber, this.config.ps.gpuNumber);
                nonWorkerResources.limits = { ...nonWorkerResources.requests };
            }
        }
        else if (this.config.operator === 'pytorch-operator') {
            if (this.config.master !== undefined) {
                nonWorkerResources.requests = this.generatePodResource((0, experimentConfig_1.toMegaBytes)(this.config.master.memorySize), this.config.master.cpuNumber, this.config.master.gpuNumber);
                nonWorkerResources.limits = { ...nonWorkerResources.requests };
            }
        }
        const kubeflowJobConfig = await this.generateKubeflowJobConfig(envId, kubeflowJobName, workerPodResources, nonWorkerResources);
        return Promise.resolve(kubeflowJobConfig);
    }
    async generateKubeflowJobConfig(envId, kubeflowJobName, workerPodResources, nonWorkerPodResources) {
        if (this.kubernetesCRDClient === undefined) {
            throw new Error('Kubeflow operator client is not initialized');
        }
        const replicaSpecsObj = {};
        const replicaSpecsObjMap = new Map();
        if (this.config.operator === 'tf-operator') {
            if (this.config.worker) {
                const privateRegistrySecretName = await this.createRegistrySecret(this.config.worker.privateRegistryAuthPath);
                replicaSpecsObj.Worker = this.generateReplicaConfig(this.config.worker.replicas, this.config.worker.dockerImage, `${envId}_run.sh`, workerPodResources, privateRegistrySecretName);
            }
            if (this.config.ps !== undefined) {
                const privateRegistrySecretName = await this.createRegistrySecret(this.config.ps.privateRegistryAuthPath);
                replicaSpecsObj.Ps = this.generateReplicaConfig(this.config.ps.replicas, this.config.ps.dockerImage, `${envId}_run.sh`, nonWorkerPodResources, privateRegistrySecretName);
            }
            replicaSpecsObjMap.set(this.kubernetesCRDClient.jobKind, { tfReplicaSpecs: replicaSpecsObj });
        }
        else if (this.config.operator === 'pytorch-operator') {
            if (this.config.worker !== undefined) {
                const privateRegistrySecretName = await this.createRegistrySecret(this.config.worker.privateRegistryAuthPath);
                replicaSpecsObj.Worker = this.generateReplicaConfig(this.config.worker.replicas, this.config.worker.dockerImage, `${envId}_run.sh`, workerPodResources, privateRegistrySecretName);
            }
            if (this.config.master !== undefined) {
                const privateRegistrySecretName = await this.createRegistrySecret(this.config.master.privateRegistryAuthPath);
                replicaSpecsObj.Master = this.generateReplicaConfig(this.config.master.replicas, this.config.master.dockerImage, `${envId}_run.sh`, nonWorkerPodResources, privateRegistrySecretName);
            }
            replicaSpecsObjMap.set(this.kubernetesCRDClient.jobKind, { pytorchReplicaSpecs: replicaSpecsObj });
        }
        return Promise.resolve({
            apiVersion: `kubeflow.org/${this.kubernetesCRDClient.apiVersion}`,
            kind: this.kubernetesCRDClient.jobKind,
            metadata: {
                name: kubeflowJobName,
                namespace: this.kubernetesCRDClient.namespace,
                labels: {
                    app: this.NNI_KUBERNETES_TRIAL_LABEL,
                    expId: this.experimentId,
                    envId: envId
                }
            },
            spec: replicaSpecsObjMap.get(this.kubernetesCRDClient.jobKind)
        });
    }
    generateReplicaConfig(replicaNumber, replicaImage, runScriptFile, podResources, privateRegistrySecretName) {
        if (this.kubernetesCRDClient === undefined) {
            throw new Error('Kubeflow operator client is not initialized');
        }
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
                }
            ]);
        }
        const containersSpecMap = new Map();
        containersSpecMap.set('containers', [
            {
                name: this.kubernetesCRDClient.containerName,
                image: replicaImage,
                args: ['sh', `${path_1.default.join(this.environmentWorkingFolder, runScriptFile)}`],
                volumeMounts: [
                    {
                        name: 'nni-vol',
                        mountPath: this.CONTAINER_MOUNT_PATH
                    }
                ],
                resources: podResources
            }
        ]);
        const spec = {
            containers: containersSpecMap.get('containers'),
            restartPolicy: 'ExitCode',
            volumes: volumeSpecMap.get('nniVolumes')
        };
        if (privateRegistrySecretName) {
            spec.imagePullSecrets = [
                {
                    name: privateRegistrySecretName
                }
            ];
        }
        return {
            replicas: replicaNumber,
            template: {
                metadata: {
                    creationTimestamp: null
                },
                spec: spec
            }
        };
    }
}
exports.KubeflowEnvironmentService = KubeflowEnvironmentService;
