<script setup lang="ts">
import { ref } from 'vue'
import { NUpload, NButton, NText, NProgress, NSpace, useMessage } from 'naive-ui'
import type { UploadFileInfo } from 'naive-ui'
import { uploadFile } from '../api/files'

const emit = defineEmits<{ uploaded: [url: string] }>()

const message = useMessage()
const uploading = ref(false)
const progress = ref(0)
const uploadedUrl = ref('')

async function handleUpload({ file }: { file: UploadFileInfo }) {
  if (!file.file) return
  uploading.value = true
  progress.value = 0
  try {
    const { data } = await uploadFile(file.file, (pct) => {
      progress.value = pct
    })
    if (data.code === 0 && data.data) {
      const { path } = data.data
      const clean = path.replace(/\\/g, '/')
      const idx = clean.indexOf('static/uploads/')
      const url = idx !== -1 ? '/' + clean.slice(idx) : '/' + clean
      uploadedUrl.value = url
      emit('uploaded', url)
      message.success('上传成功')
    } else {
      message.error(data.message || '上传失败')
    }
  } catch (e: any) {
    message.error(e?.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

function copyUrl() {
  if (!uploadedUrl.value) return
  navigator.clipboard.writeText(uploadedUrl.value).then(() => {
    message.success('链接已复制')
  })
}
</script>

<template>
  <div>
    <NUpload
      accept="image/*"
      :max="1"
      :show-file-list="false"
      @change="handleUpload"
      :disabled="uploading"
    >
      <NButton :loading="uploading">
        {{ uploading ? '上传中...' : '选择图片' }}
      </NButton>
    </NUpload>

    <NProgress
      v-if="uploading"
      :percentage="progress"
      style="margin-top: 12px;"
    />

    <div v-if="uploadedUrl" style="margin-top: 16px;">
      <img
        :src="uploadedUrl"
        style="max-width: 100%; max-height: 300px; border-radius: 8px; display: block; margin-bottom: 8px;"
        alt=""
      />
      <NSpace>
        <NText depth="3" style="font-size: 12px; word-break: break-all;">{{ uploadedUrl }}</NText>
        <NButton size="tiny" @click="copyUrl">复制链接</NButton>
      </NSpace>
    </div>
  </div>
</template>
