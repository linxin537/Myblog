import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/article/:id',
      name: 'article-detail',
      component: () => import('../views/ArticleDetail.vue'),
    },
    {
      path: '/editor/:id?',
      name: 'editor',
      component: () => import('../views/ArticleEditor.vue'),
      meta: { requiresAuth: true, roles: ['author', 'admin'] },
    },
    {
      path: '/admin/categories',
      name: 'categories-manage',
      component: () => import('../views/admin/CategoryManage.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/admin/tags',
      name: 'tags-manage',
      component: () => import('../views/admin/TagManage.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/CategoryManage.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.user) {
    await auth.fetchUser()
  }

  if (to.meta.guest && auth.isLoggedIn) {
    return { name: 'home' }
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login' }
  }

  if (to.meta.roles && auth.user) {
    const allowed = to.meta.roles as string[]
    if (!allowed.includes(auth.user.role)) {
      return { name: 'home' }
    }
  }
})

export default router
