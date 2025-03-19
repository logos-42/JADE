import { createRouter, createWebHistory } from 'vue-router';

// 懒加载各视图组件
const Home = () => import('../views/Home.vue');
const AgentsList = () => import('../views/AgentsList.vue');
const AgentDetail = () => import('../views/AgentDetail.vue');
const AgentRegister = () => import('../views/AgentRegister.vue');
const AgentDialog = () => import('../views/AgentDialog.vue');
const MarketPlace = () => import('../views/MarketPlace.vue');
const NotFound = () => import('../views/NotFound.vue');

// 路由定义
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - JADE'
    }
  },
  {
    path: '/agents',
    name: 'AgentsList',
    component: AgentsList,
    meta: {
      title: '智能体列表 - JADE'
    }
  },
  {
    path: '/market',
    name: 'MarketPlace',
    component: MarketPlace,
    meta: {
      title: '智能体市场 - JADE'
    }
  },
  {
    path: '/agent/create',
    name: 'AgentRegister',
    component: AgentRegister,
    meta: {
      title: '创建智能体 - JADE'
    }
  },
  {
    path: '/agent/:id',
    name: 'AgentDetail',
    component: AgentDetail,
    props: true,
    meta: {
      title: '智能体详情 - JADE'
    }
  },
  {
    path: '/dialog/:id',
    name: 'AgentDialog',
    component: AgentDialog,
    props: true,
    meta: {
      title: '智能体对话 - JADE'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '页面未找到 - JADE'
    }
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// 全局前置守卫，用于修改页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
});

export default router; 