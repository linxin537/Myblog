<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NText, NDropdown } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

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
        height: '80px',
        background: 'var(--color-canvas)',
        borderBottom: '1px solid var(--color-hairline-soft)',
        transition: 'background 0.3s ease, border-color 0.3s ease',
      }"
    >
      <!-- Logo -->
      <NText
        strong
        :style="{
          fontSize: '20px',
          cursor: 'pointer',
          fontWeight: 700,
          color: 'var(--color-primary)',
          letterSpacing: '-0.3px',
        }"
        @click="router.push('/')"
      >
        Blog
      </NText>

      <!-- Center Nav -->
      <NSpace align="center" :size="32">
        <NButton
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/') && route.path === '/' ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/') && route.path === '/' ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: '0',
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/')"
        >
          首页
        </NButton>
        <NButton
          v-if="auth.isAuthor"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/editor') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/editor') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: '0',
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/editor')"
        >
          创作
        </NButton>
        <NButton
          v-if="auth.isAuthor"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/drafts') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/drafts') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: '0',
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/drafts')"
        >
          草稿
        </NButton>
        <NButton
          v-if="auth.isLoggedIn"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/favorites') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/favorites') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: '0',
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/favorites')"
        >
          收藏
        </NButton>
        <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
          <NButton
            text
            :style="{ fontSize: '14px', fontWeight: 600, color: 'var(--color-muted)', height: 'auto' }"
          >
            管理
          </NButton>
        </NDropdown>
      </NSpace>

      <!-- Right Utils -->
      <NSpace align="center" :size="12">
        <NButton quaternary circle @click="dark = !dark">
          <template #icon>
            <NIcon :component="dark ? Sunny : Moon" />
          </template>
        </NButton>

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
