<!-- frontend/src/components/DynamicCursor.vue -->
<script setup lang="ts">
import { useCustomCursor } from '../composables/useCustomCursor'

const { cursorPos, cursorHover, ripples, enabled } = useCustomCursor()
</script>

<template>
  <div v-if="enabled" style="position: fixed; inset: 0; pointer-events: none; z-index: 99999;">
    <!-- Main cursor dot -->
    <div
      :style="{
        position: 'fixed',
        left: `${cursorPos.x}px`,
        top: `${cursorPos.y}px`,
        width: cursorHover ? '12px' : '20px',
        height: cursorHover ? '12px' : '20px',
        borderRadius: '50%',
        border: `1px solid var(--color-primary)`,
        background: cursorHover ? 'var(--color-primary)' : 'transparent',
        transform: 'translate(-50%, -50%)',
        transition: 'width 0.2s ease, height 0.2s ease, background 0.2s ease',
        opacity: 0.6,
      }"
    />
    <!-- Ripples -->
    <div
      v-for="r in ripples"
      :key="r.id"
      :style="{
        position: 'fixed',
        left: `${r.x}px`,
        top: `${r.y}px`,
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        border: '1px solid var(--color-primary)',
        transform: 'translate(-50%, -50%)',
        opacity: 0,
        animation: 'cursor-ripple 0.6s ease-out forwards',
      }"
    />
  </div>
</template>

<style>
@keyframes cursor-ripple {
  0% { transform: translate(-50%, -50%) scale(0); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}
</style>
