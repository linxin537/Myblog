<script setup lang="ts">
import { NH1, NP } from 'naive-ui'
import GlassCard from '../components/GlassCard.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 48px;">
    <GlassCard>
      <NH1 style="margin-bottom: 16px;">
        {{ auth.isLoggedIn ? `欢迎回来，${auth.user?.username}` : '欢迎来到博客' }}
      </NH1>
      <NP style="color: var(--text-secondary); font-size: 16px;">
        这是一个极简、聚焦写作的博客平台。
      </NP>
      <NP v-if="!auth.isLoggedIn" style="margin-top: 24px; color: var(--text-secondary);">
        请先<RouterLink to="/login">登录</RouterLink>以开始创作。
      </NP>
      <NP v-else style="margin-top: 24px; color: var(--text-secondary);">
        文章列表将在后续阶段实现。
      </NP>
    </GlassCard>
  </div>
</template>
