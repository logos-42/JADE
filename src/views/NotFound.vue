<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面未找到</p>
    <router-link to="/" class="home-btn">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 2rem;
}

h1 {
  font-size: 6rem;
  color: #00ff00;
  text-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
  margin: 0;
  line-height: 1;
}

p {
  font-size: 1.5rem;
  color: #fff;
  margin: 1rem 0 2rem;
}

.home-btn {
  padding: 0.8rem 1.5rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid #00ff00;
  color: #00ff00;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.home-btn:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
}
</style> 