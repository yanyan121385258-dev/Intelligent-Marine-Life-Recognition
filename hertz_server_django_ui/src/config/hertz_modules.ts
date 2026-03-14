export type HertzModuleGroup = 'admin' | 'user';

export interface HertzModule {
  key: string;
  label: string;
  group: HertzModuleGroup;
  description?: string;
  defaultEnabled: boolean;
}

export const HERTZ_MODULES: HertzModule[] = [
  {
    key: 'admin.user-management',
    label: '管理端 · 用户管理',
    group: 'admin',
    defaultEnabled: true,
  },
  {
    key: 'admin.department-management',
    label: '管理端 · 部门管理',
    group: 'admin',
    defaultEnabled: true,
  },
  {
    key: 'admin.menu-management',
    label: '管理端 · 菜单管理',
    group: 'admin',
    defaultEnabled: true,
  },
  {
    key: 'admin.role-management',
    label: '管理端 · 角色管理',
    group: 'admin',
    defaultEnabled: true,
  },
  {
    key: 'admin.notification-management',
    label: '管理端 · 通知管理',
    group: 'admin',
    defaultEnabled: true,
  },
  { key: 'admin.log-management', label: '管理端 · 日志管理', group: 'admin', defaultEnabled: true },
  { key: 'admin.knowledge-base', label: '管理端 · 文章管理', group: 'admin', defaultEnabled: true },
  {
    key: 'admin.yolo-model',
    label: '管理端 · YOLO 模型相关',
    group: 'admin',
    defaultEnabled: true,
  },

  { key: 'user.system-monitor', label: '用户端 · 系统监控', group: 'user', defaultEnabled: true },
  { key: 'user.ai-chat', label: '用户端 · AI 助手', group: 'user', defaultEnabled: true },
  { key: 'user.yolo-detection', label: '用户端 · YOLO 检测', group: 'user', defaultEnabled: true },
  { key: 'user.live-detection', label: '用户端 · 实时检测', group: 'user', defaultEnabled: true },
  {
    key: 'user.detection-history',
    label: '用户端 · 检测历史',
    group: 'user',
    defaultEnabled: true,
  },
  { key: 'user.alert-center', label: '用户端 · 告警中心', group: 'user', defaultEnabled: true },
  { key: 'user.notice-center', label: '用户端 · 通知中心', group: 'user', defaultEnabled: true },
  { key: 'user.knowledge-center', label: '用户端 · 文章中心', group: 'user', defaultEnabled: true },
  { key: 'user.kb-center', label: '用户端 · 知识库中心', group: 'user', defaultEnabled: true },
];

const LOCAL_STORAGE_KEY = 'hertz_enabled_modules';

export function getEnabledModuleKeys(): string[] {
  const fallback = HERTZ_MODULES.filter((m) => m.defaultEnabled).map((m) => m.key);

  if (typeof window === 'undefined') {
    return fallback;
  }

  try {
    const stored = window.localStorage.getItem(LOCAL_STORAGE_KEY);
    if (!stored) return fallback;
    const parsed = JSON.parse(stored);
    if (Array.isArray(parsed)) {
      const valid = parsed.filter((k): k is string => typeof k === 'string');
      // 自动合并新增的默认启用模块，避免新模块在已有选择下被永久隐藏
      const missingDefaults = HERTZ_MODULES.filter(
        (m) => m.defaultEnabled && !valid.includes(m.key)
      ).map((m) => m.key);
      return [...valid, ...missingDefaults];
    }
    return fallback;
  } catch {
    return fallback;
  }
}

export function setEnabledModuleKeys(keys: string[]): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(keys));
  } catch {
    // ignore
  }
}

export function isModuleEnabled(moduleKey?: string, enabledKeys?: string[]): boolean {
  if (!moduleKey) return true;
  const keys = enabledKeys ?? getEnabledModuleKeys();
  return keys.indexOf(moduleKey) !== -1;
}

export function getModulesByGroup(group: HertzModuleGroup): HertzModule[] {
  return HERTZ_MODULES.filter((m) => m.group === group);
}

export function hasModuleSelection(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return window.localStorage.getItem(LOCAL_STORAGE_KEY) !== null;
  } catch {
    return false;
  }
}
