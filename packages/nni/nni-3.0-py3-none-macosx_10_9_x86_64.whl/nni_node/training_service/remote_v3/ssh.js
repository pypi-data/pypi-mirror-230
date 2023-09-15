"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Ssh = void 0;
const node_events_1 = __importDefault(require("node:events"));
const promises_1 = __importDefault(require("node:fs/promises"));
const node_util_1 = __importDefault(require("node:util"));
const ssh2_1 = require("ssh2");
const deferred_1 = require("common/deferred");
const log_1 = require("common/log");
class Ssh {
    config;
    client = null;
    sftpSession = null;
    path = null;
    log;
    constructor(name, config) {
        this.log = (0, log_1.getLogger)(`RemoteV3.Ssh.${name}`);
        this.config = config;
    }
    async connect() {
        this.log.debug('Connecting', this.config);
        const sshConfig = {
            host: this.config.host,
            port: this.config.port,
            username: this.config.user,
            password: this.config.password,
        };
        if (this.config.sshKeyFile) {
            sshConfig.privateKey = await promises_1.default.readFile(this.config.sshKeyFile, { encoding: 'utf8' });
            sshConfig.passphrase = this.config.sshPassphrase;
        }
        this.client = new ssh2_1.Client();
        this.client.connect(sshConfig);
        await node_events_1.default.once(this.client, 'ready');
        this.log.debug('Connected');
    }
    disconnect() {
        this.log.debug('Disconnect');
        if (this.client) {
            this.client.end();
        }
        this.client = null;
        this.sftpSession = null;
    }
    setPath(path) {
        this.path = path;
    }
    async exec(command) {
        this.log.debug('Execute command:', command);
        const deferred = new deferred_1.Deferred();
        const result = { stdout: '', stderr: '' };
        if (this.path !== null) {
            command = `PATH="${this.path}" ${command}`;
        }
        this.client.exec(command, (error, stream) => {
            if (error) {
                deferred.reject(error);
            }
            else {
                stream.on('data', (data) => { result.stdout += String(data); });
                stream.stderr.on('data', (data) => { result.stderr += String(data); });
                stream.on('close', (code, signal) => {
                    if (code || code === 0) {
                        result.code = Number(code);
                    }
                    if (signal) {
                        result.signal = String(signal);
                    }
                    deferred.resolve();
                });
            }
        });
        await deferred.promise;
        if (result.stdout.length > 100) {
            this.log.debug('Command result:', {
                code: result.code,
                stdout: result.stdout.slice(0, 80) + ' ...',
                stderr: result.stderr,
            });
            this.log.trace('Full result:', result);
        }
        else {
            this.log.debug('Command result:', result);
        }
        return result;
    }
    async run(command) {
        const result = await this.exec(command);
        if (result.code !== 0) {
            this.log.error('Command failed:', command, result);
            throw new Error(`SSH command failed: ${command}`);
        }
        return result.stdout.trim();
    }
    async download(remotePath, localPath) {
        this.log.debug(`Downloading ${localPath} <- ${remotePath}`);
        const sftp = await this.sftp();
        const fastGet = node_util_1.default.promisify(sftp.fastGet.bind(sftp));
        await fastGet(remotePath.replaceAll('\\', '/'), localPath);
        this.log.debug('Download success');
    }
    async upload(localPath, remotePath) {
        this.log.debug(`Uploading ${localPath} -> ${remotePath}`);
        const sftp = await this.sftp();
        const fastPut = node_util_1.default.promisify(sftp.fastPut.bind(sftp));
        await fastPut(localPath, remotePath.replaceAll('\\', '/'));
        this.log.debug('Upload success');
    }
    async writeFile(remotePath, data) {
        this.log.debug('Writing remote file', remotePath);
        const sftp = await this.sftp();
        const stream = sftp.createWriteStream(remotePath.replaceAll('\\', '/'));
        const deferred = new deferred_1.Deferred();
        stream.end(data, () => { deferred.resolve(); });
        return deferred.promise;
    }
    async sftp() {
        if (!this.sftpSession) {
            const sftp = node_util_1.default.promisify(this.client.sftp.bind(this.client));
            this.sftpSession = await sftp();
        }
        return this.sftpSession;
    }
}
exports.Ssh = Ssh;
