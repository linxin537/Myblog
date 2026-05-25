<script setup lang="ts">
import { NButton, NDropdown } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import { onMounted, ref, watch, onUnmounted } from 'vue'
import NotificationBell from './NotificationBell.vue'
import MenuToggleIcon from './MenuToggleIcon.vue'
import { useNotificationStore } from '../stores/notification'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifStore = useNotificationStore()
notifStore.startPolling()

const headerScrolled = ref(false)
const mobileMenuOpen = ref(false)

onMounted(() => {
  ScrollTrigger.create({
    start: 'top -50',
    end: 'max',
    onEnter: () => { headerScrolled.value = true },
    onLeaveBack: () => { headerScrolled.value = false },
  })

  // Close mobile menu when resizing to desktop
  const onResize = () => {
    if (window.innerWidth >= 768 && mobileMenuOpen.value) {
      mobileMenuOpen.value = false
    }
  }
  window.addEventListener('resize', onResize)
  onUnmounted(() => window.removeEventListener('resize', onResize))
})

// Body scroll lock when mobile menu is open
watch(mobileMenuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onUnmounted(() => {
  document.body.style.overflow = ''
})

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function onNavClick(path: string) {
  closeMobileMenu()
  router.push(path)
}

const adminOptions = [
  { label: '分类管理', key: 'categories' },
  { label: '标签管理', key: 'tags' },
  { label: '用户管理', key: 'users' },
  { type: 'divider' as const, key: 'd1' },
  { label: '审计日志', key: 'audit-logs' },
]

function handleAdminSelect(key: string) {
  closeMobileMenu()
  router.push(`/admin/${key}`)
}

async function handleLogout() {
  await auth.logout()
  closeMobileMenu()
  router.push('/login')
}

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <div :style="{ minHeight: '100vh', background: 'var(--color-canvas)', position: 'relative', zIndex: 2 }">
    <!-- ===== Custom Glassmorphic Header ===== -->
    <header
      class="site-header"
      :class="{
        'site-header--scrolled': headerScrolled && !mobileMenuOpen,
        'site-header--menu-open': mobileMenuOpen,
      }"
    >
      <nav class="site-nav" :class="{ 'site-nav--scrolled': headerScrolled }">
        <!-- Logo -->
        <a class="site-logo" href="/" @click.prevent="router.push('/')">
          <svg viewBox="0 0 84 24" fill="currentColor">
            <path d="M45.035 23.984c-1.34-.062-2.566-.441-3.777-1.16-1.938-1.152-3.465-3.187-4.02-5.36-.199-.784-.238-1.128-.234-2.058 0-.691.008-.87.062-1.207.23-1.5.852-2.883 1.852-4.144.297-.371 1.023-1.09 1.41-1.387 1.399-1.082 2.84-1.68 4.406-1.816.536-.047 1.528-.02 2.047.054 1.227.184 2.227.543 3.106 1.121 1.277.84 2.5 2.184 3.367 3.7.098.168.172.308.172.312-.004 0-1.047.723-2.32 1.598l-2.711 1.867c-.61.422-2.91 2.008-2.993 2.062l-.074.047-1-1.574c-.55-.867-1.008-1.594-1.012-1.61-.007-.019.922-.648 2.188-1.476 1.215-.793 2.2-1.453 2.191-1.46-.02-.032-.508-.27-.691-.34a5 5 0 0 0-.465-.13c-.371-.09-1.105-.125-1.426-.07-1.285.219-2.336 1.3-2.777 2.852-.215.761-.242 1.636-.074 2.355.129.527.383 1.102.691 1.543.234.332.727.82 1.047 1.031.664.434 1.195.586 1.969.555.613-.023 1.027-.129 1.64-.426 1.184-.574 2.16-1.554 2.828-2.843.122-.235.208-.372.227-.368.082.032 3.77 1.938 3.79 1.961.034.032-.407.93-.696 1.414a12 12 0 0 1-1.051 1.477c-.36.422-1.102 1.14-1.492 1.445a9.9 9.9 0 0 1-3.23 1.684 9.2 9.2 0 0 1-2.95.351M74.441 23.996c-1.488-.043-2.8-.363-4.066-.992-1.687-.848-2.992-2.14-3.793-3.774-.605-1.234-.863-2.402-.863-3.894.004-1.149.176-2.156.527-3.11.14-.378.531-1.171.75-1.515 1.078-1.703 2.758-2.934 4.805-3.524.847-.242 1.465-.332 2.433-.351 1.032-.024 1.743.055 2.48.277l.31.09.007 2.48c.004 1.364 0 2.481-.008 2.481a1 1 0 0 1-.12-.055c-.688-.347-2.09-.488-2.962-.296-.754.167-1.296.453-1.785.945a3.7 3.7 0 0 0-1.043 2.11c-.047.382-.02 1.109.055 1.437a3.4 3.4 0 0 0 .941 1.738c.75.75 1.715 1.102 2.875 1.05.645-.03 1.118-.14 1.563-.366q1.721-.864 2.02-3.145c.035-.293.042-1.266.042-7.957V0H84l-.012 8.434c-.008 7.851-.011 8.457-.054 8.757-.196 1.274-.586 2.25-1.301 3.243-1.293 1.808-3.555 3.07-6.145 3.437-.664.098-1.43.14-2.047.125M9.848 23.574a14 14 0 0 1-1.137-.152c-2.352-.426-4.555-1.781-6.117-3.774-.27-.335-.75-1.05-.95-1.406-1.156-2.047-1.695-4.27-1.64-6.77.047-1.995.43-3.66 1.23-5.316.524-1.086 1.04-1.87 1.793-2.715C4.567 1.72 6.652.535 8.793.171 9.68.02 10.093 0 12.297 0h1.789v5.441l-.961.016c-2.36.04-3.441.215-4.441.719-.836.414-1.278.879-1.895 1.976-.219.399-.535 1.02-.535 1.063 0 .02 1.285.027 3.918.027h3.914v5.113h-3.914c-2.54 0-3.918.008-3.918.028 0 .05.254.597.441.953.344.656.649 1.086 1.051 1.48.668.657 1.356.985 2.445 1.16.645.106 1.274.145 2.61.16l1.285.016v5.442l-2.055-.004a120 120 0 0 1-2.183-.016M16.469 14.715c0-5.504.011-9.04.031-9.29a5.54 5.54 0 0 1 1.527-3.48c.778-.82 1.922-1.457 3.118-1.734C21.915.035 22.422 0 24.39 0h1.652v4.914h-1.426c-1.324 0-1.445.004-1.644.055-.739.191-1.059.699-1.106 1.754l-.015.355h4.191v4.914h-4.184v11.602h-5.39ZM27.023 14.727c0-5.223.012-9.04.028-9.278.129-1.98 1.234-3.68 3.012-4.62.87-.462 1.777-.716 2.851-.802A61 61 0 0 1 34.945 0h1.649v4.914h-1.426c-1.32 0-1.441.004-1.64.055-.739.191-1.063.699-1.106 1.754l-.02.355h4.192v4.914H32.41v11.602h-5.387ZM55.48 15.406V7.22h4.66v1.363c0 1.3.005 1.363.051 1.363.04 0 .075-.054.133-.203.38-.98.969-1.68 1.711-2.031.563-.266 1.422-.43 2.492-.48l.414-.02v4.914l-.414.035c-.738.063-1.597.195-2.058.313-.297.082-.688.28-.875.449-.324.289-.532.703-.625 1.254-.094.547-.098.879-.098 5.144v4.274h-5.39Zm0 0" />
          </svg>
        </a>

        <!-- Desktop nav links -->
        <div class="nav-links-desktop">
          <button
            class="nav-ghost-btn"
            :class="{ active: isActive('/') && route.path === '/' }"
            @click="router.push('/')"
          >
            首页
          </button>
          <button
            v-if="auth.isAuthor"
            class="nav-ghost-btn"
            :class="{ active: isActive('/editor') }"
            @click="router.push('/editor')"
          >
            创作
          </button>
          <button
            v-if="auth.isAuthor"
            class="nav-ghost-btn"
            :class="{ active: isActive('/drafts') }"
            @click="router.push('/drafts')"
          >
            草稿
          </button>
          <button
            v-if="auth.isLoggedIn"
            class="nav-ghost-btn"
            :class="{ active: isActive('/favorites') }"
            @click="router.push('/favorites')"
          >
            收藏
          </button>
          <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
            <button class="nav-ghost-btn">
              管理
            </button>
          </NDropdown>
        </div>

        <!-- Right utils -->
        <div class="nav-utils">
          <NButton quaternary circle @click="dark = !dark">
            <template #icon>
              <NIcon :component="dark ? Sunny : Moon" />
            </template>
          </NButton>

          <NotificationBell v-if="auth.isLoggedIn" />

          <template v-if="auth.isLoggedIn">
            <button class="nav-ghost-btn" @click="router.push('/settings')">
              {{ auth.user?.username }}
            </button>
            <button class="nav-outline-btn" @click="handleLogout">
              登出
            </button>
          </template>
          <template v-else>
            <button class="nav-primary-btn" @click="router.push('/login')">
              登录
            </button>
          </template>

          <!-- Mobile hamburger -->
          <button
            class="mobile-hamburger"
            @click="mobileMenuOpen = !mobileMenuOpen"
            aria-label="Toggle menu"
          >
            <MenuToggleIcon :open="mobileMenuOpen" :duration="400" :size="20" />
          </button>
        </div>
      </nav>

      <!-- Mobile menu overlay -->
      <Transition name="mobile-menu">
        <div v-if="mobileMenuOpen" class="mobile-menu-overlay" @click.self="closeMobileMenu">
          <div class="mobile-menu-inner">
            <div class="mobile-menu-links">
              <button class="nav-ghost-btn mobile-nav-link" @click="onNavClick('/')">
                首页
              </button>
              <button
                v-if="auth.isAuthor"
                class="nav-ghost-btn mobile-nav-link"
                @click="onNavClick('/editor')"
              >
                创作
              </button>
              <button
                v-if="auth.isAuthor"
                class="nav-ghost-btn mobile-nav-link"
                @click="onNavClick('/drafts')"
              >
                草稿
              </button>
              <button
                v-if="auth.isLoggedIn"
                class="nav-ghost-btn mobile-nav-link"
                @click="onNavClick('/favorites')"
              >
                收藏
              </button>
              <button
                v-if="auth.isLoggedIn"
                class="nav-ghost-btn mobile-nav-link"
                @click="onNavClick('/settings')"
              >
                设置
              </button>
              <template v-if="auth.isAdmin">
                <div :style="{ height: '1px', background: 'var(--color-hairline-soft)', margin: '4px 12px' }" />
                <button class="nav-ghost-btn mobile-nav-link" @click="onNavClick('/admin/categories')">
                  分类管理
                </button>
                <button class="nav-ghost-btn mobile-nav-link" @click="onNavClick('/admin/tags')">
                  标签管理
                </button>
                <button class="nav-ghost-btn mobile-nav-link" @click="onNavClick('/admin/users')">
                  用户管理
                </button>
                <button class="nav-ghost-btn mobile-nav-link" @click="onNavClick('/admin/audit-logs')">
                  审计日志
                </button>
              </template>
            </div>
            <div class="mobile-menu-actions">
              <button
                v-if="auth.isLoggedIn"
                class="nav-outline-btn nav-outline-btn--block"
                @click="handleLogout"
              >
                登出
              </button>
              <button
                v-else
                class="nav-primary-btn nav-primary-btn--block"
                @click="onNavClick('/login')"
              >
                登录
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </header>

    <!-- Page content -->
    <div :style="{ maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '32px' }">
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* --- Auth buttons (outline / primary) --- */
.nav-outline-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  color: var(--color-ink);
  background: transparent;
  border: 1px solid var(--color-ink);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

.nav-outline-btn:hover {
  background: var(--color-ink);
  color: var(--color-canvas);
}

.nav-outline-btn--block {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
}

.nav-primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  color: #fff;
  background: var(--color-primary);
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease;
  white-space: nowrap;
}

.nav-primary-btn:hover {
  background: var(--color-primary-hover);
}

.nav-primary-btn--block {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
}
</style>
