<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NDataTable, NModal, NForm, NFormItem, NInput, NInputNumber, NPopconfirm, NSpace, NText, useMessage } from 'naive-ui'
import type { FormInst, DataTableColumn } from 'naive-ui'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../../api/categories'
import type { CategoryInfo } from '../../types/api'

const message = useMessage()
const categories = ref<CategoryInfo[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingId = ref<number | null>(null)

const form = ref({ name: '', description: '', sort_order: 0 })
const formRef = ref<FormInst | null>(null)

const columns: DataTableColumn[] = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '描述', key: 'description' },
  { title: '排序', key: 'sort_order', width: 80 },
  {
    title: '操作', key: 'actions', width: 160,
    render(row: any) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'tiny', onClick: () => openEdit(row) }, { default: () => '编辑' }),
          h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, {
            trigger: () => h(NButton, { size: 'tiny', type: 'error', secondary: true }, { default: () => '删除' }),
            default: () => '确定删除此分类？',
          }),
        ],
      })
    },
  },
]

async function loadCategories() {
  loading.value = true
  const { data } = await getCategories()
  if (data.code === 0) categories.value = data.data || []
  loading.value = false
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: '', sort_order: 0 }
  showModal.value = true
}

function openEdit(cat: CategoryInfo) {
  editingId.value = cat.id
  form.value = { name: cat.name, description: cat.description || '', sort_order: cat.sort_order }
  showModal.value = true
}

async function handleSave() {
  try {
    await formRef.value?.validate()
  } catch { return }

  const payload = { ...form.value }

  if (editingId.value) {
    const { data } = await updateCategory(editingId.value, payload)
    if (data.code === 0) { message.success('已更新'); showModal.value = false; loadCategories() }
    else message.error(data.message)
  } else {
    const { data } = await createCategory(payload)
    if (data.code === 0) { message.success('已创建'); showModal.value = false; loadCategories() }
    else message.error(data.message)
  }
}

async function handleDelete(id: number) {
  const { data } = await deleteCategory(id)
  if (data.code === 0) { message.success('已删除'); loadCategories() }
  else message.error(data.message)
}

onMounted(loadCategories)
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <NText tag="h2" strong>分类管理</NText>
      <NButton type="primary" @click="openCreate">新增分类</NButton>
    </div>

    <div class="glass" style="padding: 16px;">
      <NDataTable :columns="columns" :data="categories" :loading="loading" />
    </div>

    <NModal v-model:show="showModal" :title="editingId ? '编辑分类' : '新增分类'">
      <div class="glass" style="padding: 24px; width: 420px; max-width: 90vw;">
        <NForm ref="formRef" :model="form" label-placement="left">
          <NFormItem label="名称" path="name" :rule="{ required: true, message: '请输入分类名' }">
            <NInput v-model:value="form.name" />
          </NFormItem>
          <NFormItem label="描述" path="description">
            <NInput v-model:value="form.description" type="textarea" />
          </NFormItem>
          <NFormItem label="排序" path="sort_order">
            <NInputNumber v-model:value="form.sort_order" />
          </NFormItem>
        </NForm>
        <NSpace justify="end" style="margin-top: 16px;">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" @click="handleSave">保存</NButton>
        </NSpace>
      </div>
    </NModal>
  </div>
</template>
