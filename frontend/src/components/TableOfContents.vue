<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { NText } from 'naive-ui'

const props = defineProps<{
  headings: { id: string; text: string; level: number }[]
}>()

const activeId = ref('')

function scrollToHeading(id: string) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeId.value = id
  }
}

let observer: IntersectionObserver | null = null

onMounted(() => {
  if (props.headings.length === 0) return

  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeId.value = entry.target.id
        }
      }
    },
    { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
  )

  props.headings.forEach((h) => {
    const el = document.getElementById(h.id)
    if (el) observer!.observe(el)
  })
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <aside v-if="headings.length > 0" class="toc-sidebar">
    <NText depth="3" style="font-size: 12px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 12px; display: block; text-transform: uppercase;">
      目录
    </NText>
    <nav>
      <a
        v-for="h in headings"
        :key="h.id"
        class="toc-link"
        :class="{
          'toc-active': activeId === h.id,
          'toc-h2': h.level === 2,
          'toc-h3': h.level === 3,
        }"
        :style="{ paddingLeft: (h.level - 1) * 12 + 'px' }"
        @click.prevent="scrollToHeading(h.id)"
      >
        {{ h.text }}
      </a>
    </nav>
  </aside>
</template>

<style scoped>
.toc-sidebar {
  width: 200px;
  flex-shrink: 0;
  position: sticky;
  top: 100px;
  align-self: flex-start;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
  padding: 18px;
  border-radius: 14px;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline-soft);
}

.toc-link {
  display: block;
  padding: 5px 0 5px 10px;
  font-size: 13px;
  color: var(--color-muted);
  text-decoration: none;
  border-left: 2px solid transparent;
  transition: color 0.25s ease, border-color 0.25s ease;
  cursor: pointer;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toc-link:hover {
  color: var(--color-primary);
}

.toc-active {
  color: var(--color-primary);
  border-left-color: var(--color-primary);
  font-weight: 600;
}

.toc-h2 {
  font-size: 13px;
}

.toc-h3 {
  font-size: 12px;
  opacity: 0.8;
}

@media (max-width: 1024px) {
  .toc-sidebar {
    display: none;
  }
}
</style>
