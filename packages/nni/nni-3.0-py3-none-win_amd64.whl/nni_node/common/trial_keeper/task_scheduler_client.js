"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TaskSchedulerClient = void 0;
const globals_1 = __importDefault(require("common/globals"));
const log_1 = require("common/log");
const task_scheduler_1 = require("./task_scheduler");
const logger = (0, log_1.getLogger)('TaskSchedulerClient');
class TaskSchedulerClient {
    server = null;
    constructor(enable) {
        if (enable) {
            this.server = new task_scheduler_1.TaskScheduler();
        }
    }
    async start() {
        if (this.server !== null) {
            await this.server.init();
        }
    }
    async shutdown() {
        if (this.server !== null) {
            await this.server.releaseAll(globals_1.default.args.experimentId);
        }
    }
    async schedule(trialId, gpuNumber, restrictions) {
        if (gpuNumber === undefined) {
            return {};
        }
        if (gpuNumber === 0) {
            return { 'CUDA_VISIBLE_DEVICES': '' };
        }
        if (this.server === null) {
            logger.error(`GPU scheduling is not enabled, but gpuNumber of trial ${trialId} is ${gpuNumber}`);
            return null;
        }
        return this.server.schedule(globals_1.default.args.experimentId, trialId, gpuNumber, restrictions);
    }
    async release(trialId) {
        if (this.server !== null) {
            await this.server.release(globals_1.default.args.experimentId, trialId);
        }
    }
    onUtilityUpdate(callback) {
        if (this.server !== null) {
            this.server.onUtilityUpdate(callback);
        }
    }
}
exports.TaskSchedulerClient = TaskSchedulerClient;
