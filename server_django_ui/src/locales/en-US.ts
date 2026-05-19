export default {
  common: {
    confirm: 'Confirm',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    search: 'Search',
    reset: 'Reset',
    loading: 'Loading...',
    noData: 'No Data',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
  },
  nav: {
    home: 'Home',
    dashboard: 'Dashboard',
    user: 'User Management',
    role: 'Role Management',
    menu: 'Menu Management',
    settings: 'System Settings',
    profile: 'Profile',
    logout: 'Logout',
  },
  login: {
    title: 'Login',
    username: 'Username',
    password: 'Password',
    login: 'Login',
    forgotPassword: 'Forgot Password?',
    rememberMe: 'Remember Me',
  },
  success: {
    // General success messages
    operationSuccess: 'Operation Successful',
    saveSuccess: 'Save Successful',
    deleteSuccess: 'Delete Successful',
    updateSuccess: 'Update Successful',

    // Login and registration related success messages
    loginSuccess: 'Login Successful',
    registerSuccess: 'Registration Successful! Please Login',
    logoutSuccess: 'Logout Successful',
    emailCodeSent: 'Verification Code Sent to Your Email',

    // User management related success messages
    userCreated: 'User Created Successfully',
    userUpdated: 'User Information Updated Successfully',
    userDeleted: 'User Deleted Successfully',
    roleAssigned: 'Role Assigned Successfully',

    // Other operation success messages
    uploadSuccess: 'File Upload Successful',
    downloadSuccess: 'File Download Successful',
    copySuccess: 'Copy Successful',
  },
  error: {
    // General errors
    // 404: 'Page Not Found',
    403: 'Access Denied, Please Contact Administrator',
    500: 'Internal Server Error, Please Try Again Later',
    networkError: 'Network Connection Failed, Please Check Network Settings',
    timeout: 'Request Timeout, Please Try Again Later',

    // Login related errors
    loginFailed: 'Login Failed, Please Check Username and Password',
    usernameRequired: 'Please Enter Username',
    passwordRequired: 'Please Enter Password',
    captchaRequired: 'Please Enter Captcha',
    captchaError: 'Captcha Error, Please Re-enter (Case Sensitive)',
    captchaExpired: 'Captcha Expired, Please Refresh and Re-enter',
    accountLocked: 'Account Locked, Please Contact Administrator',
    accountDisabled: 'Account Disabled, Please Contact Administrator',
    passwordExpired: 'Password Expired, Please Change Password',
    loginAttemptsExceeded: 'Too Many Login Attempts, Account Temporarily Locked',

    // Registration related errors
    registerFailed: 'Registration Failed, Please Check Input Information',
    usernameExists: 'Username Already Exists, Please Choose Another',
    emailExists: 'Email Already Registered, Please Use Another Email',
    phoneExists: 'Phone Number Already Registered, Please Use Another',
    emailFormatError: 'Invalid Email Format, Please Enter Valid Email',
    phoneFormatError: 'Invalid Phone Format, Please Enter 11-digit Phone Number',
    passwordTooWeak:
      'Password Too Weak, Please Include Uppercase, Lowercase, Numbers and Special Characters',
    passwordMismatch: 'Passwords Do Not Match',
    emailCodeError: 'Email Verification Code Error or Expired',
    emailCodeRequired: 'Please Enter Email Verification Code',
    emailCodeLength: 'Verification Code Must Be 6 Digits',
    emailRequired: 'Please Enter Email',
    usernameLength: 'Username Length Must Be 3-20 Characters',
    passwordLength: 'Password Length Must Be 6-20 Characters',
    confirmPasswordRequired: 'Please Confirm Password',
    phoneRequired: 'Please Enter Phone Number',
    realNameRequired: 'Please Enter Real Name',
    realNameLength: 'Name Length Must Be 2-10 Characters',

    // Permission related errors
    accessDenied: 'Access Denied, You Do Not Have Permission to Perform This Action',
    roleNotFound: 'Role Not Found or Deleted',
    permissionDenied: 'Permission Denied, Cannot Perform This Action',
    tokenExpired: 'Login Expired, Please Login Again',
    tokenInvalid: 'Invalid Login Status, Please Login Again',

    // User management related errors
    userNotFound: 'User Not Found or Deleted',
    userCreateFailed: 'Failed to Create User, Please Check Input Information',
    userUpdateFailed: 'Failed to Update User Information',
    userDeleteFailed: 'Failed to Delete User, User May Be In Use',
    cannotDeleteSelf: 'Cannot Delete Your Own Account',
    cannotDeleteAdmin: 'Cannot Delete Administrator Account',

    // Department management related errors
    departmentNotFound: 'Department Not Found or Deleted',
    departmentNameExists: 'Department Name Already Exists',
    departmentHasUsers: 'Department Has Users, Cannot Delete',
    departmentCreateFailed: 'Failed to Create Department',
    departmentUpdateFailed: 'Failed to Update Department Information',
    departmentDeleteFailed: 'Failed to Delete Department',

    // Role management related errors
    roleNameExists: 'Role Name Already Exists',
    roleCreateFailed: 'Failed to Create Role',
    roleUpdateFailed: 'Failed to Update Role Information',
    roleDeleteFailed: 'Failed to Delete Role',
    roleInUse: 'Role In Use, Cannot Delete',

    // File upload related errors
    fileUploadFailed: 'File Upload Failed',
    fileSizeExceeded: 'File Size Exceeded Limit',
    fileTypeNotSupported: 'File Type Not Supported',
    fileRequired: 'Please Select File to Upload',

    // Data validation related errors
    invalidInput: 'Invalid Input Data Format',
    requiredFieldMissing: 'Required Field Cannot Be Empty',
    fieldTooLong: 'Input Content Exceeds Length Limit',
    fieldTooShort: 'Input Content Length Insufficient',
    invalidDate: 'Invalid Date Format',
    invalidNumber: 'Invalid Number Format',

    // Operation related errors
    operationFailed: 'Operation Failed, Please Try Again Later',
    saveSuccess: 'Save Successful',
    saveFailed: 'Save Failed, Please Check Input Information',
    deleteSuccess: 'Delete Successful',
    deleteFailed: 'Delete Failed, Please Try Again Later',
    updateSuccess: 'Update Successful',
    updateFailed: 'Update Failed, Please Check Input Information',

    // System related errors
    systemMaintenance: 'System Under Maintenance, Please Visit Later',
    serviceUnavailable: 'Service Temporarily Unavailable, Please Try Again Later',
    databaseError: 'Database Connection Error, Please Contact Technical Support',
    configError: 'System Configuration Error, Please Contact Administrator',
  },
};
