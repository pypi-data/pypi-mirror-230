"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RemoteTrialKeeper = exports.registerTrialKeeperOnChannel = void 0;
const node_events_1 = require("node:events");
const rpc_util_1 = require("common/command_channel/rpc_util");
const deferred_1 = require("common/deferred");
const keeper_1 = require("./keeper");
function registerTrialKeeperOnChannel(channel) {
    (0, rpc_util_1.getRpcHelper)(channel).registerClass('TrialKeeper', keeper_1.TrialKeeper);
}
exports.registerTrialKeeperOnChannel = registerTrialKeeperOnChannel;
class RemoteTrialKeeper {
    args;
    emitter = new node_events_1.EventEmitter();
    id;
    initialized = new deferred_1.Deferred();
    rpc;
    constructor(environmentId, platform, enableGpuScheduling) {
        this.args = [environmentId, platform, enableGpuScheduling];
    }
    async setChannel(channel) {
        this.rpc = (0, rpc_util_1.getRpcHelper)(channel);
        this.id = await this.rpc.construct('TrialKeeper', this.args);
        await Promise.all([
            this.rpc.call(this.id, 'onTrialStart', undefined, [this.emitTrialStart.bind(this)]),
            this.rpc.call(this.id, 'onTrialStop', undefined, [this.emitTrialStop.bind(this)]),
            this.rpc.call(this.id, 'onReceiveCommand', undefined, [this.emitCommand.bind(this)]),
            this.rpc.call(this.id, 'onEnvironmentUpdate', undefined, [this.emitEnvUpdate.bind(this)]),
        ]);
        this.initialized.resolve();
    }
    async start() {
        await this.initialized.promise;
        return await this.rpc.call(this.id, 'start');
    }
    async shutdown() {
        await this.rpc.call(this.id, 'shutdown');
    }
    async registerDirectory(name, path) {
        await this.rpc.call(this.id, 'registerDirectory', [name, path.replaceAll('\\', '/')]);
    }
    async unpackDirectory(name, tarPath) {
        await this.rpc.call(this.id, 'unpackDirectory', [name, tarPath.replaceAll('\\', '/')]);
    }
    async createTrial(options) {
        return await this.rpc.call(this.id, 'createTrial', [options]);
    }
    async stopTrial(trialId) {
        await this.rpc.call(this.id, 'stopTrial', [trialId]);
    }
    async sendCommand(trialId, command) {
        await this.rpc.call(this.id, 'sendCommand', [trialId, command]);
    }
    onTrialStart(callback) {
        this.emitter.on('__trial_start', callback);
    }
    emitTrialStart(trialId, timestamp) {
        this.emitter.emit('__trial_start', trialId, timestamp);
    }
    onTrialStop(callback) {
        this.emitter.on('__trial_stop', callback);
    }
    emitTrialStop(trialId, timestamp, exitCode) {
        this.emitter.emit('__trial_stop', trialId, timestamp, exitCode);
    }
    onReceiveCommand(commandType, callback) {
        this.emitter.on(commandType, callback);
    }
    emitCommand(trialId, command) {
        this.emitter.emit(command.type, trialId, command);
    }
    onEnvironmentUpdate(callback) {
        this.emitter.on('__env_update', callback);
    }
    emitEnvUpdate(envInfo) {
        this.emitter.emit('__env_update', envInfo);
    }
}
exports.RemoteTrialKeeper = RemoteTrialKeeper;
