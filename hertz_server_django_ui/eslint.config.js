import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'

export default [
  // JavaScript 推荐规则
  js.configs.recommended,

  // TypeScript 推荐规则
  ...tseslint.configs.recommended,

  // Vue 推荐规则
  ...vue.configs['flat/recommended'],

  // 项目特定配置
  {
    files: ['**/*.{js,mjs,cjs,ts,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // 浏览器环境
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        // Node.js环境
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        global: 'readonly',
        // Vite环境
        import: 'readonly',
        // Vue环境
        Vue: 'readonly',
      }
    },
    rules: {
      // 禁用所有可能导致WebStorm警告的规则
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      'no-console': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'no-debugger': 'off',
      'no-alert': 'off',
      'no-prototype-builtins': 'off',

      // Vue相关规则
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'off',
      'vue/no-unused-components': 'off',
      'vue/no-unused-properties': 'off',
      'vue/require-v-for-key': 'off',
      'vue/no-use-v-if-with-v-for': 'off',

      // TypeScript规则
      '@typescript-eslint/no-var-requires': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/prefer-const': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-empty-function': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
    }
  },

  // 忽略文件
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      '.git/**',
      'coverage/**',
      '*.config.js',
      '*.config.ts',
    ]
  }
]
