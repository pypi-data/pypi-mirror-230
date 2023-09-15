"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.collectPlatformInfo = void 0;
const promises_1 = __importDefault(require("node:fs/promises"));
const node_os_1 = __importDefault(require("node:os"));
const node_util_1 = __importDefault(require("node:util"));
const globals_1 = require("common/globals");
const log_1 = require("common/log");
const pythonScript_1 = require("common/pythonScript");
const utils_1 = require("common/utils");
async function collectPlatformInfo(includeGpu) {
    const detailed = (globals_1.globals.args.logLevel === 'debug' || globals_1.globals.args.logLevel === 'trace');
    const info = {};
    const errors = {};
    try {
        const versionJson = await (0, pythonScript_1.runPythonModule)('nni.tools.nni_manager_scripts.collect_version_info');
        info.version = JSON.parse(versionJson);
    }
    catch (error) {
        errors.version = error;
    }
    info.system = {
        platform: process.platform,
        version: node_os_1.default.release(),
    };
    try {
        info.cpu = getCpuInfo(detailed);
    }
    catch (error) {
        errors.cpu = error;
    }
    if (includeGpu) {
        try {
            const args = detailed ? ['--detail'] : undefined;
            const gpuJson = await (0, pythonScript_1.runPythonModule)('nni.tools.nni_manager_scripts.collect_gpu_info', args);
            info.gpu = JSON.parse(gpuJson);
        }
        catch (error) {
            errors.gpu = error;
        }
    }
    try {
        info.memory = {
            memory: formatSize(node_os_1.default.totalmem()),
            freeMemory: formatSize(node_os_1.default.freemem()),
            utilization: formatUtil(1 - node_os_1.default.freemem() / node_os_1.default.totalmem()),
        };
    }
    catch (error) {
        errors.memory = error;
    }
    try {
        info.disk = await getDiskInfo();
    }
    catch (error) {
        errors.disk = error;
    }
    if (detailed) {
        try {
            const ipv4 = await (0, utils_1.getIPV4Address)();
            info.network = { ipv4 };
        }
        catch (error) {
            errors.network = error;
        }
    }
    for (const key in errors) {
        (0, log_1.getLogger)('collectEnvironmentInfo').error(`Failed to collect ${key} info:`, errors[key]);
        info[key] = { error: node_util_1.default.inspect(errors[key]) };
    }
    return info;
}
exports.collectPlatformInfo = collectPlatformInfo;
function getCpuInfo(detailed) {
    const ret = {};
    const cpus = node_os_1.default.cpus();
    if (detailed) {
        const models = cpus.map(cpu => cpu.model);
        const dedup = Array.from(new Set(models));
        ret.model = (dedup.length === 1 ? dedup[0] : dedup);
        ret.architecture = node_os_1.default.arch();
    }
    ret.logicalCores = cpus.length;
    if (process.platform !== 'win32') {
        ret.utilization = formatUtil(node_os_1.default.loadavg()[0]);
    }
    return ret;
}
async function getDiskInfo() {
    const statfs = await promises_1.default.statfs(globals_1.globals.paths.experimentRoot);
    const typeHex = '0x' + statfs.type.toString(16);
    return {
        filesystem: fsTypes[typeHex] ?? typeHex,
        space: formatSize(statfs.blocks * statfs.bsize),
        availableSpace: formatSize(statfs.bavail * statfs.bsize),
        utilization: formatUtil(1 - statfs.bavail / statfs.blocks),
    };
}
const fsTypes = {
    '0x9123683e': 'btrfs',
    '0xef53': 'ext4',
    '0x65735546': 'fuse',
    '0x6969': 'nfs',
    '0x6e736673': 'ntfs',
    '0x01021994': 'tmpfs',
};
function formatUtil(util) {
    return `${Math.round(util * 100)}%`;
}
function formatSize(size, disk) {
    let units;
    if (disk) {
        units = ['KiB', 'MiB', 'GiB', 'TiB'];
    }
    else {
        units = ['KB', 'MB', 'GB'];
    }
    let num = size;
    let unit = 'B';
    for (const u of units) {
        if (num >= 1024) {
            num /= 1024;
            unit = u;
        }
        else {
            break;
        }
    }
    if (num >= 10) {
        num = Math.round(num);
    }
    else {
        num = Math.round(num * 10) / 10;
    }
    return `${num}${unit}`;
}
