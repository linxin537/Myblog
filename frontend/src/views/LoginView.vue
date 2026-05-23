<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NCheckbox } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../api/client'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const activeTab = ref('login')
const isLogin = computed(() => activeTab.value === 'login')
const loading = ref(false)
const lockCountdown = ref(0)
let lockTimer: ReturnType<typeof setInterval> | null = null

const loginForm = ref({ username: '', password: '', rememberMe: false })
const registerForm = ref({ username: '', email: '', password: '', confirmPassword: '' })

const loginRef = ref<FormInst | null>(null)
const registerRef = ref<FormInst | null>(null)

const loginRules: FormRules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度 3-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value: string) => value === registerForm.value.password,
      message: '两次输入的密码不一致',
      trigger: 'blur',
    },
  ],
}

const lockText = computed(() => lockCountdown.value > 0 ? `账户已锁定，${lockCountdown.value}秒后重试` : '')

function startLockCountdown(seconds: number) {
  lockCountdown.value = seconds
  if (lockTimer) clearInterval(lockTimer)
  lockTimer = setInterval(() => {
    lockCountdown.value--
    if (lockCountdown.value <= 0) {
      clearInterval(lockTimer!)
      lockTimer = null
    }
  }, 1000)
}

async function handleLogin() {
  try {
    await loginRef.value?.validate()
  } catch { return }

  loading.value = true
  try {
    const result = await auth.login(loginForm.value.username, loginForm.value.password, loginForm.value.rememberMe)
    if (result.code === 0) {
      message.success('登录成功')
      router.push('/')
    } else {
      message.error(result.message)
      if (result.code === 2004) {
        startLockCountdown(900)
      }
    }
  } catch (e) {
    message.error(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  try {
    await registerRef.value?.validate()
  } catch { return }

  loading.value = true
  try {
    const result = await auth.register(
      registerForm.value.username,
      registerForm.value.email,
      registerForm.value.password,
    )
    if (result.code === 0) {
      message.success('注册成功，请登录')
      activeTab.value = 'login'
      loginForm.value.username = registerForm.value.username
    } else {
      message.error(result.message)
    }
  } catch (e) {
    message.error(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 360px; margin: 0 auto; padding: 80px 0;">
    <!-- 标题 -->
    <div style="font-size: 24px; font-weight: 700; color: var(--n-text-color); margin-bottom: 8px;">
      {{ isLogin ? '登录' : '注册' }}
    </div>
    <!-- 副标题 -->
    <div style="font-size: 14px; color: var(--n-text-color-3); margin-bottom: 32px;">
      {{ isLogin ? '欢迎回来，请登录你的账户' : '创建新账户，开始你的旅程' }}
    </div>

    <!-- 登录表单 -->
    <template v-if="isLogin">
      <NForm ref="loginRef" :model="loginForm" :rules="loginRules" label-placement="top">
        <NFormItem label="用户名" path="username">
          <NInput
            v-model:value="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NFormItem label="密码" path="password">
          <NInput
            v-model:value="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password-on="click"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NFormItem>
          <NCheckbox v-model:checked="loginForm.rememberMe">记住我</NCheckbox>
        </NFormItem>
        <NButton
          type="primary"
          block
          size="large"
          :loading="loading"
          :disabled="lockCountdown > 0"
          :style="{ borderRadius: '8px', height: '48px' }"
          @click="handleLogin"
        >
          {{ lockText || '登录' }}
        </NButton>
      </NForm>
    </template>

    <!-- 注册表单 -->
    <template v-else>
      <NForm ref="registerRef" :model="registerForm" :rules="registerRules" label-placement="top">
        <NFormItem label="用户名" path="username">
          <NInput
            v-model:value="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NFormItem label="邮箱" path="email">
          <NInput
            v-model:value="registerForm.email"
            placeholder="请输入邮箱"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NFormItem label="密码" path="password">
          <NInput
            v-model:value="registerForm.password"
            type="password"
            placeholder="至少8位，含字母和数字"
            show-password-on="click"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NFormItem label="确认密码" path="confirmPassword">
          <NInput
            v-model:value="registerForm.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            show-password-on="click"
            size="large"
            :style="{ '--n-border-radius': '8px' }"
          />
        </NFormItem>
        <NButton
          type="primary"
          block
          size="large"
          :loading="loading"
          :style="{ borderRadius: '8px', height: '48px' }"
          @click="handleRegister"
        >
          注册
        </NButton>
      </NForm>
    </template>

    <!-- 切换登录/注册 -->
    <div style="text-align: center; margin-top: 16px;">
      <NButton text type="primary" @click="activeTab = isLogin ? 'register' : 'login'">
        {{ isLogin ? '还没有账户？注册' : '已有账户？登录' }}
      </NButton>
    </div>
  </div>
</template>
