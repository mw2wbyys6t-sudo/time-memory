const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()
const _ = db.command
const VLOGS = 'vlogs'
const RECORDS = 'records'
const MEDIA = 'media'

function ok(data, extra = {}) {
  return { success: true, data, ...extra }
}

function fail(message) {
  return { success: false, message }
}

async function resolveUrls(vlog) {
  if (!vlog) return vlog
  const fileList = [vlog.videoFileID, vlog.coverFileID].filter(Boolean)
  if (!fileList.length) return vlog
  const res = await cloud.getTempFileURL({ fileList })
  const urlMap = {}
  res.fileList.forEach((file) => {
    urlMap[file.fileID] = file.tempFileURL || ''
  })
  return {
    ...vlog,
    videoUrl: vlog.videoFileID ? urlMap[vlog.videoFileID] || vlog.videoUrl : vlog.videoUrl,
    coverUrl: vlog.coverFileID ? urlMap[vlog.coverFileID] || vlog.coverUrl : vlog.coverUrl
  }
}

async function list() {
  const res = await db
    .collection(VLOGS)
    .orderBy('createdAt', 'desc')
    .limit(50)
    .get()
  const data = await Promise.all(res.data.map((item) => resolveUrls(item)))
  return ok(data)
}

async function get(event) {
  if (!event.id) return fail('缺少 Vlog id')
  const res = await db.collection(VLOGS).doc(event.id).get()
  const data = await resolveUrls(res.data)
  return ok(data)
}

async function collectSourceRecords(limit) {
  const recordRes = await db
    .collection(RECORDS)
    .orderBy('originalTime', 'desc')
    .limit(limit)
    .get()
  const records = recordRes.data
  if (!records.length) return { records: [], fileIDs: [] }

  const ids = records.map((item) => item._id)
  const mediaRes = await db
    .collection(MEDIA)
    .where({ recordId: _.in(ids) })
    .orderBy('createdAt', 'asc')
    .limit(1000)
    .get()

  return {
    records,
    fileIDs: mediaRes.data.map((m) => m.fileID)
  }
}

async function generateVideo(source, options) {
  const provider = process.env.VLOG_PROVIDER
  if (!provider) {
    return {
      status: 'failed',
      message: '尚未接入 AI 视频生成服务，请先配置 VLOG_PROVIDER 与对应密钥'
    }
  }
  return {
    status: 'failed',
    message: `暂不支持的生成服务：${provider}`
  }
}

async function create(event) {
  const openid = cloud.getWXContext().OPENID
  const limit = Math.min(Number(event.limit) || 20, 50)
  const { records, fileIDs } = await collectSourceRecords(limit)

  if (records.length === 0) {
    return fail('还没有可用的记录，先去记录一些时光吧')
  }

  const now = new Date()
  const vlog = {
    _openid: openid,
    title: event.title || '我的时光 Vlog',
    description: event.description || '',
    recordIds: records.map((item) => item._id),
    mediaFileIDs: fileIDs,
    videoFileID: '',
    coverFileID: '',
    videoUrl: '',
    coverUrl: '',
    duration: 0,
    status: 'generating',
    config: event.config || {},
    createdAt: now,
    updatedAt: now
  }

  const addRes = await db.collection(VLOGS).add({ data: vlog })
  const vlogId = addRes._id

  const result = await generateVideo({ records, fileIDs }, vlog.config)

  await db
    .collection(VLOGS)
    .doc(vlogId)
    .update({
      data: {
        status: result.status,
        videoFileID: result.videoFileID || '',
        coverFileID: result.coverFileID || '',
        duration: result.duration || 0,
        errorMessage: result.message || '',
        updatedAt: new Date()
      }
    })

  return ok({ id: vlogId, status: result.status, message: result.message || '' })
}

exports.main = async (event) => {
  try {
    switch (event.action) {
      case 'list':
        return await list()
      case 'get':
        return await get(event)
      case 'create':
        return await create(event)
      default:
        return fail(`未知 action: ${event.action}`)
    }
  } catch (err) {
    console.error('[vlog] error', err)
    return fail(err.message || '服务异常')
  }
}
