<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NText, NDropdown } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import { onMounted, ref } from 'vue'
import NotificationBell from './NotificationBell.vue'
import { useNotificationStore } from '../stores/notification'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifStore = useNotificationStore()
notifStore.startPolling()

const headerScrolled = ref(false)

onMounted(() => {
  ScrollTrigger.create({
    start: 'top -50',
    end: 'max',
    onEnter: () => { headerScrolled.value = true },
    onLeaveBack: () => { headerScrolled.value = false },
  })
})

const adminOptions = [
  { label: '分类管理', key: 'categories' },
  { label: '标签管理', key: 'tags' },
  { label: '用户管理', key: 'users' },
  { type: 'divider' as const, key: 'd1' },
  { label: '审计日志', key: 'audit-logs' },
]

function handleAdminSelect(key: string) {
  router.push(`/admin/${key}`)
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <NLayout :style="{ minHeight: '100vh', background: 'var(--color-canvas)' }">
    <NLayoutHeader
      :style="{
        padding: '0 40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: headerScrolled ? '56px' : '80px',
        background: headerScrolled
          ? 'color-mix(in srgb, var(--color-canvas) 85%, transparent)'
          : 'var(--color-canvas)',
        borderBottom: '1px solid var(--color-hairline-soft)',
        transition: 'height 0.3s ease, background 0.3s ease',
        backdropFilter: headerScrolled ? 'blur(12px)' : 'none',
        WebkitBackdropFilter: headerScrolled ? 'blur(12px)' : 'none',
      }"
    >
      <!-- Logo -->
      <NText
        strong
        :style="{
          fontSize: headerScrolled ? '18px' : '20px',
          cursor: 'pointer',
          fontWeight: 700,
          color: 'var(--color-primary)',
          letterSpacing: '-0.3px',
          transition: 'font-size 0.3s ease',
        }"
        @click="router.push('/')"
      >
        Blog
      </NText>

      <!-- Center Nav -->
      <NSpace align="center" :size="32">
        <div
          class="nav-item"
          :class="{ active: isActive('/') && route.path === '/' }"
          @click="router.push('/')"
        >
          首页
        </div>
        <div
          v-if="auth.isAuthor"
          class="nav-item"
          :class="{ active: isActive('/editor') }"
          @click="router.push('/editor')"
        >
          创作
        </div>
        <div
          v-if="auth.isAuthor"
          class="nav-item"
          :class="{ active: isActive('/drafts') }"
          @click="router.push('/drafts')"
        >
          草稿
        </div>
        <div
          v-if="auth.isLoggedIn"
          class="nav-item"
          :class="{ active: isActive('/favorites') }"
          @click="router.push('/favorites')"
        >
          收藏
        </div>
        <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
          <div class="nav-item">
            管理
          </div>
        </NDropdown>
      </NSpace>

      <!-- Right Utils -->
      <NSpace align="center" :size="12">
        <NButton quaternary circle @click="dark = !dark">
          <template #icon>
            <NIcon :component="dark ? Sunny : Moon" />
          </template>
        </NButton>

        <NotificationBell v-if="auth.isLoggedIn" />

        <template v-if="auth.isLoggedIn">
          <NButton text :style="{ fontSize: '13px', color: 'var(--color-muted)' }" @click="router.push('/settings')">
            {{ auth.user?.username }}
          </NButton>
          <NButton
            size="small"
            :style="{
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--color-ink)',
              border: '1px solid var(--color-ink)',
              borderRadius: '8px',
            }"
            @click="handleLogout"
          >
            登出
          </NButton>
        </template>
        <template v-else>
          <NButton
            size="small"
            type="primary"
            :style="{ borderRadius: '8px', fontWeight: 500 }"
            @click="router.push('/login')"
          >
            登录
          </NButton>
        </template>
      </NSpace>
    </NLayoutHeader>

    <NLayoutContent :style="{ maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '32px' }">
      <slot />
    </NLayoutContent>
  </NLayout>
</template>

<style scoped>
.nav-item {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-muted);
  cursor: pointer;
  padding: 0 0 4px;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease, border-color 0.2s ease;
  user-select: none;
  line-height: 1.4;
}

.nav-item:hover {
  color: var(--color-ink);
}

.nav-item.active {
  color: var(--color-ink);
  border-bottom-color: var(--color-ink);
}
</style>
