<script setup lang="ts">
import { Editor } from '@bytemd/vue-next'
import gfm from '@bytemd/plugin-gfm'
import highlight from '@bytemd/plugin-highlight'
import frontmatter from '@bytemd/plugin-frontmatter'
import mediumZoom from '@bytemd/plugin-medium-zoom'
import 'bytemd/dist/index.css'
import 'highlight.js/styles/github.css'
import 'highlight.js/styles/github-dark.css' with { media: '(prefers-color-scheme: dark)' }

const modelValue = defineModel<string>('modelValue', { default: '' })

interface UploadResult {
  url: string
}

const props = defineProps<{
  uploadFn?: (file: File) => Promise<UploadResult>
}>()

const plugins = [gfm(), highlight(), frontmatter(), mediumZoom()]

async function handleUploadImages(files: File[]) {
  if (!props.uploadFn) return []
  const results: { title: string; url: string }[] = []
  for (const file of files) {
    try {
      const result = await props.uploadFn(file)
      results.push({ title: file.name, url: result.url })
    } catch {
      // skip failed uploads
    }
  }
  return results
}
</script>

<template>
  <div class="markdown-editor">
    <Editor
      :value="modelValue"
      :plugins="plugins"
      :upload-images="handleUploadImages"
      locale="zh_Hans"
      @change="(v: string) => modelValue = v"
    />
  </div>
</template>

<style>
.markdown-editor {
  min-height: 500px;
}
.markdown-editor .bytemd {
  height: 600px;
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
}
</style>
