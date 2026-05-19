/**
 * URL处理工具函数
 */

/**
 * 获取完整的文件URL
 * @param relativePath 相对路径，如 /media/detection/original/xxx.jpg
 * @returns 完整的URL
 */
export function getFullFileUrl(relativePath: string): string {
  if (!relativePath) {
    console.warn('⚠️ 文件路径为空');
    return '';
  }

  // 如果已经是完整URL，直接返回
  if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
    return relativePath;
  }

  // 在开发环境中，使用相对路径（通过Vite代理）
  if (import.meta.env.DEV) {
    return relativePath;
  }

  // 在生产环境中，拼接完整的URL
  const baseURL = getBackendBaseUrl();
  return `${baseURL}${relativePath}`;
}

export function getBackendBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
}

export function getWsBaseUrl(): string {
  const httpBase = getBackendBaseUrl();
  if (httpBase.startsWith('https://')) {
    return 'wss://' + httpBase.slice('https://'.length);
  }
  if (httpBase.startsWith('http://')) {
    return 'ws://' + httpBase.slice('http://'.length);
  }
  return httpBase;
}

/**
 * 获取API基础URL
 * @returns API基础URL
 */
export function getApiBaseUrl(): string {
  if (import.meta.env.DEV) {
    return ''; // 开发环境使用空字符串，通过Vite代理
  }
  return getBackendBaseUrl();
}

/**
 * 获取媒体文件基础URL
 * @returns 媒体文件基础URL
 */
export function getMediaBaseUrl(): string {
  if (import.meta.env.DEV) {
    return ''; // 开发环境使用空字符串，通过Vite代理
  }
  const baseURL = getBackendBaseUrl();
  return baseURL.replace('/api', ''); // 移除/api后缀
}

/**
 * 检查URL是否可访问
 * @param url 要检查的URL
 * @returns Promise<boolean>
 */
export async function checkUrlAccessibility(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    return response.ok;
  } catch (error) {
    console.error('❌ URL访问检查失败:', url, error);
    return false;
  }
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 获取文件扩展名
 * @param filename 文件名
 * @returns 文件扩展名
 */
export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

/**
 * 检查是否为图片文件
 * @param filename 文件名或URL
 * @returns 是否为图片文件
 */
export function isImageFile(filename: string): boolean {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
  const extension = getFileExtension(filename);
  return imageExtensions.includes(extension);
}

/**
 * 检查是否为视频文件
 * @param filename 文件名或URL
 * @returns 是否为视频文件
 */
export function isVideoFile(filename: string): boolean {
  const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'];
  const extension = getFileExtension(filename);
  return videoExtensions.includes(extension);
}
