<script setup lang="ts">
defineProps<{
  padding?: string
  aurora?: boolean
}>()
</script>

<template>
  <div
    :class="aurora ? 'glass-aurora scale-in' : 'glass scale-in'"
    :style="{ padding: padding || '32px' }"
  >
    <slot />
  </div>
</template>
