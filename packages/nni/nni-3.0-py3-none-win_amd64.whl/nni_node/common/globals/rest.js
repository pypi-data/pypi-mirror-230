"use strict";
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
exports.RestManager = void 0;
const express_1 = __importStar(require("express"));
const express_ws_1 = __importDefault(require("express-ws"));
class RestManager {
    app;
    router;
    constructor() {
        this.app = (0, express_1.default)();
        (0, express_ws_1.default)(this.app, undefined, { wsOptions: { maxPayload: 4 * 1024 * 1024 * 1024 } });
        this.router = (0, express_1.Router)();
        this.router.use(express_1.default.json({ limit: '50mb' }));
    }
    getExpressApp() {
        return this.app;
    }
    getExpressRouter() {
        return this.router;
    }
    registerSyncHandler(method, path, callback) {
        const p = '/' + trimSlash(path);
        if (method === 'GET') {
            this.router.get(p, callback);
        }
        else if (method === 'PUT') {
            this.router.put(p, callback);
        }
        else {
            throw new Error(`RestManager: Bad method ${method}`);
        }
    }
    registerWebSocketHandler(path, callback) {
        const p = '/' + trimSlash(path);
        this.router.ws(p, callback);
    }
    registerExpressRouter(path, router) {
        this.router.use(path, router);
    }
    urlJoin(...parts) {
        return parts.map(trimSlash).filter(part => part).join('/');
    }
    getFullUrl(protocol, ip, ...parts) {
        const root = `${protocol}://${ip}:${global.nni.args.port}/`;
        return root + this.urlJoin(global.nni.args.urlPrefix, ...parts);
    }
}
exports.RestManager = RestManager;
function trimSlash(s) {
    return s.replace(/^\/+|\/+$/g, '');
}
