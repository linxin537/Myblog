<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NButton, NTag, NText, NSpace, NDataTable, NSelect, NInput,
  NModal, NForm, NFormItem, NPopconfirm, useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getUsers, updateUserRole, updateUserStatus, updateUser, deleteUser, type UserManageInfo } from '../../api/admin'
import { useAuthStore } from '../../stores/auth'
import { getIdenticonUrl } from '../../utils/identicon'

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

const roleLabels: Record<string, string> = {
  admin: '管理员',
  author: '作者',
  reader: '读者',
}

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

async function handleStatusToggle(userId: number, isActive: boolean) {
  const { data } = await updateUserStatus(userId, !isActive)
  if (data.code === 0) {
    message.success(!isActive ? '已启用' : '已禁用')
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
  {
    title: '', key: 'avatar', width: 44,
    render(row) {
      return h('img', {
        src: getIdenticonUrl(row.username, row.avatar, 28),
        style: { width: '28px', height: '28px', borderRadius: '50%', display: 'block' },
      })
    },
  },
  { title: 'ID', key: 'id', width: 50 },
  { title: '用户名', key: 'username', width: 110, ellipsis: { tooltip: true } },
  { title: '邮箱', key: 'email', width: 200, ellipsis: { tooltip: true } },
  {
    title: '角色', key: 'role', width: 130,
    render(row) {
      const isSelf = row.id === auth.user?.id
      if (isSelf) {
        return h(NTag, {
          size: 'small',
          bordered: false,
          style: {
            background: 'var(--color-surface-soft)',
            color: 'var(--color-muted)',
            borderRadius: '9999px',
            fontWeight: 500,
          },
        }, { default: () => roleLabels[row.role] || row.role })
      }
      return h(NSelect, {
        value: row.role,
        size: 'small',
        options: roleOptions,
        consistentMenuWidth: false,
        style: { width: '94px' },
        'onUpdate:value': (val: string) => handleRoleChange(row.id, val),
      })
    },
  },
  {
    title: '状态', key: 'is_active', width: 80,
    render(row) {
      const color = row.is_active ? '#22c55e' : '#d1d5db'
      const isSelf = row.id === auth.user?.id
      return h('div', {
        style: {
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          cursor: isSelf ? 'default' : 'pointer',
          opacity: isSelf ? '0.6' : '1',
        },
        onClick: () => {
          if (!isSelf) handleStatusToggle(row.id, row.is_active)
        },
      }, [
        h('span', {
          style: {
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: color,
            display: 'inline-block',
            flexShrink: 0,
            transition: 'background 0.2s ease',
          },
        }),
        h('span', { style: { fontSize: '13px', color: 'var(--color-muted)' } },
          row.is_active ? '正常' : '禁用'),
      ])
    },
  },
  { title: '登录失败', key: 'login_attempts', width: 70 },
  {
    title: '注册时间', key: 'created_at', width: 140,
    render(row) { return new Date(row.created_at).toLocaleDateString('zh-CN') },
  },
  {
    title: '操作', key: 'actions', width: 110,
    render(row) {
      return h(NSpace, { size: 8 }, () => [
        h(NButton, {
          text: true,
          size: 'small',
          style: { color: 'var(--color-primary)', fontWeight: 500 },
          onClick: () => openEditDialog(row),
        }, () => '编辑'),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row.id) },
          {
            default: () => '确定删除该用户？',
            trigger: () => h(NButton, {
              text: true,
              size: 'small',
              disabled: row.id === auth.user?.id,
              style: {
                color: 'var(--color-error)',
                fontWeight: 500,
              },
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
    <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700, marginBottom: '20px', display: 'block' }">用户管理</NText>

    <div :style="{ display: 'flex', gap: '12px', marginBottom: '16px' }">
      <NInput
        v-model:value="search"
        placeholder="搜索用户名或邮箱..."
        style="width: 240px;"
        clearable
        :style="{ '--n-border-radius': '8px' }"
        @clear="onSearch"
        @keyup.enter="onSearch"
      />
      <NSelect
        v-model:value="roleFilter"
        :options="roleOptions"
        placeholder="角色筛选"
        clearable
        style="width: 140px;"
        @update:value="onSearch"
      />
      <NButton
        type="primary"
        :style="{ borderRadius: '8px' }"
        @click="onSearch"
      >
        搜索
      </NButton>
    </div>

    <div class="card" :style="{ padding: '4px 0', overflow: 'hidden' }">
      <NDataTable
        :columns="columns"
        :data="users"
        :loading="loading"
        :pagination="{ page: page, pageSize: pageSize, itemCount: total, prefix: () => `共 ${total} 个用户` }"
        :row-key="(row: UserManageInfo) => row.id"
        @update:page="(p: number) => { page = p; load(); }"
        @update:page-size="(s: number) => { pageSize = s; load(); }"
      />
    </div>

    <!-- 编辑用户弹窗 -->
    <NModal v-model:show="showEditModal" title="编辑用户信息">
      <div
        class="card"
        :style="{ width: '420px', maxWidth: '90vw', padding: '24px' }"
      >
        <NForm label-placement="top">
          <NFormItem label="用户名">
            <NInput
              v-model:value="editForm.username"
              :style="{ '--n-border-radius': '8px' }"
            />
          </NFormItem>
          <NFormItem label="邮箱">
            <NInput
              v-model:value="editForm.email"
              :style="{ '--n-border-radius': '8px' }"
            />
          </NFormItem>
          <NFormItem label="简介">
            <NInput
              v-model:value="editForm.bio"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              :style="{ '--n-border-radius': '8px' }"
            />
          </NFormItem>
        </NForm>
        <NSpace justify="end" style="margin-top: 20px;">
          <NButton @click="showEditModal = false">取消</NButton>
          <NButton
            type="primary"
            :loading="editSaving"
            :style="{ borderRadius: '8px' }"
            @click="handleSaveEdit"
          >
            保存
          </NButton>
        </NSpace>
      </div>
    </NModal>
  </div>
</template>
