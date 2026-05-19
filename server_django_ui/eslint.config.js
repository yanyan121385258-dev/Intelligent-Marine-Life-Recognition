import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import parserVue from 'vue-eslint-parser'

export default [
  // JavaScript 推荐规则
  js.configs.recommended,

  // TypeScript 推荐规则
  ...tseslint.configs.recommended,

  // Vue 推荐规则
  ...vue.configs['flat/recommended'],

  // 项目特定配置
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    }
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: tseslint.parser,
      globals: {
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        global: 'readonly',
      }
    }
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,vue}'],
    languageOptions: {
      globals: {
        // 浏览器全局变量
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        CustomEvent: 'readonly',
        DOMParser: 'readonly',
        SpeechSynthesis: 'readonly',
        SpeechSynthesisUtterance: 'readonly',
        SpeechSynthesisVoice: 'readonly',
        HTMLInputElement: 'readonly',
        alert: 'readonly',
      },
    },
    rules: {
      // 禁用规则
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      'no-console': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'no-debugger': 'off',
      'no-alert': 'off',
      'no-prototype-builtins': 'off',

      // Vue 规则
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'off',
      'vue/no-unused-components': 'off',
      'vue/no-unused-properties': 'off',
      'vue/require-v-for-key': 'off',
      'vue/no-use-v-if-with-v-for': 'off',

      // TypeScript 规则
      '@typescript-eslint/no-var-requires': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/prefer-const': 'off',
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
      '*.config.cjs',
    ]
  }
]
