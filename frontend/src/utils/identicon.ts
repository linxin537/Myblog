/**
 * GitHub-style identicon generator.
 * Deterministic geometric avatar from username hash.
 */

const PALETTE: [string, string][] = [
  ['#667eea', '#764ba2'],
  ['#f093fb', '#f5576c'],
  ['#4facfe', '#00f2fe'],
  ['#43e97b', '#38f9d7'],
  ['#fa709a', '#fee140'],
  ['#a18cd1', '#fbc2eb'],
  ['#fad0c4', '#ffd1ff'],
  ['#ff9a9e', '#fecfef'],
  ['#a1c4fd', '#c2e9fb'],
  ['#d4fc79', '#96e6a1'],
  ['#84fab0', '#8fd3f4'],
  ['#e0c3fc', '#8ec5fc'],
]

function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}

function getPalette(username: string): [string, string] {
  return PALETTE[hashString(username) % PALETTE.length]
}

/**
 * Generate a 5x5 symmetric identicon pattern.
 * Returns a 5-element array of 5-bit integers (each bit = fill/empty).
 * Mirroring: horizontal flip for symmetry.
 */
function generatePattern(hash: number): number[] {
  const rows: number[] = []
  for (let y = 0; y < 5; y++) {
    let row = 0
    // Only need to compute left 3 columns; mirror for right
    for (let x = 0; x < 3; x++) {
      const bit = (hash >> (y * 3 + x)) & 1
      if (bit) {
        row |= (1 << x)
        row |= (1 << (4 - x)) // mirror
      }
    }
    rows.push(row)
  }
  return rows
}

export function generateIdenticonSVG(username: string, size = 80): string {
  const hash = hashString(username)
  const [color1, color2] = getPalette(username)
  const pattern = generatePattern(hash)
  const cellSize = size / 5
  const radius = size * 0.1 // 8px radius equivalent at 80px

  let rects = ''
  for (let y = 0; y < 5; y++) {
    for (let x = 0; x < 5; x++) {
      if (pattern[y] & (1 << x)) {
        const rx = x * cellSize
        const ry = y * cellSize
        rects += `<rect x="${rx}" y="${ry}" width="${cellSize}" height="${cellSize}" rx="${radius}" ry="${radius}"/>`
      }
    }
  }

  return `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${color1}"/><stop offset="100%" stop-color="${color2}"/></linearGradient></defs>
      <rect width="${size}" height="${size}" rx="${radius}" fill="url(#g)"/>
      <g fill="rgba(255,255,255,0.55)">${rects}</g>
    </svg>`
  )}`
}

export function getIdenticonUrl(username: string, customAvatar?: string | null, size = 80): string {
  if (customAvatar) return customAvatar
  return generateIdenticonSVG(username, size)
}
