<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NText } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const auth = useAuthStore()

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
        <NButton v-if="auth.isAuthor" text @click="router.push('/dashboard')">创作</NButton>
        <NButton v-if="auth.isAdmin" text @click="router.push('/admin')">管理</NButton>
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
