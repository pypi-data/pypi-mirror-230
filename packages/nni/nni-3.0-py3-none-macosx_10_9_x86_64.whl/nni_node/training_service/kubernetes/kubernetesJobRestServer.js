"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KubernetesJobRestServer = void 0;
const clusterJobRestServer_1 = require("../common/clusterJobRestServer");
class KubernetesJobRestServer extends clusterJobRestServer_1.ClusterJobRestServer {
    kubernetesTrainingService;
    constructor(kubernetesTrainingService) {
        super();
        this.kubernetesTrainingService = kubernetesTrainingService;
    }
    handleTrialMetrics(jobId, metrics) {
        if (this.kubernetesTrainingService === undefined) {
            throw Error('kubernetesTrainingService not initialized!');
        }
        for (const singleMetric of metrics) {
            this.kubernetesTrainingService.MetricsEmitter.emit('metric', {
                id: jobId,
                data: singleMetric
            });
        }
    }
}
exports.KubernetesJobRestServer = KubernetesJobRestServer;
