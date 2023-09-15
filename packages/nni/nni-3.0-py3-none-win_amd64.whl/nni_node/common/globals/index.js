"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.initGlobalsCustom = exports.initGlobals = exports.globals = void 0;
const strict_1 = __importDefault(require("assert/strict"));
const arguments_1 = require("./arguments");
const log_stream_1 = require("./log_stream");
const paths_1 = require("./paths");
const rest_1 = require("./rest");
const shutdown_1 = require("./shutdown");
if (global.nni === undefined) {
    global.nni = {};
}
exports.globals = global.nni;
exports.default = exports.globals;
function initGlobals() {
    strict_1.default.deepEqual(global.nni, {});
    const args = (0, arguments_1.parseArgs)(process.argv.slice(2));
    const paths = (0, paths_1.createPaths)(args);
    const logStream = (0, log_stream_1.initLogStream)(args, paths);
    const rest = new rest_1.RestManager();
    const shutdown = new shutdown_1.ShutdownManager();
    const globals = { args, paths, logStream, rest, shutdown };
    Object.assign(global.nni, globals);
}
exports.initGlobals = initGlobals;
function initGlobalsCustom(args, logPath) {
    strict_1.default.deepEqual(global.nni, {});
    const paths = (0, paths_1.createPaths)(args);
    const logStream = (0, log_stream_1.initLogStreamCustom)(args, logPath);
    const rest = new rest_1.RestManager();
    const shutdown = new shutdown_1.ShutdownManager();
    const globals = { args, paths, logStream, rest, shutdown };
    Object.assign(global.nni, globals);
}
exports.initGlobalsCustom = initGlobalsCustom;
