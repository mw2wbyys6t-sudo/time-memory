const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()

const TIME_PATTERN = /(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\s*\d{0,2}:?\d{0,2})/
const NOISE_PATTERN = /^(赞|评论|收藏|分享|\d+人?赞|\d+条评论|全文|收起)$/

function extractTags(text) {
  const tags = []
  const pattern = /#([^\s#]+)/g
  let match
  while ((match = pattern.exec(text)) !== null) {
    if (!tags.includes(match[1])) tags.push(match[1])
  }
  return tags
}

function extractTime(text) {
  const match = text.match(TIME_PATTERN)
  if (!match) return ''
  return match[1].replace(/[年月]/g, '-').replace(/日/g, '').trim()
}

function cleanContent(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !NOISE_PATTERN.test(line) && !TIME_PATTERN.test(line))
    .join('\n')
}

async function recognize(event) {
  if (!event.fileID) {
    return { content: '', rawText: '', supported: false, message: '缺少截图文件' }
  }

  const urlRes = await cloud.getTempFileURL({ fileList: [event.fileID] })
  const imgUrl = urlRes.fileList[0] && urlRes.fileList[0].tempFileURL
  if (!imgUrl) {
    return { content: '', rawText: '', supported: false, message: '获取截图地址失败' }
  }

  try {
    const ocrRes = await cloud.openapi.ocr.printedText({ imgUrl })
    const rawText = (ocrRes.items || []).map((item) => item.text).join('\n')

    const record = {
      _openid: cloud.getWXContext().OPENID,
      imageFileID: event.fileID,
      rawText,
      parsedData: {
        content: cleanContent(rawText),
        tags: extractTags(rawText),
        originalTime: extractTime(rawText)
      },
      createdAt: new Date()
    }
    await db.collection('ocr_results').add({ data: record })

    return {
      content: record.parsedData.content,
      rawText,
      originalTime: record.parsedData.originalTime,
      tags: record.parsedData.tags,
      supported: true
    }
  } catch (err) {
    console.error('[import] ocr error', err)
    return {
      content: '',
      rawText: '',
      supported: false,
      message: 'OCR 识别不可用，请检查小程序是否已开通文字识别能力，或改用手动导入'
    }
  }
}

exports.main = async (event) => {
  try {
    switch (event.action) {
      case 'recognize':
        return await recognize(event)
      default:
        return { success: false, message: `未知 action: ${event.action}` }
    }
  } catch (err) {
    console.error('[import] error', err)
    return { success: false, message: err.message || '服务异常' }
  }
}
