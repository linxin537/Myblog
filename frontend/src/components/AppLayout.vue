<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NText, NDropdown } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
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
</script>

<template>
  <NLayout style="min-height: 100vh">
    <NLayoutHeader
      class="glass-strong"
      style="padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; border-radius: 0;"
    >
      <NSpace align="center" :size="24">
        <NText strong style="font-size: 20px; cursor: pointer" @click="router.push('/')">
          Blog
        </NText>
        <NButton text @click="router.push('/')">首页</NButton>
        <NButton v-if="auth.isAuthor" text @click="router.push('/editor')">创作</NButton>
        <NButton v-if="auth.isAuthor" text @click="router.push('/drafts')">草稿</NButton>
        <NButton v-if="auth.isLoggedIn" text @click="router.push('/favorites')">收藏</NButton>
        <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
            <NButton text>管理</NButton>
          </NDropdown>
      </NSpace>

      <NSpace align="center" :size="12">
        <NButton quaternary circle @click="dark = !dark">
          <template #icon>
            <NIcon :component="dark ? Sunny : Moon" />
          </template>
        </NButton>

        <template v-if="auth.isLoggedIn">
          <NText>{{ auth.user?.username }}</NText>
          <NButton quaternary @click="router.push('/settings')">设置</NButton>
          <NButton quaternary @click="handleLogout">登出</NButton>
        </template>
        <template v-else>
          <NButton type="primary" @click="router.push('/login')">登录</NButton>
        </template>
      </NSpace>
    </NLayoutHeader>

    <NLayoutContent style="padding: 32px; max-width: 1200px; margin: 0 auto;">
      <slot />
    </NLayoutContent>
  </NLayout>
</template>
