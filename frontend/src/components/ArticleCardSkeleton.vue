<script setup lang="ts">

</script>

<template>
  <div class="glass" style="padding: 20px; border-radius: 12px; margin-bottom: 16px;">
    <div style="display: flex; gap: 16px;">
      <div class="skeleton-pulse" style="width: 200px; height: 120px; flex-shrink: 0; border-radius: 8px;" />
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div class="skeleton-pulse" style="height: 22px; width: 70%;" />
        <div class="skeleton-pulse" style="height: 14px; width: 90%;" />
        <div class="skeleton-pulse" style="height: 14px; width: 50%;" />
        <div style="display: flex; gap: 8px; margin-top: auto;">
          <div class="skeleton-pulse" style="height: 20px; width: 50px; border-radius: 10px;" />
          <div class="skeleton-pulse" style="height: 20px; width: 50px; border-radius: 10px;" />
        </div>
      </div>
    </div>
  </div>
</template>
