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
      path: '/favorites',
      name: 'favorites',
      component: () => import('../views/FavoritesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/user/:username',
      name: 'user-profile',
      component: () => import('../views/ProfileView.vue'),
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
      path: '/admin/users',
      name: 'user-manage',
      component: () => import('../views/admin/UserManage.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/admin/audit-logs',
      name: 'audit-logs',
      component: () => import('../views/admin/AuditLogs.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/CategoryManage.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/drafts',
      name: 'drafts',
      component: () => import('../views/DraftsView.vue'),
      meta: { requiresAuth: true, roles: ['author', 'admin'] },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
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
