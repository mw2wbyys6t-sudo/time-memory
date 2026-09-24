export function pad(n) {
  return n < 10 ? `0${n}` : `${n}`
}

export function formatDate(value, withTime = false) {
  if (!value) return ''
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const y = date.getFullYear()
  const m = pad(date.getMonth() + 1)
  const d = pad(date.getDate())
  if (!withTime) return `${y}-${m}-${d}`
  const hh = pad(date.getHours())
  const mm = pad(date.getMinutes())
  return `${y}-${m}-${d} ${hh}:${mm}`
}

export function formatMonthDay(value) {
  if (!value) return ''
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

export function relativeTime(value) {
  if (!value) return ''
  const date = value instanceof Date ? value : new Date(value)
  const diff = Date.now() - date.getTime()
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  if (diff < 30 * day) return `${Math.floor(diff / day)}天前`
  return formatDate(value)
}

export function groupByDate(list, field = 'createdAt') {
  const groups = []
  const map = {}
  list.forEach((item) => {
    const key = formatDate(item[field])
    if (!map[key]) {
      map[key] = { date: key, items: [] }
      groups.push(map[key])
    }
    map[key].items.push(item)
  })
  return groups
}

export function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0))
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${pad(m)}:${pad(s)}`
}
