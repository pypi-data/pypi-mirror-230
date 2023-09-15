"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.globals = exports.resetGlobals = void 0;
const os_1 = __importDefault(require("os"));
const path_1 = __importDefault(require("path"));
const paths_1 = require("./paths");
const rest_1 = require("./rest");
require("./shutdown");
function resetGlobals() {
    const args = {
        port: 8080,
        experimentId: 'unittest',
        action: 'create',
        experimentsDirectory: path_1.default.join(os_1.default.homedir(), 'nni-experiments'),
        logLevel: 'info',
        foreground: false,
        urlPrefix: '',
        tunerCommandChannel: null,
        pythonInterpreter: 'python',
        mode: 'unittest'
    };
    const paths = (0, paths_1.createPaths)(args);
    const logStream = {
        writeLine: (_line) => { },
        writeLineSync: (_line) => { },
        close: async () => { }
    };
    const rest = new rest_1.RestManager();
    const shutdown = {
        register: (..._) => { },
    };
    const globalAsAny = global;
    const utGlobals = { args, paths, logStream, rest, shutdown, reset: resetGlobals, showLog };
    if (globalAsAny.nni === undefined) {
        globalAsAny.nni = utGlobals;
    }
    else {
        Object.assign(globalAsAny.nni, utGlobals);
    }
}
exports.resetGlobals = resetGlobals;
function showLog() {
    exports.globals.args.logLevel = 'trace';
    exports.globals.logStream.writeLine = (line) => { console.debug(line); };
    exports.globals.logStream.writeLineSync = (line) => { console.debug(line); };
}
function isUnitTest() {
    if (global.nniUnitTest) {
        return true;
    }
    const event = process.env['npm_lifecycle_event'] ?? '';
    return event.startsWith('test') || event === 'mocha' || event === 'nyc';
}
if (isUnitTest()) {
    resetGlobals();
}
exports.globals = global.nni;
exports.default = exports.globals;
