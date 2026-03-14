<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>{{ $t('error.404') }}</h2>
      <p>抱歉，您访问的页面不存在</p>
      <router-link to="/" class="back-home-btn"> 返回首页 </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404页面不需要额外的逻辑
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.not-found-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.not-found-content h1 {
  font-size: 72px;
  margin: 0;
  color: #1890ff;
}

.not-found-content h2 {
  font-size: 24px;
  margin: 16px 0;
  color: #333;
}

.not-found-content p {
  color: #666;
  margin-bottom: 24px;
}

.back-home-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.back-home-btn:hover {
  background: #40a9ff;
}
</style>
