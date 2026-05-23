<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NText, NResult, useMessage } from 'naive-ui'
import { forgotPassword, resetPassword } from '../api/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const token = ref(route.query.token as string || '')
const email = ref('')
const newPassword = ref('')
const sent = ref(false)
const done = ref(false)
const submitting = ref(false)

async function handleForgot() {
  submitting.value = true
  try {
    const res = await forgotPassword(email.value)
    if (res.data.code === 0) sent.value = true
  } catch {
    // ignore
  }
  submitting.value = false
}

async function handleReset() {
  submitting.value = true
  try {
    const res = await resetPassword(token.value, newPassword.value)
    if (res.data.code === 0) {
      done.value = true
      message.success('密码已重置，请重新登录')
    } else {
      message.error(res.data.message || '重置失败')
    }
  } catch {
    message.error('网络错误')
  }
  submitting.value = false
}
</script>

<template>
  <div :style="{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-canvas)' }">
    <div :style="{ width: '380px', padding: '40px', background: 'var(--color-canvas)', borderRadius: '14px', border: '1px solid var(--color-hairline-soft)', boxShadow: 'var(--shadow-card)' }">
      <!-- Done state -->
      <NResult
        v-if="done"
        status="success"
        title="密码重置成功"
        description="请使用新密码登录"
      >
        <template #footer>
          <NButton type="primary" @click="router.push('/login')" :style="{ borderRadius: '8px' }">
            前往登录
          </NButton>
        </template>
      </NResult>

      <!-- Token mode: reset password -->
      <template v-else-if="token">
        <NText strong :style="{ fontSize: '22px', display: 'block', marginBottom: '24px' }">设置新密码</NText>
        <NForm>
          <NFormItem label="新密码">
            <NInput
              v-model:value="newPassword"
              type="password"
              placeholder="至少 6 位"
              :style="{ borderRadius: '8px' }"
            />
          </NFormItem>
          <NButton
            type="primary"
            block
            :loading="submitting"
            :disabled="newPassword.length < 6"
            @click="handleReset"
            :style="{ borderRadius: '8px' }"
          >
            重置密码
          </NButton>
        </NForm>
      </template>

      <!-- Email mode: request reset -->
      <template v-else-if="!sent">
        <NText strong :style="{ fontSize: '22px', display: 'block', marginBottom: '24px' }">忘记密码</NText>
        <NForm>
          <NFormItem label="注册邮箱">
            <NInput
              v-model:value="email"
              placeholder="请输入注册邮箱"
              :style="{ borderRadius: '8px' }"
            />
          </NFormItem>
          <NButton
            type="primary"
            block
            :loading="submitting"
            :disabled="!email"
            @click="handleForgot"
            :style="{ borderRadius: '8px' }"
          >
            发送重置链接
          </NButton>
        </NForm>
      </template>

      <!-- Sent state -->
      <template v-else>
        <NText strong :style="{ fontSize: '18px', display: 'block', marginBottom: '16px', textAlign: 'center' }">请检查控制台日志</NText>
        <NText depth="3" :style="{ textAlign: 'center', display: 'block', marginBottom: '24px' }">
          开发模式下，重置链接已打印到后端控制台。请复制链接在浏览器中打开。
        </NText>
        <NButton block @click="router.push('/login')" :style="{ borderRadius: '8px' }">
          返回登录
        </NButton>
      </template>
    </div>
  </div>
</template>
