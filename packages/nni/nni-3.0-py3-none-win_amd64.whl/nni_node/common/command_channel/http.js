"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.UnitTestHelpers = exports.HttpChannelServer = void 0;
const events_1 = require("events");
const deferred_1 = require("common/deferred");
const globals_1 = __importDefault(require("common/globals"));
const log_1 = require("common/log");
let timeoutMilliseconds = 1000;
const HttpRequestTimeout = 408;
const HttpGone = 410;
class HttpChannelServer {
    emitter = new events_1.EventEmitter();
    log;
    outgoingQueues = new Map();
    path;
    serving = false;
    constructor(name, urlPath) {
        this.log = (0, log_1.getLogger)(`HttpChannelManager.${name}`);
        this.path = urlPath;
    }
    async start() {
        this.serving = true;
        const channelPath = globals_1.default.rest.urlJoin(this.path, ':channel');
        globals_1.default.rest.registerSyncHandler('GET', channelPath, this.handleGet.bind(this));
        globals_1.default.rest.registerSyncHandler('PUT', channelPath, this.handlePut.bind(this));
    }
    async shutdown() {
        this.serving = false;
        this.outgoingQueues.forEach(queue => { queue.clear(); });
    }
    getChannelUrl(channelId, ip) {
        return globals_1.default.rest.getFullUrl('http', ip ?? 'localhost', this.path, channelId);
    }
    send(channelId, command) {
        this.getOutgoingQueue(channelId).push(command);
    }
    onReceive(callback) {
        this.emitter.on('receive', callback);
    }
    onConnection(_callback) {
        throw new Error('Not implemented');
    }
    handleGet(request, response) {
        const channelId = request.params['channel'];
        const promise = this.getOutgoingQueue(channelId).asyncPop(timeoutMilliseconds);
        promise.then(command => {
            if (command === null) {
                response.sendStatus(this.serving ? HttpRequestTimeout : HttpGone);
            }
            else {
                response.send(command);
            }
        });
    }
    handlePut(request, response) {
        if (!this.serving) {
            response.sendStatus(HttpGone);
            return;
        }
        const channelId = request.params['channel'];
        const command = request.body;
        this.emitter.emit('receive', channelId, command);
        response.send();
    }
    getOutgoingQueue(channelId) {
        if (!this.outgoingQueues.has(channelId)) {
            this.outgoingQueues.set(channelId, new CommandQueue());
        }
        return this.outgoingQueues.get(channelId);
    }
}
exports.HttpChannelServer = HttpChannelServer;
class CommandQueue {
    commands = [];
    consumers = [];
    push(command) {
        const consumer = this.consumers.shift();
        if (consumer !== undefined) {
            consumer.resolve(command);
        }
        else {
            this.commands.push(command);
        }
    }
    asyncPop(timeout) {
        const command = this.commands.shift();
        if (command !== undefined) {
            return Promise.resolve(command);
        }
        else {
            const consumer = new deferred_1.Deferred();
            this.consumers.push(consumer);
            setTimeout(() => {
                if (!consumer.settled) {
                    this.consumers = this.consumers.filter(item => (item !== consumer));
                    consumer.resolve(null);
                }
            }, timeout);
            return consumer.promise;
        }
    }
    clear() {
        for (const consumer of this.consumers) {
            consumer.resolve(null);
        }
    }
}
var UnitTestHelpers;
(function (UnitTestHelpers) {
    function setTimeoutMilliseconds(ms) {
        timeoutMilliseconds = ms;
    }
    UnitTestHelpers.setTimeoutMilliseconds = setTimeoutMilliseconds;
})(UnitTestHelpers = exports.UnitTestHelpers || (exports.UnitTestHelpers = {}));
