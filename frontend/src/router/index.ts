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
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true, roles: ['author', 'admin'] },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/HomeView.vue'),
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
