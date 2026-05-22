const STORAGE_KEY = 'draft_article_new'
const DEBOUNCE_MS = 2000

export interface DraftData {
  title: string
  content: string
  summary: string
  cover_image: string
  category_id: number | null
  tag_ids: number[]
  is_draft: boolean
  is_pinned: boolean
  saved_at: number
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null

export function useDraftSave() {
  function loadDraft(): DraftData | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return null
      return JSON.parse(raw) as DraftData
    } catch {
      return null
    }
  }

  function saveDraft(data: Omit<DraftData, 'saved_at'>) {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...data, saved_at: Date.now() }))
    }, DEBOUNCE_MS)
  }

  function clearDraft() {
    localStorage.removeItem(STORAGE_KEY)
    if (debounceTimer) clearTimeout(debounceTimer)
  }

  function hasDraft(): boolean {
    return !!localStorage.getItem(STORAGE_KEY)
  }

  return { loadDraft, saveDraft, clearDraft, hasDraft }
}
