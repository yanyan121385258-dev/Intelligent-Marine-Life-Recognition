import { defineConfig, type Plugin, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'
import Components from 'unplugin-vue-components/vite'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
// 生成 public/models/manifest.json，自动列举 .onnx 文件
function modelsManifestPlugin(): Plugin {
  const writeManifest = () => {
    try {
      const modelsDir = resolve(__dirname, 'public/models')
      if (!fs.existsSync(modelsDir)) return
      const files = fs
        .readdirSync(modelsDir)
        .filter((f) => f.toLowerCase().endsWith('.onnx'))
      const manifestPath = resolve(modelsDir, 'manifest.json')
      fs.writeFileSync(manifestPath, JSON.stringify(files, null, 2))
      console.log(`📦 models manifest updated (${files.length}):`, files)
    } catch (e) {
      console.warn('⚠️ update models manifest failed:', (e as any)?.message)
    }
  }

  return {
    name: 'models-manifest',
    apply: 'serve',
    configureServer(server) {
      writeManifest()
      const dir = resolve(__dirname, 'public/models')
      try {
        if (fs.existsSync(dir)) {
          fs.watch(dir, { persistent: true }, (_event, filename) => {
            if (!filename) return
            if (filename.toLowerCase().endsWith('.onnx')) writeManifest()
          })
        }
      } catch {}
    },
    buildStart() {
      writeManifest()
    },
    closeBundle() {
      writeManifest()
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  const backendOrigin = apiBaseUrl.replace(/\/+$/, '')
  console.log('🔧 Vite配置 - mode:', mode)
  console.log('🔧 Vite配置 - apiBaseUrl:', apiBaseUrl)
  console.log('🔧 Vite配置 - backendOrigin:', backendOrigin)

  return {
  plugins: [
    vue(),
    modelsManifestPlugin(),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0', // 新增：允许所有网络接口访问
    port: 3001, // 明确设置为3001端口
    open: true,
    cors: true,
    proxy: {
      // RSS新闻代理转发到百度新闻（需要放在/api之前，优先匹配）
      '/api/rss': {
        target: 'https://news.baidu.com',
        changeOrigin: true,
        secure: true,
        timeout: 10000, // 设置10秒超时
        rewrite: (path) => {
          // 百度新闻RSS格式: /n?cmd=1&class=类别&tn=rss
          // 支持多种RSS路径
          if (path.includes('/world')) {
            return '/n?cmd=1&class=internet&tn=rss' // 国际新闻
          } else if (path.includes('/tech')) {
            return '/n?cmd=1&class=technic&tn=rss' // 科技新闻
          } else if (path.includes('/domestic')) {
            return '/n?cmd=1&class=civilnews&tn=rss' // 国内新闻
          } else if (path.includes('/finance')) {
            return '/n?cmd=1&class=finance&tn=rss' // 财经新闻
          }
          // 默认使用国内新闻
          return '/n?cmd=1&class=civilnews&tn=rss'
        },
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加必要的请求头，模拟浏览器请求
            proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            proxyReq.setHeader('Accept', 'application/xml, text/xml, */*')
            proxyReq.setHeader('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
            proxyReq.setHeader('Referer', 'https://news.baidu.com/')
            proxyReq.setHeader('Host', 'news.baidu.com')
            // 移除Origin，避免CORS问题
            proxyReq.removeHeader('Origin')
            if (process.env.NODE_ENV === 'development') {
              console.log(`📰 RSS代理请求: ${req.method} ${req.url} -> ${proxyReq.path}`)
            }
          })

          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 添加CORS头部
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
            res.setHeader('Access-Control-Expose-Headers', 'Content-Type')
            
            // 确保Content-Type正确
            if (proxyRes.headers['content-type']) {
              res.setHeader('Content-Type', proxyRes.headers['content-type'])
            } else {
              res.setHeader('Content-Type', 'application/xml; charset=utf-8')
            }
            
            if (process.env.NODE_ENV === 'development') {
              console.log(`✅ RSS响应: ${proxyRes.statusCode} ${req.url}`)
            }
          })

          proxy.on('error', (err, req, res) => {
            console.error('❌ RSS代理错误:', err.message)
          })
        },
      },
      // 翻译API代理转发到腾讯翻译（需要放在/api之前，优先匹配）
      '/api/translate': {
        target: 'https://fanyi.qq.com',
        changeOrigin: true,
        secure: true,
        timeout: 10000, // 设置10秒超时
        rewrite: (path) => {
          // 腾讯翻译接口路径是 /api/translate，需要保留所有查询参数
          const pathWithoutPrefix = path.replace(/^\/api\/translate/, '/api/translate')
          if (process.env.NODE_ENV === 'development') {
            console.log('翻译代理路径重写:', path, '->', pathWithoutPrefix)
          }
          return pathWithoutPrefix
        },
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加必要的请求头，模拟浏览器请求
            proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            proxyReq.setHeader('Accept', 'application/json, text/plain, */*')
            proxyReq.setHeader('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
            proxyReq.setHeader('Referer', 'https://fanyi.qq.com/')
            proxyReq.setHeader('Content-Type', 'application/json; charset=UTF-8')
            // 移除Origin，避免CORS问题
            if (proxyReq.getHeader('Origin')) {
              proxyReq.removeHeader('Origin')
            }
            if (process.env.NODE_ENV === 'development') {
              console.log(`🌐 翻译代理请求: ${req.method} ${req.url} -> ${proxyReq.path}`)
              console.log(`🌐 代理目标: https://fanyi.qq.com${proxyReq.path}`)
            }
          })

          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 添加CORS头部
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
            res.setHeader('Access-Control-Expose-Headers', 'Content-Type')
            
            // 确保Content-Type正确
            if (proxyRes.headers['content-type']) {
              res.setHeader('Content-Type', proxyRes.headers['content-type'])
            } else {
              res.setHeader('Content-Type', 'application/json; charset=utf-8')
            }
            
            if (process.env.NODE_ENV === 'development') {
              console.log(`✅ 翻译响应: ${proxyRes.statusCode} ${req.url}`)
              // 如果是错误状态码，记录详细信息
              if (proxyRes.statusCode >= 400) {
                console.error(`❌ 翻译API错误: ${proxyRes.statusCode} ${req.url}`)
              }
            }
          })

          proxy.on('error', (err, req, res) => {
            console.error('❌ 翻译代理错误:', err.message)
          })
        },
      },
      // 天气API代理转发到中国气象局（需要放在/api之前，优先匹配）
      '/api/weather': {
        target: 'https://weather.cma.cn',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api\/weather/, '/api/weather'),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加必要的请求头，模拟浏览器请求
            proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            proxyReq.setHeader('Accept', 'application/json, text/plain, */*')
            proxyReq.setHeader('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
            proxyReq.setHeader('Referer', 'https://weather.cma.cn/')
            proxyReq.setHeader('Origin', 'https://weather.cma.cn')
            proxyReq.setHeader('X-Proxy-By', 'Vite-Dev-Server')
            if (process.env.NODE_ENV === 'development') {
              console.log(`🌤️ 天气API代理: ${req.method} ${req.url}`)
            }
          })

          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 添加CORS头部
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
            if (process.env.NODE_ENV === 'development') {
              console.log(`✅ 天气API响应: ${proxyRes.statusCode} ${req.url}`)
            }
          })

          proxy.on('error', (err, req, res) => {
            console.error('❌ 天气API代理错误:', err.message)
          })
        },
      },
      // API代理转发到后端服务器
      '/api': {
        target: backendOrigin,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        // 优化Network面板显示
        // 保持原始头部信息
        preserveHeaderKeyCase: true,
        // 添加CORS头部，改善Network面板显示
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, Content-Length, X-Requested-With',
        },
        configure: (proxy, options) => {
          // 简化代理日志
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加标识头部，帮助Network面板识别
            proxyReq.setHeader('X-Proxy-By', 'Vite-Dev-Server')
            if (process.env.NODE_ENV === 'development') {
              console.log(`🔄 代理: ${req.method} ${req.url}`)
            }
          })

          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 添加响应头部，改善Network面板显示
            res.setHeader('X-Proxy-By', 'Vite-Dev-Server')
            res.setHeader('Access-Control-Allow-Origin', '*')
            if (process.env.NODE_ENV === 'development') {
              console.log(`✅ 响应: ${proxyRes.statusCode} ${req.url}`)
            }
          })

          proxy.on('error', (err, req, res) => {
            console.error('❌ 代理错误:', err.message)
          })
        },
      },
      // 媒体文件代理转发到后端服务器
      '/media': {
        target: backendOrigin,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/media/, '/media'),
        // 优化Network面板显示
        // 保持原始头部信息
        preserveHeaderKeyCase: true,
        // 添加CORS头部，改善Network面板显示
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, Content-Length, X-Requested-With',
        },
        configure: (proxy, options) => {
          // 简化代理日志
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加标识头部，帮助Network面板识别
            proxyReq.setHeader('X-Proxy-By', 'Vite-Dev-Server')
            if (process.env.NODE_ENV === 'development') {
              console.log(`🔄 媒体代理: ${req.method} ${req.url}`)
            }
          })

          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 添加响应头部，改善Network面板显示
            res.setHeader('X-Proxy-By', 'Vite-Dev-Server')
            res.setHeader('Access-Control-Allow-Origin', '*')
            if (process.env.NODE_ENV === 'development') {
              console.log(`✅ 媒体响应: ${proxyRes.statusCode} ${req.url}`)
            }
          })

          proxy.on('error', (err, req, res) => {
            console.error('❌ 媒体代理错误:', err.message)
          })
        },
      },
    },
  },
  define: {
    // 环境变量定义，确保在没有.env文件时也能正常工作
    __VITE_API_BASE_URL__: JSON.stringify(`${backendOrigin}/api`),
    __VITE_APP_TITLE__: JSON.stringify('Hertz Admin'),
    __VITE_APP_VERSION__: JSON.stringify('1.0.0'),
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          antd: ['ant-design-vue'],
          utils: ['axios', 'echarts'],
        },
      },
    },
  },
  }
})
