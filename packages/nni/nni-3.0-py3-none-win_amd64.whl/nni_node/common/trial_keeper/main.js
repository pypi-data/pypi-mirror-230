"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const promises_1 = __importDefault(require("node:fs/promises"));
const node_path_1 = __importDefault(require("node:path"));
const node_util_1 = __importDefault(require("node:util"));
const app_module_path_1 = require("app-module-path");
(0, app_module_path_1.addPath)(node_path_1.default.dirname(node_path_1.default.dirname(__dirname)));
const globals_1 = require("common/globals");
const log_1 = require("common/log");
const client_1 = require("common/command_channel/websocket/client");
const core_1 = require("rest_server/core");
const rpc_1 = require("./rpc");
const logger = (0, log_1.getRobustLogger)('TrialKeeper.main');
async function main() {
    process.on('SIGTERM', () => { globals_1.globals.shutdown.initiate('SIGTERM'); });
    process.on('SIGBREAK', () => { globals_1.globals.shutdown.initiate('SIGBREAK'); });
    process.on('SIGINT', () => { globals_1.globals.shutdown.initiate('SIGINT'); });
    const workDir = process.argv[2];
    const configPath = node_path_1.default.join(workDir, 'trial_keeper_config.json');
    const config = JSON.parse(await promises_1.default.readFile(configPath, { encoding: 'utf8' }));
    const args = {
        experimentId: config.experimentId,
        experimentsDirectory: config.experimentsDirectory,
        logLevel: config.logLevel,
        pythonInterpreter: config.pythonInterpreter,
        platform: config.platform,
        environmentId: config.environmentId,
        managerCommandChannel: config.managerCommandChannel,
        port: 0,
        action: 'create',
        foreground: false,
        urlPrefix: '',
        tunerCommandChannel: null,
        mode: '',
    };
    const logPath = node_path_1.default.join(workDir, 'trial_keeper.log');
    (0, globals_1.initGlobalsCustom)(args, logPath);
    logger.info('Trial keeper start');
    logger.debug('command:', process.argv);
    logger.debug('config:', config);
    const client = new client_1.WsChannelClient(args.environmentId, args.managerCommandChannel);
    client.enableHeartbeat();
    client.onClose(reason => {
        logger.info('Manager closed connection:', reason);
        globals_1.globals.shutdown.initiate('Connection end');
    });
    client.onError(error => {
        logger.info('Connection error:', error);
        globals_1.globals.shutdown.initiate('Connection error');
    });
    (0, rpc_1.registerTrialKeeperOnChannel)(client);
    await client.connect();
    const restServer = new core_1.RestServerCore();
    await restServer.start();
    logger.info('Running on port', globals_1.globals.args.port);
    logger.info('Initialized');
    globals_1.globals.shutdown.notifyInitializeComplete();
    await promises_1.default.writeFile(node_path_1.default.join(workDir, 'success.flag'), 'ok');
    setInterval(() => {
        logger.debug('@', new Date());
    }, 1000);
}
if (!process.argv[1].includes('mocha')) {
    main().catch(error => {
        logger.critical(error);
        console.error(node_util_1.default.inspect(error));
        process.exit(1);
    });
}
