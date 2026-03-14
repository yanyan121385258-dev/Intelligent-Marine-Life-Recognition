#!/usr/bin/env node

// 一键裁剪脚本：根据功能模块删除或屏蔽对应的菜单配置和页面文件
// 设计原则：
// - 先通过运行时模块开关/页面确认要保留哪些模块
// - 然后运行本脚本，选择要“裁剪掉”的模块，以及裁剪模式：
//   1) 仅屏蔽（修改 moduleKey，使其永远不会被启用，保留页面文件）
//   2) 删除（在 1 的基础上，再删除对应 .vue 页面文件）
// - 脚本只操作前端代码，不影响后端

import fs from 'fs'
import path from 'path'
import readline from 'readline'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')

/** 模块定义（与 src/config/hertz_modules.ts 保持一致） */
const MODULES = [
  { key: 'admin.user-management', label: '管理端 · 用户管理', group: 'admin' },
  { key: 'admin.department-management', label: '管理端 · 部门管理', group: 'admin' },
  { key: 'admin.menu-management', label: '管理端 · 菜单管理', group: 'admin' },
  { key: 'admin.role-management', label: '管理端 · 角色管理', group: 'admin' },
  { key: 'admin.notification-management', label: '管理端 · 通知管理', group: 'admin' },
  { key: 'admin.log-management', label: '管理端 · 日志管理', group: 'admin' },
  { key: 'admin.knowledge-base', label: '管理端 · 文章管理', group: 'admin' },
  { key: 'admin.yolo-model', label: '管理端 · YOLO 模型相关', group: 'admin' },

  { key: 'user.system-monitor', label: '用户端 · 系统监控', group: 'user' },
  { key: 'user.ai-chat', label: '用户端 · AI 助手', group: 'user' },
  { key: 'user.yolo-detection', label: '用户端 · YOLO 检测', group: 'user' },
  { key: 'user.live-detection', label: '用户端 · 实时检测', group: 'user' },
  { key: 'user.detection-history', label: '用户端 · 检测历史', group: 'user' },
  { key: 'user.alert-center', label: '用户端 · 告警中心', group: 'user' },
  { key: 'user.notice-center', label: '用户端 · 通知中心', group: 'user' },
  { key: 'user.knowledge-center', label: '用户端 · 知识库中心', group: 'user' },
]

/**
 * 每个模块对应的裁剪配置：
 * - adminModuleKey / userModuleKey: 在路由配置文件中的 moduleKey 值
 * - adminComponentNames / userComponentNames: 在组件映射对象中的组件名（*.vue）
 * - viewFiles: 可以安全删除的页面文件（相对项目根路径）
 */
const PRUNE_CONFIG = {
  'admin.user-management': {
    adminModuleKey: 'admin.user-management',
    adminComponentNames: ['UserManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/UserManagement.vue'],
  },
  'admin.department-management': {
    adminModuleKey: 'admin.department-management',
    adminComponentNames: ['DepartmentManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/DepartmentManagement.vue'],
  },
  'admin.menu-management': {
    adminModuleKey: 'admin.menu-management',
    adminComponentNames: ['MenuManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/MenuManagement.vue'],
  },
  'admin.role-management': {
    adminModuleKey: 'admin.role-management',
    adminComponentNames: ['Role.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/Role.vue'],
  },
  'admin.notification-management': {
    adminModuleKey: 'admin.notification-management',
    adminComponentNames: ['NotificationManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/NotificationManagement.vue'],
  },
  'admin.log-management': {
    adminModuleKey: 'admin.log-management',
    adminComponentNames: ['LogManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/LogManagement.vue'],
  },
  'admin.knowledge-base': {
    adminModuleKey: 'admin.knowledge-base',
    adminComponentNames: ['KnowledgeBaseManagement.vue'],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: ['src/views/admin_page/KnowledgeBaseManagement.vue'],
  },
  'admin.yolo-model': {
    adminModuleKey: 'admin.yolo-model',
    adminComponentNames: [
      'ModelManagement.vue',
      'AlertLevelManagement.vue',
      'AlertProcessingCenter.vue',
      'DetectionHistoryManagement.vue',
    ],
    userModuleKey: null,
    userComponentNames: [],
    viewFiles: [
      'src/views/admin_page/ModelManagement.vue',
      'src/views/admin_page/AlertLevelManagement.vue',
      'src/views/admin_page/AlertProcessingCenter.vue',
      'src/views/admin_page/DetectionHistoryManagement.vue',
    ],
  },
  'user.system-monitor': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.system-monitor',
    userComponentNames: ['SystemMonitor.vue'],
    viewFiles: ['src/views/user_pages/SystemMonitor.vue'],
  },
  'user.ai-chat': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.ai-chat',
    userComponentNames: ['AiChat.vue'],
    viewFiles: ['src/views/user_pages/AiChat.vue'],
  },
  'user.yolo-detection': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.yolo-detection',
    userComponentNames: ['YoloDetection.vue'],
    viewFiles: ['src/views/user_pages/YoloDetection.vue'],
  },
  'user.live-detection': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.live-detection',
    userComponentNames: ['LiveDetection.vue'],
    viewFiles: ['src/views/user_pages/LiveDetection.vue'],
  },
  'user.detection-history': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.detection-history',
    userComponentNames: ['DetectionHistory.vue'],
    viewFiles: ['src/views/user_pages/DetectionHistory.vue'],
  },
  'user.alert-center': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.alert-center',
    userComponentNames: ['AlertCenter.vue'],
    viewFiles: ['src/views/user_pages/AlertCenter.vue'],
  },
  'user.notice-center': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.notice-center',
    userComponentNames: ['NoticeCenter.vue'],
    viewFiles: ['src/views/user_pages/NoticeCenter.vue'],
  },
  'user.knowledge-center': {
    adminModuleKey: null,
    adminComponentNames: [],
    userModuleKey: 'user.knowledge-center',
    userComponentNames: ['KnowledgeCenter.vue'],
    // 注意：这里只删除 KnowledgeCenter.vue，保留 KnowledgeDetail.vue，避免复杂路由修改
    viewFiles: ['src/views/user_pages/KnowledgeCenter.vue'],
  },
}

const ADMIN_MENU_FILE = 'src/router/admin_menu.ts'
const USER_MENU_FILE = 'src/router/user_menu_ai.ts'

/**
 * 简单的 CLI 交互封装
 */
const rl = readline.createInterface({ input: process.stdin, output: process.stdout })

function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim())
    })
  })
}

function resolvePath(relativePath) {
  return path.resolve(projectRoot, relativePath)
}

function readTextFile(relativePath) {
  const full = resolvePath(relativePath)
  if (!fs.existsSync(full)) {
    return null
  }
  return fs.readFileSync(full, 'utf8')
}

function writeTextFile(relativePath, content) {
  const full = resolvePath(relativePath)
  fs.writeFileSync(full, content, 'utf8')
}

function commentComponentLines(content, componentNames) {
  if (!componentNames || componentNames.length === 0) return content
  const lines = content.split('\n')
  const nameSet = new Set(componentNames)

  const updated = lines.map((line) => {
    const trimmed = line.trim()
    if (trimmed.startsWith('//')) return line

    for (const name of nameSet) {
      if (line.includes(`'${name}'`)) {
        return `// ${line}`
      }
    }
    return line
  })

  return updated.join('\n')
}

function updateModuleKey(content, originalKey) {
  if (!originalKey) return content
  const patterns = [
    `moduleKey: '${originalKey}'`,
    `moduleKey: "${originalKey}"`,
  ]
  const pruned = `moduleKey: '__pruned__${originalKey}'`

  if (content.includes(pruned)) {
    return content
  }

  let updated = content
  let found = false

  for (const p of patterns) {
    if (updated.includes(p)) {
      updated = updated.replace(p, pruned)
      found = true
    }
  }

  if (!found) {
    console.warn(`⚠️ 未在文件中找到 moduleKey: ${originalKey}`)
  }

  return updated
}

function collectViewFilesForModules(selectedKeys) {
  const files = new Set()
  for (const key of selectedKeys) {
    const cfg = PRUNE_CONFIG[key]
    if (!cfg) continue
    for (const f of cfg.viewFiles) {
      files.add(f)
    }
  }
  return Array.from(files)
}

async function main() {
  console.log('===== Hertz 模板 · 一键裁剪脚本 =====')
  console.log('说明：')
  console.log('1. 建议先在浏览器里通过“模板模式 + 模块选择页”确认要保留的模块')
  console.log('2. 然后关闭 dev 服务器，运行本脚本选择要裁剪掉的模块')
  console.log('3. 先可选择“仅屏蔽”，确认无误后，再选择“删除”彻底缩减代码体积')
  console.log('')

  console.log('当前可裁剪模块：')
  MODULES.forEach((m, index) => {
    console.log(`${index + 1}. [${m.group}] ${m.label} (${m.key})`)
  })
  console.log('')

  const indexAnswer = await ask('请输入要“裁剪掉”的模块序号（多个用逗号分隔，例如 2,4,7），或直接回车取消：')
  if (!indexAnswer) {
    console.log('未选择任何模块，退出。')
    rl.close()
    return
  }

  const indexes = indexAnswer
    .split(',')
    .map((s) => parseInt(s.trim(), 10))
    .filter((n) => !Number.isNaN(n) && n >= 1 && n <= MODULES.length)

  if (indexes.length === 0) {
    console.log('未解析出有效的序号，退出。')
    rl.close()
    return
  }

  const selectedModules = Array.from(new Set(indexes.map((i) => MODULES[i - 1])))
  console.log('\n将要裁剪的模块：')
  selectedModules.forEach((m) => {
    console.log(`- [${m.group}] ${m.label} (${m.key})`)
  })

  console.log('\n裁剪模式：')
  console.log('1) 仅屏蔽模块：')
  console.log('   - 修改 router 配置中的 moduleKey 为 __pruned__...')
  console.log('   - 生成的菜单和路由中将完全隐藏这些模块')
  console.log('   - 不删除任何 .vue 页面文件（可随时恢复）')
  console.log('2) 删除模块：')
  console.log('   - 在 1 的基础上，额外删除对应的 .vue 页面文件')
  console.log('   - 删除操作不可逆，请确保已经提交或备份代码\n')

  const modeAnswer = await ask('请选择裁剪模式（1 = 仅屏蔽，2 = 删除）：')
  const mode = modeAnswer === '2' ? 'delete' : 'comment'

  const viewFiles = collectViewFilesForModules(selectedModules.map((m) => m.key))

  console.log('\n即将进行如下修改：')
  console.log('- 修改文件: src/router/admin_menu.ts（按需）')
  console.log('- 修改文件: src/router/user_menu_ai.ts（按需）')
  if (mode === 'delete') {
    console.log('- 删除页面文件:')
    viewFiles.forEach((f) => console.log(`  · ${f}`))
  } else {
    console.log('- 不删除任何页面文件，仅屏蔽模块')
  }

  const confirm = await ask('\n确认执行这些修改吗？(y/N): ')
  if (confirm.toLowerCase() !== 'y') {
    console.log('已取消操作。')
    rl.close()
    return
  }

  // 1) 修改 admin_menu.ts
  let adminMenuContent = readTextFile(ADMIN_MENU_FILE)
  if (adminMenuContent) {
    const adminKeys = selectedModules.map((m) => m.key).filter((k) => PRUNE_CONFIG[k]?.adminModuleKey)
    if (adminKeys.length > 0) {
      for (const key of adminKeys) {
        const cfg = PRUNE_CONFIG[key]
        adminMenuContent = updateModuleKey(adminMenuContent, cfg.adminModuleKey)
        adminMenuContent = commentComponentLines(adminMenuContent, cfg.adminComponentNames)
      }
      writeTextFile(ADMIN_MENU_FILE, adminMenuContent)
      console.log('✅ 已更新 src/router/admin_menu.ts')
    }
  }

  // 2) 修改 user_menu_ai.ts
  let userMenuContent = readTextFile(USER_MENU_FILE)
  if (userMenuContent) {
    const userKeys = selectedModules.map((m) => m.key).filter((k) => PRUNE_CONFIG[k]?.userModuleKey)
    if (userKeys.length > 0) {
      for (const key of userKeys) {
        const cfg = PRUNE_CONFIG[key]
        userMenuContent = updateModuleKey(userMenuContent, cfg.userModuleKey)
        userMenuContent = commentComponentLines(userMenuContent, cfg.userComponentNames)
      }
      writeTextFile(USER_MENU_FILE, userMenuContent)
      console.log('✅ 已更新 src/router/user_menu_ai.ts')
    }
  }

  // 3) 删除 .vue 页面文件（仅在 delete 模式下）
  if (mode === 'delete') {
    console.log('\n开始删除页面文件...')
    for (const relative of viewFiles) {
      const full = resolvePath(relative)
      if (fs.existsSync(full)) {
        fs.rmSync(full)
        console.log(`🗑️ 已删除: ${relative}`)
      } else {
        console.log(`⚠️ 文件不存在，跳过: ${relative}`)
      }
    }
  }

  console.log('\n🎉 裁剪完成。建议执行以下操作检查：')
  console.log('- 重新运行: npm run dev')
  console.log('- 在浏览器中确认菜单和路由是否符合预期')
  console.log('- 如需恢复，请使用 Git 回退或重新拷贝模板')

  rl.close()
}

main().catch((err) => {
  console.error('执行过程中发生错误:', err)
  rl.close()
  process.exit(1)
})
