<template>
  <div class="home-container">
    <!-- 简约导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-text">
            <span class="brand-name ocean-gradient-text">智慧海洋生物识别系统</span>
          </div>
        </div>

        <nav class="navigation">
          <a href="#home" class="nav-link">首页</a>
          <a href="#about" class="nav-link">关于</a>
          <a href="#service" class="nav-link">服务</a>
          <a href="#contact" class="nav-link">联系</a>
        </nav>

        <div class="header-actions">
          <button class="btn-login" @click="goToLogin">登录</button>
        </div>
      </div>
    </header>

    <!-- 英雄区域 -->
    <section class="hero-section" id="home">
      <div class="hero-content">
        <h1 class="hero-title ocean-gradient-text">智慧海洋生物识别系统</h1>
        <p class="hero-description">智能海洋生物监测与识别平台</p>
        <div class="hero-actions">
          <button class="btn-primary" @click="goToLogin">开始使用</button>
          <button class="btn-secondary">了解更多</button>
        </div>
      </div>
    </section>

    <!-- 特性区域 -->
    <section class="features-section" id="service">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">核心特性</h2>
          <p class="section-subtitle">提供全方位的功能支持</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🐋</div>
            <h3 class="feature-title">海洋生物识别</h3>
            <p class="feature-description">基于深度学习的海洋生物智能识别</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">数据可视化</h3>
            <p class="feature-description">直观的图表展示，让数据一目了然</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🔐</div>
            <h3 class="feature-title">权限管理</h3>
            <p class="feature-description">完善的权限控制体系，保障系统安全</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3 class="feature-title">高性能</h3>
            <p class="feature-description">优化的架构设计，提供流畅的使用体验</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3 class="feature-title">响应式设计</h3>
            <p class="feature-description">完美适配各种设备，随时随地访问</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🔧</div>
            <h3 class="feature-title">易于扩展</h3>
            <p class="feature-description">模块化设计，轻松添加新功能</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 关于区域 -->
    <section class="about-section" id="about">
      <div class="container">
        <div class="about-content">
          <div class="about-text">
            <h2 class="about-title">关于系统</h2>
            <p class="about-description">
              智慧海洋生物识别系统是一个现代化的智能监测平台，
              采用最新的人工智能技术，帮助您快速识别和监测海洋生物。
            </p>
            <ul class="about-features">
              <li>基于 Vue 3 + TypeScript</li>
              <li>Ant Design Vue 组件库</li>
              <li>YOLO 目标检测技术</li>
              <li>完整的权限管理</li>
              <li>丰富的功能模块</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer" id="contact">
      <div class="container">
        <div class="footer-content">
          <div class="footer-info">
            <h3 class="footer-title">智慧海洋生物识别系统</h3>
            <p class="footer-description">智能海洋生物监测与识别平台</p>
          </div>
          <div class="footer-links">
            <div class="link-group">
              <h4>快速链接</h4>
              <ul>
                <li><a href="#" @click="goToLogin">登录系统</a></li>
                <li><a href="#about">关于我们</a></li>
                <li><a href="#service">功能介绍</a></li>
              </ul>
            </div>
            <div class="link-group">
              <h4>联系方式</h4>
              <ul>
                <li>邮箱：contact@ocean.com</li>
                <li>电话：+86 123-4567-8900</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 智慧海洋生物识别系统. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #000814 0%, #001d3d 30%, #003566 60%, #00509d 100%);
}

// 导航栏
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(0, 29, 61, 0.95);
  border-bottom: 2px solid rgba(0, 212, 255, 0.3);
  backdrop-filter: blur(15px);
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

.logo-section {
  .logo-text {
    .brand-name {
      font-size: 20px;
      font-weight: 600;
    }
  }
}

.navigation {
  display: flex;
  gap: 32px;

  .nav-link {
    color: #90e0ef;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s;
    text-shadow: 0 0 10px rgba(144, 224, 239, 0.5);

    &:hover {
      color: #00d4ff;
      text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
    }
  }
}

.header-actions {
  .btn-login {
    padding: 8px 20px;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(72, 202, 228, 0.2));
    border: 2px solid #00d4ff;
    border-radius: 16px;
    color: #00d4ff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.4s ease;
    letter-spacing: 2px;

    &:hover {
      background: linear-gradient(135deg, #00d4ff, #48cae4);
      border-color: transparent;
      color: #001d3d;
      box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
      transform: translateY(-2px);
    }
  }
}

// 英雄区域
.hero-section {
  padding: 160px 24px 120px;
  text-align: center;
  background: transparent;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 24px;
  line-height: 1.2;
}

.hero-description {
  font-size: 20px;
  color: #90e0ef;
  margin-bottom: 48px;
  line-height: 1.6;
  text-shadow: 0 0 10px rgba(144, 224, 239, 0.5);
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;

  .btn-primary {
    padding: 14px 32px;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(72, 202, 228, 0.2));
    border: 2px solid #00d4ff;
    border-radius: 16px;
    color: #00d4ff;
    font-size: 16px;
    font-weight: 900;
    cursor: pointer;
    transition: all 0.4s ease;
    letter-spacing: 4px;
    text-transform: uppercase;

    &:hover {
      background: linear-gradient(135deg, #00d4ff, #48cae4);
      border-color: transparent;
      color: #001d3d;
      box-shadow:
        0 0 50px rgba(0, 212, 255, 0.7),
        0 0 100px rgba(72, 202, 228, 0.4);
      transform: translateY(-4px) scale(1.02);
    }
  }

  .btn-secondary {
    padding: 14px 32px;
    background: transparent;
    border: 2px solid rgba(0, 212, 255, 0.4);
    border-radius: 16px;
    color: #90e0ef;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.4s ease;

    &:hover {
      border-color: #00d4ff;
      color: #00d4ff;
      background: rgba(0, 212, 255, 0.1);
      box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
      transform: translateY(-2px);
    }
  }
}

// 特性区域
.features-section {
  padding: 80px 24px;
  background: transparent;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: #caf0f8;
  margin-bottom: 16px;
  text-shadow: 0 0 20px rgba(202, 240, 248, 0.5);
}

.section-subtitle {
  font-size: 18px;
  color: #90e0ef;
  text-shadow: 0 0 10px rgba(144, 224, 239, 0.5);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}

.feature-card {
  background: rgba(0, 29, 61, 0.9);
  padding: 32px;
  border-radius: 24px;
  border: 2px solid rgba(0, 212, 255, 0.4);
  text-align: center;
  transition: all 0.4s ease;
  box-shadow:
    0 0 40px rgba(0, 212, 255, 0.2),
    inset 0 0 30px rgba(0, 212, 255, 0.05);

  &:hover {
    border-color: #00d4ff;
    box-shadow:
      0 0 60px rgba(0, 212, 255, 0.4),
      inset 0 0 40px rgba(0, 212, 255, 0.1);
    transform: translateY(-8px) scale(1.02);
  }
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: #caf0f8;
  margin-bottom: 12px;
  text-shadow: 0 0 10px rgba(202, 240, 248, 0.5);
}

.feature-description {
  font-size: 14px;
  color: #90e0ef;
  line-height: 1.6;
  text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
}

// 关于区域
.about-section {
  padding: 80px 24px;
  background: transparent;
}

.about-content {
  max-width: 800px;
  margin: 0 auto;
}

.about-text {
  text-align: center;
}

.about-title {
  font-size: 36px;
  font-weight: 700;
  color: #caf0f8;
  margin-bottom: 24px;
  text-shadow: 0 0 20px rgba(202, 240, 248, 0.5);
}

.about-description {
  font-size: 16px;
  color: #90e0ef;
  line-height: 1.8;
  margin-bottom: 32px;
  text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
}

.about-features {
  list-style: none;
  padding: 0;
  display: inline-block;
  text-align: left;

  li {
    padding: 8px 0;
    color: #caf0f8;
    font-size: 15px;
    text-shadow: 0 0 8px rgba(202, 240, 248, 0.5);

    &::before {
      content: '✓';
      color: #00d4ff;
      font-weight: bold;
      margin-right: 12px;
      text-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
    }
  }
}

// 页脚
.footer {
  background: rgba(0, 29, 61, 0.8);
  border-top: 2px solid rgba(0, 212, 255, 0.3);
  padding: 64px 24px 32px;
  backdrop-filter: blur(15px);
}

.footer-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  margin-bottom: 48px;
}

.footer-info {
  .footer-title {
    font-size: 20px;
    font-weight: 600;
    color: #caf0f8;
    margin-bottom: 12px;
    text-shadow: 0 0 15px rgba(202, 240, 248, 0.5);
  }

  .footer-description {
    color: #90e0ef;
    font-size: 14px;
    line-height: 1.6;
    text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
  }
}

.footer-links {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;

  .link-group {
    h4 {
      color: #caf0f8;
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      text-shadow: 0 0 10px rgba(202, 240, 248, 0.5);
    }

    ul {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        margin-bottom: 8px;
        font-size: 14px;
        color: #90e0ef;
        text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);

        a {
          color: #90e0ef;
          text-decoration: none;
          transition: color 0.2s;

          &:hover {
            color: #00d4ff;
            text-shadow: 0 0 15px rgba(0, 212, 255, 0.8);
          }
        }
      }
    }
  }
}

.footer-bottom {
  text-align: center;
  padding-top: 32px;
  border-top: 1px solid rgba(0, 212, 255, 0.3);

  p {
    color: #90e0ef;
    font-size: 14px;
    margin: 0;
    text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
  }
}

.ocean-gradient-text {
  background: linear-gradient(90deg, #00d4ff, #48cae4, #90e0ef, #caf0f8, #00d4ff);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: oceanGradient 5s ease infinite;
}

@keyframes oceanGradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
