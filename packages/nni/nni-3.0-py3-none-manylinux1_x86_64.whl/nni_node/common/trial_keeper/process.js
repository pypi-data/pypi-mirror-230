"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TrialProcess = void 0;
const child_process_1 = __importDefault(require("child_process"));
const events_1 = __importDefault(require("events"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const deferred_1 = require("common/deferred");
const globals_1 = __importDefault(require("common/globals"));
const log_1 = require("common/log");
class TrialProcess {
    id;
    info = {};
    log;
    proc = null;
    started = new deferred_1.Deferred();
    stopped = new deferred_1.Deferred();
    constructor(id) {
        this.id = id;
        this.log = (0, log_1.getLogger)(`TrialProcess.${id}`);
    }
    async spawn(options) {
        const stdout = fs_1.default.createWriteStream(path_1.default.join(options.outputDirectory, 'trial.stdout'));
        const stderr = fs_1.default.createWriteStream(path_1.default.join(options.outputDirectory, 'trial.stderr'));
        await Promise.all([events_1.default.once(stdout, 'open'), events_1.default.once(stderr, 'open')]);
        let shell = true;
        if (options.shell) {
            shell = options.shell;
        }
        else if (process.platform !== 'win32') {
            shell = '/bin/bash';
        }
        const spawnOptions = {
            cwd: options.codeDirectory,
            env: this.buildEnv(options),
            stdio: ['ignore', stdout, stderr],
            shell: shell,
        };
        this.proc = child_process_1.default.spawn(options.command, spawnOptions);
        this.proc.on('spawn', () => { this.resolveStart('spawn'); });
        this.proc.on('exit', (code, signal) => { this.resolveStop('exit', code, signal); });
        this.proc.on('error', (err) => { this.handleError(err); });
        this.proc.on('close', (code, signal) => { this.resolveStop('close', code, signal); });
        await this.started.promise;
        return Boolean(this.info.startSuccess);
    }
    async kill(timeout) {
        this.log.trace('kill');
        if (!this.started.settled) {
            this.log.error('Killing a not started trial');
            return;
        }
        if (this.stopped.settled) {
            return;
        }
        if (process.platform === 'win32') {
            this.proc.kill();
        }
        else {
            this.proc.kill('SIGINT');
            setTimeout(() => {
                if (!this.stopped.settled) {
                    this.log.info(`Failed to terminate in ${timeout ?? 5000} ms, force kill`);
                    this.proc.kill('SIGKILL');
                }
            }, timeout ?? 5000);
        }
        await this.stopped.promise;
    }
    onStart(callback) {
        this.started.promise.then(() => {
            if (this.info.startSuccess) {
                callback(this.info.startTime);
            }
        });
    }
    onStop(callback) {
        this.stopped.promise.then(() => {
            if (this.info.startSuccess) {
                callback(this.info.stopTime, this.info.stopCode, this.info.stopSignal);
            }
        });
    }
    buildEnv(opts) {
        const env = { ...process.env, ...opts.environmentVariables };
        env['NNI_CODE_DIR'] = opts.codeDirectory;
        env['NNI_EXP_ID'] = globals_1.default.args.experimentId;
        env['NNI_OUTPUT_DIR'] = opts.outputDirectory;
        env['NNI_PLATFORM'] = opts.platform;
        env['NNI_SYS_DIR'] = opts.outputDirectory;
        env['NNI_TRIAL_COMMAND_CHANNEL'] = opts.commandChannelUrl;
        env['NNI_TRIAL_JOB_ID'] = this.id;
        env['NNI_TRIAL_SEQ_ID'] = String(opts.sequenceId ?? -1);
        this.log.trace('Env:', env);
        return env;
    }
    resolveStart(event) {
        this.log.trace('Start', event);
        if (this.started.settled) {
            this.log.warning(`Receive ${event} event after started`);
            return;
        }
        this.info.startTime = Date.now();
        if (this.stopped.settled) {
            this.log.error(`Receive ${event} event after stopped`);
            this.info.startSuccess = false;
        }
        else {
            this.info.startSuccess = true;
        }
        this.started.resolve();
    }
    resolveStop(event, code, signal, timestamp) {
        this.log.trace('Stop', event, code, signal, timestamp);
        if (event === 'close') {
            this.log.debug('Stopped and cleaned');
            this.proc = null;
        }
        if (this.stopped.settled) {
            if (event !== 'close' && timestamp === undefined) {
                this.log.warning(`Receive ${event} event after stopped`);
            }
            return;
        }
        this.info.stopTime = timestamp ?? Date.now();
        this.info.stopCode = code;
        this.info.stopSignal = signal;
        if (!this.started.settled) {
            this.log.error(`Receive ${event} event before starting`);
            this.info.startSuccess = false;
            this.started.resolve();
        }
        this.stopped.resolve();
    }
    handleError(err) {
        this.log.error('Error:', err);
        if (!this.stopped.settled) {
            const time = Date.now();
            setTimeout(() => { this.resolveStop('error', null, null, time); }, 1000);
        }
    }
}
exports.TrialProcess = TrialProcess;
