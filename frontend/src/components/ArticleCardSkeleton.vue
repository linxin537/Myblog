<template>
  <div :style="{
    borderRadius: '14px',
    overflow: 'hidden',
    border: '1px solid var(--color-hairline-soft)',
    background: 'var(--color-canvas)',
  }">
    <div :style="{
      aspectRatio: '1 / 1',
      background: 'var(--color-surface-soft)',
      animation: 'pulse 1.5s ease-in-out infinite',
    }" />
    <div :style="{ padding: '16px' }">
      <div :style="{ height: '14px', width: '40%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '8px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ height: '18px', width: '90%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '6px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ height: '18px', width: '65%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '12px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ display: 'flex', justifyContent: 'space-between' }">
        <div :style="{ height: '13px', width: '35%', background: 'var(--color-surface-soft)', borderRadius: '4px', animation: 'pulse 1.5s ease-in-out infinite' }" />
        <div :style="{ height: '13px', width: '20%', background: 'var(--color-surface-soft)', borderRadius: '4px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
