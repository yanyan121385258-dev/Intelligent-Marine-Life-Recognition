import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 1. 系统信息
export interface SystemInfo {
  hostname: string;
  platform: string;
  architecture: string;
  boot_time: string;
  uptime: string;
}

// 2. CPU 信息
export interface CpuInfo {
  cpu_count: number;
  cpu_percent: number;
  cpu_freq: {
    current: number;
    min: number;
    max: number;
  };
  load_avg: number[];
}

// 3. 内存信息
export interface MemoryInfo {
  total: number;
  available: number;
  used: number;
  percent: number;
  free: number;
}

// 4. 磁盘信息
export interface DiskInfo {
  device: string;
  mountpoint: string;
  fstype: string;
  total: number;
  used: number;
  free: number;
  percent: number;
}

// 5. 网络信息
export interface NetworkInfo {
  interface: string;
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
}

// 6. 进程信息
export interface ProcessInfo {
  pid: number;
  name: string;
  status: string;
  cpu_percent: number;
  memory_percent: number;
  memory_info: {
    rss: number;
    vms: number;
  };
  create_time: string;
  cmdline: string[];
}

// 7. GPU 信息
export interface GpuInfoItem {
  id: number;
  name: string;
  load: number;
  memory_total: number;
  memory_used: number;
  memory_util: number;
  temperature: number;
}

export interface GpuInfoResponse {
  gpu_available: boolean;
  gpu_info?: GpuInfoItem[];
  message?: string;
  timestamp: string;
}

// 8. 综合监测信息
export interface MonitorData {
  system: SystemInfo;
  cpu: CpuInfo;
  memory: MemoryInfo;
  disks: DiskInfo[];
  network: NetworkInfo[];
  processes: ProcessInfo[];
  gpus: Array<{ gpu_available: boolean; message?: string; timestamp: string }>;
}

export const systemMonitorApi = {
  getSystem: (): Promise<ApiResponse<SystemInfo>> => request.get('/api/system/system/'),
  getCpu: (): Promise<ApiResponse<CpuInfo>> => request.get('/api/system/cpu/'),
  getMemory: (): Promise<ApiResponse<MemoryInfo>> => request.get('/api/system/memory/'),
  getDisks: (): Promise<ApiResponse<DiskInfo[]>> => request.get('/api/system/disks/'),
  getNetwork: (): Promise<ApiResponse<NetworkInfo[]>> => request.get('/api/system/network/'),
  getProcesses: (): Promise<ApiResponse<ProcessInfo[]>> => request.get('/api/system/processes/'),
  getGpu: (): Promise<ApiResponse<GpuInfoResponse>> => request.get('/api/system/gpu/'),
  getMonitor: (): Promise<ApiResponse<MonitorData>> => request.get('/api/system/monitor/'),
};
