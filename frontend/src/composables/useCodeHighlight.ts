import { onMounted, onUnmounted } from 'vue'

function getThemeLink(theme: string): HTMLLinkElement | null {
  return document.querySelector(`link[data-highlight-theme="${theme}"]`) as HTMLLinkElement | null
}

function ensureThemeLink(targetTheme: string) {
  let link = getThemeLink(targetTheme)
  if (!link) {
    link = document.createElement('link')
    link.rel = 'stylesheet'
    link.dataset.highlightTheme = targetTheme
    link.href = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/${targetTheme}.min.css`
    document.head.appendChild(link)
  }
  link.disabled = false
  return link
}

export function useCodeHighlight() {
  function updateTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
    const lightLink = getThemeLink('github')
    const darkLink = getThemeLink('github-dark')

    if (isDark) {
      if (lightLink) lightLink.disabled = true
      ensureThemeLink('github-dark')
    } else {
      if (darkLink) darkLink.disabled = true
      ensureThemeLink('github')
    }
  }

  const observer = new MutationObserver(updateTheme)

  onMounted(() => {
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    updateTheme()
  })

  onUnmounted(() => {
    observer.disconnect()
  })

  function copyCodeBlock(block: HTMLElement) {
    const code = block.textContent || ''
    navigator.clipboard.writeText(code).catch(() => {})
  }

  return { copyCodeBlock, updateTheme }
}
