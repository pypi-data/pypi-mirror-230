"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseArgs = void 0;
const strict_1 = __importDefault(require("assert/strict"));
const yargs_1 = __importDefault(require("yargs/yargs"));
function parseArgs(rawArgs) {
    const parser = (0, yargs_1.default)(rawArgs).options(yargsOptions).strict().fail(false);
    const parsedArgs = parser.parseSync();
    const argsAsAny = {};
    for (const key in yargsOptions) {
        argsAsAny[key] = parsedArgs[key];
        (0, strict_1.default)(!Number.isNaN(argsAsAny[key]), `Command line arg --${key} is not a number`);
    }
    const args = argsAsAny;
    const prefixErrMsg = `Command line arg --url-prefix "${args.urlPrefix}" is not stripped`;
    (0, strict_1.default)(!args.urlPrefix.startsWith('/') && !args.urlPrefix.endsWith('/'), prefixErrMsg);
    return args;
}
exports.parseArgs = parseArgs;
const yargsOptions = {
    port: {
        demandOption: true,
        type: 'number'
    },
    experimentId: {
        demandOption: true,
        type: 'string'
    },
    action: {
        choices: ['create', 'resume', 'view'],
        demandOption: true
    },
    experimentsDirectory: {
        demandOption: true,
        type: 'string'
    },
    logLevel: {
        choices: ['critical', 'error', 'warning', 'info', 'debug', 'trace'],
        demandOption: true
    },
    foreground: {
        default: false,
        type: 'boolean'
    },
    urlPrefix: {
        default: '',
        type: 'string'
    },
    tunerCommandChannel: {
        default: null,
        type: 'string'
    },
    pythonInterpreter: {
        demandOption: true,
        type: 'string'
    },
    mode: {
        default: '',
        type: 'string'
    }
};
