<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { NButton, NInput, NTabs, NTabPane, NSpace, NText, useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import AuthorDashboard from '../components/AuthorDashboard.vue'
import client from '../api/client'
import type { ApiResponse } from '../types/api'
import gsap from 'gsap'

const message = useMessage()
const auth = useAuthStore()

// 个人资料
const avatar = ref(auth.user?.avatar || '')
const bio = ref(auth.user?.bio || '')

async function saveProfile() {
  const { data } = await client.put<ApiResponse>('/users/me', { avatar: avatar.value, bio: bio.value })
  if (data.code === 0) {
    message.success('个人资料已更新')
    nextTick(() => {
      const btn = document.querySelector('.save-btn') as HTMLElement
      if (btn) {
        gsap.fromTo(btn, { scale: 1 }, { scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: 'power2.out' })
      }
    })
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
    nextTick(() => {
      const btn = document.querySelector('.save-btn') as HTMLElement
      if (btn) {
        gsap.fromTo(btn, { scale: 1 }, { scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: 'power2.out' })
      }
    })
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
    <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700, marginBottom: '24px', display: 'block' }">
      个人设置
    </NText>

    <NTabs type="line">
      <NTabPane tab="个人资料" name="profile">
        <div class="card" :style="{ padding: '24px', marginTop: '16px' }">
          <NSpace vertical size="large" style="width: 100%;">
            <div>
              <NText :depth="3" :style="{ fontSize: '13px', marginBottom: '6px', display: 'block', color: 'var(--color-muted)' }">头像 URL</NText>
              <NInput
                v-model:value="avatar"
                placeholder="输入头像图片链接"
                :style="{ '--n-border-radius': '8px' }"
              />
            </div>
            <div>
              <NText :depth="3" :style="{ fontSize: '13px', marginBottom: '6px', display: 'block', color: 'var(--color-muted)' }">个人简介</NText>
              <NInput
                v-model:value="bio"
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 6 }"
                placeholder="介绍一下自己..."
                maxlength="200"
                show-count
                :style="{ '--n-border-radius': '8px' }"
              />
            </div>
            <NButton
              type="primary"
              class="save-btn"
              :style="{ borderRadius: '8px', height: '40px' }"
              @click="saveProfile"
            >
              保存
            </NButton>
          </NSpace>
        </div>
      </NTabPane>

      <NTabPane v-if="auth.isAuthor" tab="数据统计" name="stats">
        <div class="card" :style="{ padding: '24px', marginTop: '16px' }">
          <AuthorDashboard />
        </div>
      </NTabPane>

      <NTabPane tab="修改密码" name="password">
        <div class="card" :style="{ padding: '24px', marginTop: '16px' }">
          <NSpace vertical size="large" style="width: 100%;">
            <div>
              <NText :depth="3" :style="{ fontSize: '13px', marginBottom: '6px', display: 'block', color: 'var(--color-muted)' }">旧密码</NText>
              <NInput
                v-model:value="oldPassword"
                type="password"
                placeholder="输入旧密码"
                :style="{ '--n-border-radius': '8px' }"
              />
            </div>
            <div>
              <NText :depth="3" :style="{ fontSize: '13px', marginBottom: '6px', display: 'block', color: 'var(--color-muted)' }">新密码</NText>
              <NInput
                v-model:value="newPassword"
                type="password"
                placeholder="至少 8 位，包含字母和数字"
                :style="{ '--n-border-radius': '8px' }"
              />
            </div>
            <div>
              <NText :depth="3" :style="{ fontSize: '13px', marginBottom: '6px', display: 'block', color: 'var(--color-muted)' }">确认新密码</NText>
              <NInput
                v-model:value="confirmPassword"
                type="password"
                placeholder="再次输入新密码"
                :style="{ '--n-border-radius': '8px' }"
              />
            </div>
            <NButton
              type="primary"
              class="save-btn"
              :style="{ borderRadius: '8px', height: '40px' }"
              @click="changePassword"
            >
              修改密码
            </NButton>
          </NSpace>
        </div>
      </NTabPane>
    </NTabs>
  </div>
</template>
