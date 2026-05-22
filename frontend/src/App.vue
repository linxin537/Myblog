<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import AppLayout from './components/AppLayout.vue'

const isDark = ref(false)

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
})

const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#6C9BF2',
    primaryColorHover: '#8BB4FF',
    primaryColorPressed: '#5A88E0',
    borderRadius: '12px',
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
  },
}

const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#6C9BF2',
    primaryColorHover: '#8BB4FF',
    primaryColorPressed: '#5A88E0',
    borderRadius: '12px',
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
  },
}
</script>

<template>
  <NConfigProvider :theme="isDark ? darkTheme : undefined" :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <AppLayout v-model:dark="isDark">
          <RouterView v-slot="{ Component }">
            <Transition name="page" mode="out-in">
              <component :is="Component" />
            </Transition>
          </RouterView>
        </AppLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
