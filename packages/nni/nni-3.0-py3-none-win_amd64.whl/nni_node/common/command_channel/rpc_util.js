"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RpcHelper = exports.getRpcHelper = void 0;
const node_util_1 = __importDefault(require("node:util"));
const default_map_1 = require("common/default_map");
const deferred_1 = require("common/deferred");
const log_1 = require("common/log");
const rpcHelpers = new Map();
function getRpcHelper(channel) {
    if (!rpcHelpers.has(channel)) {
        rpcHelpers.set(channel, new RpcHelper(channel));
    }
    return rpcHelpers.get(channel);
}
exports.getRpcHelper = getRpcHelper;
class RpcHelper {
    channel;
    lastId = 0;
    localCtors = new Map();
    localObjs = new Map();
    localCbs = new Map();
    log;
    responses = new default_map_1.DefaultMap(() => new deferred_1.Deferred());
    constructor(channel) {
        this.log = (0, log_1.getLogger)(`RpcHelper.${channel.name}`);
        this.channel = channel;
        this.channel.onCommand('rpc_constructor', command => {
            this.invokeLocalConstructor(command.id, command.className, command.parameters);
        });
        this.channel.onCommand('rpc_method', command => {
            this.invokeLocalMethod(command.id, command.objectId, command.methodName, command.parameters, command.callbackIds);
        });
        this.channel.onCommand('rpc_callback', command => {
            this.invokeLocalCallback(command.id, command.callbackId, command.parameters);
        });
        this.channel.onCommand('rpc_response', command => {
            this.responses.get(command.id).resolve(command);
        });
    }
    registerClass(className, constructor) {
        this.log.debug('Register class', className);
        this.localCtors.set(className, constructor);
    }
    construct(className, parameters) {
        return this.invokeRemoteConstructor(className, parameters ?? []);
    }
    call(objectId, methodName, parameters, callbacks) {
        return this.invokeRemoteMethod(objectId, methodName, parameters ?? [], callbacks ?? []);
    }
    async invokeRemoteConstructor(className, parameters) {
        this.log.debug('Send constructor command', className, parameters);
        const id = this.generateId();
        this.channel.send({ type: 'rpc_constructor', id, className, parameters });
        await this.waitResponse(id);
        return id;
    }
    invokeLocalConstructor(id, className, parameters) {
        this.log.debug('Receive constructor command', className, parameters);
        const ctor = this.localCtors.get(className);
        if (!ctor) {
            this.sendRpcError(id, `Unknown class name ${className}`);
            return;
        }
        let obj;
        try {
            obj = new ctor(...parameters);
        }
        catch (error) {
            this.log.debug('Constructor throws error', className, error);
            this.sendError(id, error);
            return;
        }
        this.localObjs.set(id, obj);
        this.sendResult(id, undefined);
    }
    async invokeRemoteMethod(objectId, methodName, parameters, callbacks) {
        this.log.debug('Send method command', methodName, parameters);
        const id = this.generateId();
        const callbackIds = this.generateCallbackIds(callbacks);
        this.channel.send({ type: 'rpc_method', id, objectId, methodName, parameters, callbackIds });
        return await this.waitResponse(id);
    }
    async invokeLocalMethod(id, objectId, methodName, parameters, callbackIds) {
        this.log.debug('Receive method command', methodName, parameters);
        const obj = this.localObjs.get(objectId);
        if (!obj) {
            this.sendRpcError(id, `Non-exist object ${objectId}`);
            return;
        }
        const callbacks = this.createCallbacks(callbackIds);
        let result;
        try {
            result = obj[methodName](...parameters, ...callbacks);
            if (typeof result === 'object' && result.then) {
                result = await result;
            }
        }
        catch (error) {
            this.log.debug('Command throws error', methodName, error);
            this.sendError(id, error);
            return;
        }
        this.log.debug('Command returns', result);
        this.sendResult(id, result);
    }
    invokeRemoteCallback(callbackId, parameters) {
        this.log.debug('Send callback command', parameters);
        const id = this.generateId();
        this.channel.send({ type: 'rpc_callback', id, callbackId, parameters });
    }
    invokeLocalCallback(_id, callbackId, parameters) {
        this.log.debug('Receive callback command', parameters);
        const cb = this.localCbs.get(callbackId);
        if (cb) {
            cb(...parameters);
        }
        else {
            this.log.error('Non-exist callback ID', callbackId);
        }
    }
    generateId() {
        this.lastId += 1;
        return this.lastId;
    }
    generateCallbackIds(callbacks) {
        const ids = [];
        for (const cb of callbacks) {
            const id = this.generateId();
            ids.push(id);
            this.localCbs.set(id, cb);
        }
        return ids;
    }
    createCallbacks(callbackIds) {
        return callbackIds.map(id => ((...args) => { this.invokeRemoteCallback(id, args); }));
    }
    sendResult(id, result) {
        try {
            JSON.stringify(result);
        }
        catch {
            this.sendRpcError(id, 'method returns non-JSON value ' + node_util_1.default.inspect(result));
            return;
        }
        this.channel.send({ type: 'rpc_response', id, result });
    }
    sendError(id, error) {
        const msg = error?.stack ? String(error.stack) : node_util_1.default.inspect(error);
        this.channel.send({ type: 'rpc_response', id, error: msg });
    }
    sendRpcError(id, message) {
        this.channel.send({ type: 'rpc_response', id, error: `RPC framework error: ${message}` });
    }
    async waitResponse(id) {
        const deferred = this.responses.get(id);
        const res = await deferred.promise;
        if (res.error) {
            throw new Error(`RPC remote error:\n${res.error}`);
        }
        return res.result;
    }
}
exports.RpcHelper = RpcHelper;
