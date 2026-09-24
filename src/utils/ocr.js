import { callFunction, uploadFile, buildCloudPath } from './cloud.js'

export function parseScreenshotText(rawText) {
  if (!rawText) {
    return { content: '', tags: [], images: [] }
  }
  const lines = rawText
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  const tagPattern = /#([^\s#]+)/g
  const tags = []
  let match
  while ((match = tagPattern.exec(rawText)) !== null) {
    if (!tags.includes(match[1])) tags.push(match[1])
  }

  const timePattern = /(\d{4}-\d{2}-\d{2}|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2})/
  const noisePattern = /^(赞|评论|收藏|分享|\d+人?赞|\d+条评论)$/

  const contentLines = lines.filter(
    (line) => !noisePattern.test(line) && !timePattern.test(line) && !/^#/.test(line)
  )

  return {
    content: contentLines.join('\n'),
    tags,
    images: []
  }
}

export async function recognizeScreenshot(filePath) {
  const cloudPath = buildCloudPath('ocr', filePath)
  const fileID = await uploadFile(filePath, cloudPath)
  const result = await callFunction('import', {
    action: 'recognize',
    fileID
  })
  return { fileID, ...result }
}
