"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.trainingServiceFactoryV3 = void 0;
const local_v3_1 = require("../local_v3");
const remote_v3_1 = require("../remote_v3");
function trainingServiceFactoryV3(config) {
    if (config.platform.startsWith('local')) {
        return new local_v3_1.LocalTrainingServiceV3('local', config);
    }
    else if (config.platform.startsWith('remote')) {
        return new remote_v3_1.RemoteTrainingServiceV3('remote', config);
    }
    else {
        throw new Error(`Bad training service platform: ${config.platform}`);
    }
}
exports.trainingServiceFactoryV3 = trainingServiceFactoryV3;
