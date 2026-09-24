const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()
const _ = db.command
const RECORDS = 'records'
const MEDIA = 'media'
const VLOGS = 'vlogs'

function ok(data, extra = {}) {
  return { success: true, data, ...extra }
}

function fail(message) {
  return { success: false, message }
}

async function attachImages(records) {
  if (!records.length) return records
  const ids = records.map((item) => item._id)
  const mediaRes = await db
    .collection(MEDIA)
    .where({ recordId: _.in(ids) })
    .orderBy('createdAt', 'asc')
    .limit(1000)
    .get()

  const fileIDs = mediaRes.data.map((m) => m.fileID)
  const urlMap = {}
  if (fileIDs.length) {
    const urlRes = await cloud.getTempFileURL({ fileList: fileIDs })
    urlRes.fileList.forEach((file) => {
      urlMap[file.fileID] = file.tempFileURL || file.fileID
    })
  }

  const byRecord = {}
  mediaRes.data.forEach((m) => {
    if (!byRecord[m.recordId]) byRecord[m.recordId] = []
    byRecord[m.recordId].push(urlMap[m.fileID] || m.fileID)
  })

  return records.map((item) => ({
    ...item,
    images: byRecord[item._id] || []
  }))
}

function normalizeTime(value) {
  if (!value) return null
  const date = new Date(String(value).replace(/-/g, '/'))
  return Number.isNaN(date.getTime()) ? null : date
}

async function list(event) {
  const limit = Math.min(Number(event.limit) || 30, 100)
  const skip = Number(event.skip) || 0
  const where = {}
  if (event.type) where.type = event.type
  if (event.tag) where.tags = _.all([event.tag])

  const res = await db
    .collection(RECORDS)
    .where(where)
    .orderBy('originalTime', 'desc')
    .orderBy('createdAt', 'desc')
    .skip(skip)
    .limit(limit)
    .get()

  const countRes = await db.collection(RECORDS).where(where).count()
  const data = await attachImages(res.data)
  return ok(data, { total: countRes.total })
}

async function get(event) {
  if (!event.id) return fail('缺少记录 id')
  const res = await db.collection(RECORDS).doc(event.id).get()
  const data = await attachImages([res.data])
  return ok(data[0])
}

async function create(event) {
  const now = new Date()
  const openid = cloud.getWXContext().OPENID
  const record = {
    _openid: openid,
    type: event.type || 'original',
    sourceType: event.sourceType || 'manual',
    content: (event.content || '').trim(),
    location: (event.location || '').trim(),
    tags: Array.isArray(event.tags) ? event.tags : [],
    mood: event.mood || '',
    originalTime: normalizeTime(event.originalTime) || now,
    createdAt: now,
    updatedAt: now
  }

  const addRes = await db.collection(RECORDS).add({ data: record })
  const recordId = addRes._id

  const fileIDs = Array.isArray(event.fileIDs) ? event.fileIDs : []
  if (fileIDs.length) {
    const tasks = fileIDs.map((fileID) =>
      db.collection(MEDIA).add({
        data: {
          _openid: openid,
          recordId,
          fileID,
          url: '',
          type: 'image',
          width: 0,
          height: 0,
          size: 0,
          createdAt: now
        }
      })
    )
    await Promise.all(tasks)
  }

  return ok({ id: recordId })
}

async function remove(event) {
  if (!event.id) return fail('缺少记录 id')
  const openid = cloud.getWXContext().OPENID
  const doc = await db.collection(RECORDS).doc(event.id).get()
  if (!doc.data || doc.data._openid !== openid) {
    return fail('无权删除该记录')
  }
  await db.collection(RECORDS).doc(event.id).remove()

  const mediaRes = await db.collection(MEDIA).where({ recordId: event.id }).limit(1000).get()
  if (mediaRes.data.length) {
    await Promise.all(mediaRes.data.map((m) => db.collection(MEDIA).doc(m._id).remove()))
    const fileIDs = mediaRes.data.map((m) => m.fileID)
    if (fileIDs.length) {
      await cloud.deleteFile({ fileList: fileIDs })
    }
  }
  return ok({ id: event.id })
}

async function stats() {
  const [recordCount, importedCount, vlogCount] = await Promise.all([
    db.collection(RECORDS).count(),
    db.collection(RECORDS).where({ type: 'imported' }).count(),
    db.collection(VLOGS).count()
  ])
  return ok({
    records: recordCount.total,
    imported: importedCount.total,
    vlogs: vlogCount.total
  })
}

exports.main = async (event) => {
  try {
    switch (event.action) {
      case 'list':
        return await list(event)
      case 'get':
        return await get(event)
      case 'create':
        return await create(event)
      case 'remove':
        return await remove(event)
      case 'stats':
        return await stats()
      default:
        return fail(`未知 action: ${event.action}`)
    }
  } catch (err) {
    console.error('[record] error', err)
    return fail(err.message || '服务异常')
  }
}
