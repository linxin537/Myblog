/**
 * Tag-to-cover-image mapping.
 * When an article has no cover_image, derive a default gradient + icon
 * from the first matching tag.
 */

export interface CoverStyle {
  gradient: string    // CSS gradient string
  icon: string        // Emoji
}

const TAG_COVER_MAP: Record<string, CoverStyle> = {
  '编程':    { gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: '\u{1F4BB}' },
  '技术':    { gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: '\u{1F527}' },
  '前端':    { gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: '\u{1F3A8}' },
  '后端':    { gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: '\u{2699}\u{FE0F}' },
  'Python':  { gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', icon: '\u{1F40D}' },
  'JavaScript': { gradient: 'linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)', icon: '\u{1F310}' },
  'AI':      { gradient: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)', icon: '\u{1F916}' },
  '设计':    { gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', icon: '\u{1F3A8}' },
  '产品':    { gradient: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)', icon: '\u{1F4A1}' },
  '创业':    { gradient: 'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)', icon: '\u{1F680}' },
  '生活':    { gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', icon: '\u{1F30D}' },
  '随笔':    { gradient: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)', icon: '\u{270F}\u{FE0F}' },
  '阅读':    { gradient: 'linear-gradient(135deg, #c1dfc4 0%, #deecdd 100%)', icon: '\u{1F4DA}' },
  '摄影':    { gradient: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)', icon: '\u{1F4F7}' },
  '音乐':    { gradient: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)', icon: '\u{1F3B5}' },
}

const DEFAULT_COVER: CoverStyle = {
  gradient: 'linear-gradient(135deg, #e8e8e8 0%, #f5f5f5 100%)',
  icon: '\u{1F4DD}',
}

/**
 * Get cover style for a given tag name.
 * Falls back to DEFAULT_COVER for unknown tags.
 */
export function getCoverForTag(tagName?: string | null): CoverStyle {
  if (!tagName) return DEFAULT_COVER
  const match = TAG_COVER_MAP[tagName]
  if (match) return match
  const lower = tagName.toLowerCase()
  for (const [key, value] of Object.entries(TAG_COVER_MAP)) {
    if (key.toLowerCase() === lower) return value
  }
  return DEFAULT_COVER
}

/**
 * Get cover style from an article's tags array.
 * Uses the first tag, falls back to default.
 */
export function getCoverForArticle(tags?: Array<{ id: number; name: string }> | null): CoverStyle {
  if (!tags || tags.length === 0) return DEFAULT_COVER
  return getCoverForTag(tags[0].name)
}
