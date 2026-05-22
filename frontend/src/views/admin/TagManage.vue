<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NDataTable, NModal, NForm, NFormItem, NInput, NPopconfirm, NSpace, NText, useMessage } from 'naive-ui'
import type { FormInst, DataTableColumn } from 'naive-ui'
import { getTags, createTag, updateTag, deleteTag } from '../../api/tags'
import type { TagInfo } from '../../types/api'

const message = useMessage()
const tags = ref<TagInfo[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingId = ref<number | null>(null)

const form = ref({ name: '' })
const formRef = ref<FormInst | null>(null)

const columns: DataTableColumn[] = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  {
    title: '操作', key: 'actions', width: 160,
    render(row: any) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'tiny', onClick: () => openEdit(row) }, { default: () => '编辑' }),
          h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, {
            trigger: () => h(NButton, { size: 'tiny', type: 'error', secondary: true }, { default: () => '删除' }),
            default: () => '确定删除此标签？',
          }),
        ],
      })
    },
  },
]

async function loadTags() {
  loading.value = true
  const { data } = await getTags()
  if (data.code === 0) tags.value = data.data || []
  loading.value = false
}

function openCreate() {
  editingId.value = null
  form.value = { name: '' }
  showModal.value = true
}

function openEdit(tag: TagInfo) {
  editingId.value = tag.id
  form.value = { name: tag.name }
  showModal.value = true
}

async function handleSave() {
  try {
    await formRef.value?.validate()
  } catch { return }

  if (editingId.value) {
    const { data } = await updateTag(editingId.value, { name: form.value.name })
    if (data.code === 0) { message.success('已更新'); showModal.value = false; loadTags() }
    else message.error(data.message)
  } else {
    const { data } = await createTag({ name: form.value.name })
    if (data.code === 0) { message.success('已创建'); showModal.value = false; loadTags() }
    else message.error(data.message)
  }
}

async function handleDelete(id: number) {
  const { data } = await deleteTag(id)
  if (data.code === 0) { message.success('已删除'); loadTags() }
  else message.error(data.message)
}

onMounted(loadTags)
</script>

<template>
  <div style="max-width: 600px; margin: 0 auto; padding-top: 24px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <NText tag="h2" strong>标签管理</NText>
      <NButton type="primary" @click="openCreate">新增标签</NButton>
    </div>

    <div class="glass" style="padding: 16px;">
      <NDataTable :columns="columns" :data="tags" :loading="loading" />
    </div>

    <NModal v-model:show="showModal" :title="editingId ? '编辑标签' : '新增标签'">
      <div class="glass" style="padding: 24px; width: 380px; max-width: 90vw;">
        <NForm ref="formRef" :model="form" label-placement="left">
          <NFormItem label="名称" path="name" :rule="{ required: true, message: '请输入标签名' }">
            <NInput v-model:value="form.name" />
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
