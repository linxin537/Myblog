<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NText, NDataTable, NTag, NSelect } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getAuditLogs, type AuditLogInfo } from '../../api/admin'

const logs = ref<AuditLogInfo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
let pageSize = 20
const actionFilter = ref<string | null>(null)

const actionOptions = [
  { label: '登录', value: 'login' },
  { label: '创建文章', value: 'create_article' },
  { label: '删除文章', value: 'delete_article' },
  { label: '修改角色', value: 'update_role' },
  { label: '启用/禁用', value: 'toggle_user_status' },
  { label: '修改密码', value: 'change_password' },
  { label: '上传文件', value: 'upload_file' },
]

const actionLabels: Record<string, string> = {
  login: '登录', create_article: '创建文章', delete_article: '删除文章',
  update_role: '修改角色', toggle_user_status: '启用/禁用',
  change_password: '修改密码', upload_file: '上传文件',
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN')
}

async function load() {
  loading.value = true
  try {
    const { data } = await getAuditLogs({
      page: page.value, page_size: pageSize, action: actionFilter.value || undefined,
    })
    if (data.code === 0) {
      logs.value = (data.data || []) as AuditLogInfo[]
      total.value = data.pagination?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  load()
}

const columns: DataTableColumns<AuditLogInfo> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户', key: 'username', width: 100, render(row) { return row.username || '—' } },
  {
    title: '操作', key: 'action', width: 110,
    render(row) {
      const isDelete = row.action.includes('delete')
      return h(NTag, {
        size: 'small',
        bordered: false,
        style: {
          background: isDelete ? 'rgba(193,53,21,0.08)' : 'var(--color-surface-soft)',
          color: isDelete ? 'var(--color-error)' : 'var(--color-muted)',
          borderRadius: '9999px',
          fontWeight: 500,
        },
      }, { default: () => actionLabels[row.action] || row.action })
    },
  },
  { title: '目标', key: 'target_type', width: 80 },
  { title: '目标ID', key: 'target_id', width: 70 },
  { title: 'IP', key: 'ip_address', width: 130 },
  { title: '详情', key: 'detail', width: 160, ellipsis: { tooltip: true } },
  {
    title: '时间', key: 'created_at', width: 170,
    render(row) { return formatDate(row.created_at) },
  },
]

onMounted(load)
</script>

<template>
  <div style="max-width: 1200px; margin: 0 auto; padding-top: 24px;">
    <div :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }">
      <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700 }">审计日志</NText>
      <NSelect
        v-model:value="actionFilter"
        :options="actionOptions"
        placeholder="筛选操作类型"
        clearable
        style="width: 180px;"
        @update:value="onFilterChange"
      />
    </div>

    <div class="card" :style="{ padding: '4px 0', overflow: 'hidden' }">
      <NDataTable
        :columns="columns"
        :data="logs"
        :loading="loading"
        :pagination="{ page: page, pageSize: pageSize, itemCount: total }"
        :row-key="(row: AuditLogInfo) => row.id"
        @update:page="(p: number) => { page = p; load(); }"
        @update:page-size="(s: number) => { pageSize = s; load(); }"
        :scroll-x="1000"
      />
    </div>
  </div>
</template>
