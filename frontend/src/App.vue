<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import AppLayout from './components/AppLayout.vue'

const isDark = ref(true)

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
})

const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#ff385c',
    primaryColorHover: '#e00b41',
    primaryColorPressed: '#c90936',
    borderRadius: '8px',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    textColor1: '#222222',
    textColor2: '#3f3f3f',
    textColor3: '#6a6a6a',
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusLarge: '8px',
    borderRadiusSmall: '8px',
    heightMedium: '40px',
  },
  Input: {
    borderRadius: '8px',
    heightLarge: '48px',
  },
  Tag: {
    borderRadius: '8px',
  },
}

const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#ff5a7a',
    primaryColorHover: '#ff7a95',
    primaryColorPressed: '#e04868',
    borderRadius: '8px',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    textColor1: '#e8e8e8',
    textColor2: '#b0b0b0',
    textColor3: '#888888',
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusLarge: '8px',
    borderRadiusSmall: '8px',
    heightMedium: '40px',
  },
  Input: {
    borderRadius: '8px',
    heightLarge: '48px',
  },
  Tag: {
    borderRadius: '8px',
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
