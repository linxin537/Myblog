<script setup lang="ts">
defineProps<{
  padding?: string
}>()
</script>

<template>
  <div class="glass scale-in" :style="{ padding: padding || '32px' }">
    <slot />
  </div>
</template>
