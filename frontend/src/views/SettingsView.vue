<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NInput, NTabs, NTabPane, NSpace, NText, useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import GlassCard from '../components/GlassCard.vue'
import AuthorDashboard from '../components/AuthorDashboard.vue'
import client from '../api/client'
import type { ApiResponse } from '../types/api'

const message = useMessage()
const auth = useAuthStore()

// 个人资料
const avatar = ref(auth.user?.avatar || '')
const bio = ref(auth.user?.bio || '')

async function saveProfile() {
  const { data } = await client.put<ApiResponse>('/users/me', { avatar: avatar.value, bio: bio.value })
  if (data.code === 0) {
    message.success('个人资料已更新')
    await auth.fetchUser()
  } else {
    message.error(data.message)
  }
}

// 修改密码
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

async function changePassword() {
  if (!oldPassword.value || !newPassword.value) {
    message.warning('请填写完整')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    message.warning('两次输入的新密码不一致')
    return
  }
  if (newPassword.value.length < 8) {
    message.warning('新密码长度至少 8 位')
    return
  }
  const { data } = await client.put<ApiResponse>('/auth/password', {
    old_password: oldPassword.value,
    new_password: newPassword.value,
  })
  if (data.code === 0) {
    message.success('密码修改成功，请重新登录')
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } else {
    message.error(data.message)
  }
}
</script>

<template>
  <div style="max-width: 600px; margin: 0 auto; padding-top: 24px;">
    <NText tag="h2" style="font-size: 24px; font-weight: 700; margin-bottom: 24px;">
      个人设置
    </NText>

    <NTabs type="line">
      <NTabPane tab="个人资料" name="profile">
        <GlassCard style="margin-top: 16px;">
          <NSpace vertical size="large" style="width: 100%;">
            <div>
              <NText depth="3" style="font-size: 13px; margin-bottom: 6px; display: block;">头像 URL</NText>
              <NInput v-model:value="avatar" placeholder="输入头像图片链接" />
            </div>
            <div>
              <NText depth="3" style="font-size: 13px; margin-bottom: 6px; display: block;">个人简介</NText>
              <NInput v-model:value="bio" type="textarea" :autosize="{ minRows: 3, maxRows: 6 }" placeholder="介绍一下自己..." maxlength="200" show-count />
            </div>
            <NButton type="primary" @click="saveProfile">保存</NButton>
          </NSpace>
        </GlassCard>
      </NTabPane>

      <NTabPane v-if="auth.isAuthor" tab="数据统计" name="stats">
        <GlassCard style="margin-top: 16px;">
          <AuthorDashboard />
        </GlassCard>
      </NTabPane>

      <NTabPane tab="修改密码" name="password">
        <GlassCard style="margin-top: 16px;">
          <NSpace vertical size="large" style="width: 100%;">
            <div>
              <NText depth="3" style="font-size: 13px; margin-bottom: 6px; display: block;">旧密码</NText>
              <NInput v-model:value="oldPassword" type="password" placeholder="输入旧密码" />
            </div>
            <div>
              <NText depth="3" style="font-size: 13px; margin-bottom: 6px; display: block;">新密码</NText>
              <NInput v-model:value="newPassword" type="password" placeholder="至少 8 位，包含字母和数字" />
            </div>
            <div>
              <NText depth="3" style="font-size: 13px; margin-bottom: 6px; display: block;">确认新密码</NText>
              <NInput v-model:value="confirmPassword" type="password" placeholder="再次输入新密码" />
            </div>
            <NButton type="primary" @click="changePassword">修改密码</NButton>
          </NSpace>
        </GlassCard>
      </NTabPane>
    </NTabs>
  </div>
</template>
