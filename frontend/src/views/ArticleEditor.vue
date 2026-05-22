<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NInput, NSelect, NButton, NTag, NSpace, NSpin, NText,
  NSwitch, NModal, useMessage, useDialog,
} from 'naive-ui'
import MarkdownEditor from '../components/MarkdownEditor.vue'
import ImageUpload from '../components/ImageUpload.vue'
import { useAuthStore } from '../stores/auth'
import { getArticle, createArticle, updateArticle } from '../api/articles'
import { getCategories } from '../api/categories'
import { getTags, createTag } from '../api/tags'
import { uploadFile } from '../api/files'
import { useDraftSave } from '../composables/useDraftSave'
import type { ArticleDetail, CategoryInfo, TagInfo } from '../types/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const auth = useAuthStore()
const { loadDraft, saveDraft, flushDraft, clearDraft, hasDraft } = useDraftSave()

const articleId = route.params.id ? Number(route.params.id) : null
const isEditing = !!articleId

const title = ref('')
const content = ref('')
const summary = ref('')
const coverImage = ref('')
const categoryId = ref<number | null>(null)
const tagIds = ref<number[]>([])
const isDraft = ref(true)
const isPinned = ref(false)

const categories = ref<CategoryInfo[]>([])
const tags = ref<TagInfo[]>([])
const loading = ref(false)
const saving = ref(false)
const showImageUpload = ref(false)
const lastSaved = ref('')

async function loadCategoriesAndTags() {
  const [catRes, tagRes] = await Promise.all([getCategories(), getTags()])
  if (catRes.data.code === 0) categories.value = catRes.data.data || []
  if (tagRes.data.code === 0) tags.value = tagRes.data.data || []
}

async function loadArticle() {
  if (!articleId) return
  loading.value = true
  try {
    const { data } = await getArticle(articleId)
    if (data.code === 0 && data.data) {
      const a = data.data as ArticleDetail
      title.value = a.title
      content.value = a.content
      summary.value = a.summary || ''
      coverImage.value = a.cover_image || ''
      categoryId.value = a.category?.id ?? null
      tagIds.value = a.tags?.map((t: TagInfo) => t.id) || []
      isDraft.value = a.is_draft
      isPinned.value = a.is_pinned
    }
  } finally {
    loading.value = false
  }
}

function getDraftData() {
  return {
    title: title.value,
    content: content.value,
    summary: summary.value,
    cover_image: coverImage.value,
    category_id: categoryId.value,
    tag_ids: tagIds.value,
    is_draft: isDraft.value,
    is_pinned: isPinned.value,
  }
}

onBeforeUnmount(() => {
  flushDraft(getDraftData())
})

// 自动保存
watch([title, content, summary, coverImage, categoryId, tagIds, isDraft, isPinned], () => {
  if (title.value || content.value) {
    lastSaved.value = '保存中...'
    saveDraft(getDraftData(), () => {
      lastSaved.value = '已保存'
    })
  }
}, { deep: true })

// 恢复草稿
function checkAndRestoreDraft() {
  if (isEditing) return // 编辑模式不恢复草稿
  if (!hasDraft()) return
  const draft = loadDraft()
  if (!draft) return
  dialog.info({
    title: '发现未保存的草稿',
    content: `上次编辑于 ${new Date(draft.saved_at).toLocaleString('zh-CN')}，是否恢复？`,
    positiveText: '恢复',
    negativeText: '放弃',
    onPositiveClick: () => {
      title.value = draft.title
      content.value = draft.content
      summary.value = draft.summary
      coverImage.value = draft.cover_image
      categoryId.value = draft.category_id
      tagIds.value = draft.tag_ids
      isDraft.value = draft.is_draft
      isPinned.value = draft.is_pinned
    },
    onNegativeClick: () => clearDraft(),
  })
}

async function handleSave(publish: boolean) {
  saving.value = true
  try {
    const payload = {
      title: title.value,
      content: content.value,
      summary: summary.value || null,
      cover_image: coverImage.value || null,
      category_id: categoryId.value,
      tag_ids: tagIds.value,
      is_draft: !publish,
      is_pinned: isPinned.value,
    }

    let result
    if (isEditing) {
      result = await updateArticle(articleId!, payload)
    } else {
      result = await createArticle(payload)
    }

    if (result.data.code === 0) {
      clearDraft()
      message.success(publish ? '发布成功' : '草稿已保存')
      const newArticle = result.data.data as ArticleDetail
      router.push(`/article/${newArticle.id}`)
    } else {
      message.error(result.data.message)
    }
  } catch (e: any) {
    message.error(e?.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleCreateTag(name: string) {
  try {
    const { data } = await createTag({ name })
    if (data.code === 0 && data.data) {
      const newTag = data.data as TagInfo
      tags.value.push(newTag)
      tagIds.value.push(newTag.id)
      return newTag
    }
  } catch {
    message.error('创建标签失败')
  }
  return null
}

async function handleImageUpload(file: File) {
  const { data } = await uploadFile(file)
  if (data.code === 0 && data.data) {
    return { url: `/static/uploads/${data.data.path.split('static/uploads/')[1] || data.data.path}` }
  }
  throw new Error('上传失败')
}

function insertCoverImage(url: string) {
  coverImage.value = url
  showImageUpload.value = false
}

onMounted(async () => {
  await loadCategoriesAndTags()
  if (isEditing) {
    await loadArticle()
  } else {
    checkAndRestoreDraft()
  }
})
</script>

<template>
  <div style="max-width: 1000px; margin: 0 auto; padding-top: 24px;">
    <NSpin :show="loading">
      <!-- 工具栏 -->
      <div class="glass" style="padding: 12px 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
        <NButton text @click="router.back()">← 返回</NButton>
        <div style="flex: 1;" />
        <NText v-if="lastSaved" depth="3" style="font-size: 12px;">{{ lastSaved }}</NText>
        <NSwitch v-model:value="isDraft" checked-text="草稿" unchecked-text="发布" />
        <NButton secondary :loading="saving" @click="handleSave(true)" :disabled="!title">
          {{ isDraft ? '发布' : '更新' }}
        </NButton>
        <NButton type="primary" :loading="saving" @click="handleSave(false)" :disabled="!title">
          保存草稿
        </NButton>
      </div>

      <div style="display: flex; gap: 20px; align-items: flex-start;">
        <!-- 元数据面板 -->
        <div class="glass" style="width: 280px; flex-shrink: 0; padding: 20px;">
          <div style="margin-bottom: 16px;">
            <NText strong style="display: block; margin-bottom: 4px;">分类</NText>
            <NSelect
              v-model:value="categoryId"
              :options="categories.map(c => ({ label: c.name, value: c.id }))"
              placeholder="选择分类"
              clearable
            />
          </div>

          <div style="margin-bottom: 16px;">
            <NText strong style="display: block; margin-bottom: 4px;">标签</NText>
            <NSelect
              v-model:value="tagIds"
              :options="tags.map(t => ({ label: t.name, value: t.id }))"
              placeholder="选择标签"
              multiple
              tag
              filterable
              @create="(l: string) => handleCreateTag(l)"
            />
          </div>

          <div style="margin-bottom: 16px;">
            <NText strong style="display: block; margin-bottom: 4px;">摘要</NText>
            <NInput v-model:value="summary" type="textarea" :autosize="{ minRows: 3 }" placeholder="文章摘要..." />
          </div>

          <div style="margin-bottom: 16px;">
            <NText strong style="display: block; margin-bottom: 4px;">封面图</NText>
            <div v-if="coverImage" style="margin-bottom: 8px;">
              <img :src="coverImage" style="width: 100%; border-radius: 8px; max-height: 150px; object-fit: cover;" alt="" />
            </div>
            <NInput v-model:value="coverImage" placeholder="封面图 URL" />
            <NButton size="small" quaternary style="margin-top: 4px;" @click="showImageUpload = true">
              上传图片
            </NButton>
          </div>

          <div style="margin-bottom: 16px;">
            <NSpace align="center">
              <NSwitch v-model:value="isPinned" />
              <NText>置顶文章</NText>
            </NSpace>
          </div>
        </div>

        <!-- 编辑器主体 -->
        <div style="flex: 1; min-width: 0;">
          <NInput
            v-model:value="title"
            placeholder="文章标题..."
            size="large"
            style="margin-bottom: 16px; font-size: 24px; font-weight: 700;"
          />
          <MarkdownEditor v-model="content" :upload-fn="handleImageUpload" />
        </div>
      </div>
    </NSpin>

    <!-- 图片上传弹窗 -->
    <NModal v-model:show="showImageUpload" title="上传图片">
      <div class="glass" style="padding: 24px; width: 500px; max-width: 90vw;">
        <ImageUpload @uploaded="insertCoverImage" />
      </div>
    </NModal>
  </div>
</template>
