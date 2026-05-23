export function useReadingTime(content: string): number {
  const chineseChars = (content.match(/[一-鿿]/g) || []).length
  const words = (content.match(/[a-zA-Z]+/g) || []).length
  return Math.max(1, Math.ceil((chineseChars + words) / 400))
}

export function formatReadingTime(content: string): string {
  return `约 ${useReadingTime(content)} 分钟`
}
