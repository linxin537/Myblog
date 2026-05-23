<script setup lang="ts">
import { ref, watch, watchEffect, onMounted, nextTick } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import gsap from 'gsap'
import { useRoute } from 'vue-router'
import AppLayout from './components/AppLayout.vue'
import DynamicCursor from './components/DynamicCursor.vue'

const THEME_KEY = 'blog-theme'

function getSavedTheme(): boolean {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved !== null) return saved === 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

const isDark = ref(getSavedTheme())

onMounted(() => {
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
})

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
})

const route = useRoute()

// Page transition: animate on route change
watch(
  () => route.fullPath,
  () => {
    nextTick(() => {
      const page = document.querySelector('.page-content')
      if (page) {
        gsap.fromTo(
          page,
          { opacity: 0, y: 8 },
          { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' }
        )
      }
    })
  }
)

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
        <DynamicCursor />
        <AppLayout v-model:dark="isDark">
          <RouterView v-slot="{ Component, route: r }">
            <div class="page-content" :key="r.fullPath">
              <component :is="Component" />
            </div>
          </RouterView>
        </AppLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
