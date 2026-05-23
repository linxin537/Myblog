<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NButton, NTag, NText, NSpace, NDataTable, NSelect, NSwitch, NInput,
  NModal, NForm, NFormItem, NPopconfirm, useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getUsers, updateUserRole, updateUserStatus, updateUser, deleteUser, type UserManageInfo } from '../../api/admin'
import { useAuthStore } from '../../stores/auth'

const message = useMessage()
const auth = useAuthStore()

const users = ref<UserManageInfo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 10
const search = ref('')
const roleFilter = ref<string | null>(null)

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '作者', value: 'author' },
  { label: '读者', value: 'reader' },
]

// Edit dialog
const showEditModal = ref(false)
const editingUser = ref<UserManageInfo | null>(null)
const editForm = ref({ username: '', email: '', bio: '' })
const editSaving = ref(false)

function openEditDialog(user: UserManageInfo) {
  editingUser.value = user
  editForm.value = { username: user.username, email: user.email, bio: user.bio || '' }
  showEditModal.value = true
}

async function handleSaveEdit() {
  if (!editingUser.value) return
  editSaving.value = true
  try {
    const { data } = await updateUser(editingUser.value.id, {
      username: editForm.value.username,
      email: editForm.value.email,
      bio: editForm.value.bio || undefined,
    })
    if (data.code === 0) {
      message.success('用户信息已更新')
      showEditModal.value = false
      load()
    } else {
      message.error(data.message)
    }
  } finally {
    editSaving.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await getUsers({
      page: page.value, page_size: pageSize, search: search.value || undefined, role: roleFilter.value || undefined,
    })
    if (data.code === 0) {
      users.value = (data.data || []) as UserManageInfo[]
      total.value = data.pagination?.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function handleRoleChange(userId: number, newRole: string) {
  const { data } = await updateUserRole(userId, newRole)
  if (data.code === 0) {
    message.success('角色已更新')
    load()
  } else {
    message.error(data.message)
  }
}

async function handleStatusChange(userId: number, isActive: boolean) {
  const { data } = await updateUserStatus(userId, isActive)
  if (data.code === 0) {
    message.success(isActive ? '已启用' : '已禁用')
    load()
  } else {
    message.error(data.message)
  }
}

async function handleDelete(userId: number) {
  const { data } = await deleteUser(userId)
  if (data.code === 0) {
    message.success('用户已删除')
    load()
  } else {
    message.error(data.message)
  }
}

const columns: DataTableColumns<UserManageInfo> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户名', key: 'username', width: 120 },
  { title: '邮箱', key: 'email', width: 200, ellipsis: { tooltip: true } },
  {
    title: '角色', key: 'role', width: 150,
    render(row) {
      if (row.id === auth.user?.id) {
        return h(NTag, { type: 'info', size: 'small', round: true }, { default: () => row.role })
      }
      return h(NSelect, {
        value: row.role, size: 'small', options: roleOptions, consistentMenuWidth: false,
        style: { width: '100px' },
        'onUpdate:value': (val: string) => handleRoleChange(row.id, val),
      })
    },
  },
  {
    title: '状态', key: 'is_active', width: 90,
    render(row) {
      return h(NSwitch, {
        value: row.is_active, size: 'small',
        disabled: row.id === auth.user?.id,
        'onUpdate:value': (val: boolean) => handleStatusChange(row.id, val),
      })
    },
  },
  { title: '登录失败', key: 'login_attempts', width: 80 },
  {
    title: '注册时间', key: 'created_at', width: 160,
    render(row) { return new Date(row.created_at).toLocaleDateString('zh-CN') },
  },
  {
    title: '操作', key: 'actions', width: 140,
    render(row) {
      return h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', onClick: () => openEditDialog(row) }, () => '编辑'),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row.id) },
          {
            default: () => '确定删除该用户？',
            trigger: () => h(NButton, {
              size: 'small', type: 'error', secondary: true,
              disabled: row.id === auth.user?.id,
            }, () => '删除'),
          },
        ),
      ])
    },
  },
]

function onSearch() {
  page.value = 1
  load()
}

onMounted(load)
</script>

<template>
  <div style="max-width: 1100px; margin: 0 auto; padding-top: 24px;">
    <NText tag="h2" style="font-size: 24px; font-weight: 700; margin-bottom: 20px;">用户管理</NText>

    <div style="display: flex; gap: 12px; margin-bottom: 16px;">
      <NInput v-model:value="search" placeholder="搜索用户名或邮箱..." style="width: 240px;" clearable @clear="onSearch" @keyup.enter="onSearch" />
      <NSelect v-model:value="roleFilter" :options="roleOptions" placeholder="角色筛选" clearable style="width: 140px;" @update:value="onSearch" />
      <NButton type="primary" @click="onSearch">搜索</NButton>
    </div>

    <NDataTable
      :columns="columns"
      :data="users"
      :loading="loading"
      :pagination="{ page: page, pageSize: pageSize, itemCount: total, prefix: () => `共 ${total} 个用户` }"
      :row-key="(row: UserManageInfo) => row.id"
      @update:page="(p: number) => { page = p; load(); }"
      @update:page-size="(s: number) => { pageSize = s; load(); }"
    />

    <!-- 编辑用户弹窗 -->
    <NModal v-model:show="showEditModal" title="编辑用户信息">
      <div style="width: 420px; max-width: 90vw; padding: 24px;">
        <NForm label-placement="top">
          <NFormItem label="用户名">
            <NInput v-model:value="editForm.username" />
          </NFormItem>
          <NFormItem label="邮箱">
            <NInput v-model:value="editForm.email" />
          </NFormItem>
          <NFormItem label="简介">
            <NInput v-model:value="editForm.bio" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
          </NFormItem>
        </NForm>
        <NSpace justify="end" style="margin-top: 20px;">
          <NButton @click="showEditModal = false">取消</NButton>
          <NButton type="primary" :loading="editSaving" @click="handleSaveEdit">保存</NButton>
        </NSpace>
      </div>
    </NModal>
  </div>
</template>
