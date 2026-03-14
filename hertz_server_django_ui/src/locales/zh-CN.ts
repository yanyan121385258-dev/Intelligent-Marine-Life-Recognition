export default {
  common: {
    confirm: '确定',
    cancel: '取消',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    add: '添  加',
    search: '搜索',
    reset: '重置',
    loading: '加载中...',
    noData: '暂无数据',
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '提示',
  },
  nav: {
    home: '首页',
    dashboard: '仪表板',
    user: '用户管理',
    role: '角色管理',
    menu: '菜单管理',
    settings: '系统设置',
    profile: '个人资料',
    logout: '退出登录',
  },
  login: {
    title: '智慧海洋生物识别系统',
    username: '用户名',
    password: '密码',
    login: '登录',
    forgotPassword: '忘记密码？',
    rememberMe: '记住我',
  },
  register: {
    title: '注册',
    username: '用户名',
    email: '邮箱',
    password: '密码',
    confirmPassword: '确认密码',
    register: '注册',
    agreement: '我已阅读并同意',
    userAgreement: '用户协议',
    privacyPolicy: '隐私政策',
    hasAccount: '已有账号？',
    goToLogin: '立即登录',
  },
  success: {
    // 通用成功提示
    operationSuccess: '操作成功',
    saveSuccess: '保存成功',
    deleteSuccess: '删除成功',
    updateSuccess: '更新成功',

    // 登录注册相关成功提示
    loginSuccess: '登录成功',
    registerSuccess: '注册成功！请前往登录',
    logoutSuccess: '退出登录成功',
    emailCodeSent: '验证码已发送到您的邮箱',

    // 用户管理相关成功提示
    userCreated: '用户创建成功',
    userUpdated: '用户信息更新成功',
    userDeleted: '用户删除成功',
    roleAssigned: '角色分配成功',

    // 其他操作成功提示
    uploadSuccess: '文件上传成功',
    downloadSuccess: '文件下载成功',
    copySuccess: '复制成功',
  },
  error: {
    // 通用错误
    // 404: '页面未找到',
    403: '权限不足，请联系管理员',
    500: '服务器内部错误，请稍后重试',
    networkError: '网络连接失败，请检查网络设置',
    timeout: '请求超时，请稍后重试',

    // 登录相关错误
    loginFailed: '登录失败，请检查用户名和密码',
    usernameRequired: '请输入用户名',
    passwordRequired: '请输入密码',
    captchaRequired: '请输入验证码',
    captchaError: '验证码错误，请重新输入（区分大小写）',
    captchaExpired: '验证码已过期，请刷新后重新输入',
    accountLocked: '账户已被锁定，请联系管理员',
    accountDisabled: '账户已被禁用，请联系管理员',
    passwordExpired: '密码已过期，请修改密码',
    loginAttemptsExceeded: '登录尝试次数过多，账户已被临时锁定',

    // 注册相关错误
    registerFailed: '注册失败，请检查输入信息',
    usernameExists: '用户名已存在，请选择其他用户名',
    emailExists: '邮箱已被注册，请使用其他邮箱',
    phoneExists: '手机号已被注册，请使用其他手机号',
    emailFormatError: '邮箱格式不正确，请输入有效的邮箱地址',
    phoneFormatError: '手机号格式不正确，请输入11位手机号',
    passwordTooWeak: '密码强度不足，请包含大小写字母、数字和特殊字符',
    passwordMismatch: '两次输入的密码不一致',
    emailCodeError: '邮箱验证码错误或已过期',
    emailCodeRequired: '请输入邮箱验证码',
    emailCodeLength: '验证码长度为6位',
    emailRequired: '请输入邮箱',
    usernameLength: '用户名长度为3-20个字符',
    passwordLength: '密码长度为6-20个字符',
    confirmPasswordRequired: '请确认密码',
    phoneRequired: '请输入手机号',
    realNameRequired: '请输入真实姓名',
    realNameLength: '姓名长度为2-10个字符',

    // 权限相关错误
    accessDenied: '访问被拒绝，您没有执行此操作的权限',
    roleNotFound: '角色不存在或已被删除',
    permissionDenied: '权限不足，无法执行此操作',
    tokenExpired: '登录已过期，请重新登录',
    tokenInvalid: '登录状态无效，请重新登录',

    // 用户管理相关错误
    userNotFound: '用户不存在或已被删除',
    userCreateFailed: '创建用户失败，请检查输入信息',
    userUpdateFailed: '更新用户信息失败',
    userDeleteFailed: '删除用户失败，该用户可能正在使用中',
    cannotDeleteSelf: '不能删除自己的账户',
    cannotDeleteAdmin: '不能删除管理员账户',

    // 部门管理相关错误
    departmentNotFound: '部门不存在或已被删除',
    departmentNameExists: '部门名称已存在',
    departmentHasUsers: '部门下还有用户，无法删除',
    departmentCreateFailed: '创建部门失败',
    departmentUpdateFailed: '更新部门信息失败',
    departmentDeleteFailed: '删除部门失败',

    // 角色管理相关错误
    roleNameExists: '角色名称已存在',
    roleCreateFailed: '创建角色失败',
    roleUpdateFailed: '更新角色信息失败',
    roleDeleteFailed: '删除角色失败',
    roleInUse: '角色正在使用中，无法删除',

    // 文件上传相关错误
    fileUploadFailed: '文件上传失败',
    fileSizeExceeded: '文件大小超出限制',
    fileTypeNotSupported: '不支持的文件类型',
    fileRequired: '请选择要上传的文件',

    // 数据验证相关错误
    invalidInput: '输入数据格式不正确',
    requiredFieldMissing: '必填字段不能为空',
    fieldTooLong: '输入内容超出长度限制',
    fieldTooShort: '输入内容长度不足',
    invalidDate: '日期格式不正确',
    invalidNumber: '数字格式不正确',

    // 操作相关错误
    operationFailed: '操作失败，请稍后重试',
    saveSuccess: '保存成功',
    saveFailed: '保存失败，请检查输入信息',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败，请稍后重试',
    updateSuccess: '更新成功',
    updateFailed: '更新失败，请检查输入信息',

    // 系统相关错误
    systemMaintenance: '系统正在维护中，请稍后访问',
    serviceUnavailable: '服务暂时不可用，请稍后重试',
    databaseError: '数据库连接错误，请联系技术支持',
    configError: '系统配置错误，请联系管理员',
  },
};
