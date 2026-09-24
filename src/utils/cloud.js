import { CLOUD_ENV_ID } from '../config.js'

let initialized = false

function getWxCloud() {
  if (typeof wx !== 'undefined' && wx.cloud) {
    return wx.cloud
  }
  return null
}

export function initCloud() {
  if (initialized) return initialized
  const cloud = getWxCloud()
  if (!cloud) {
    console.warn('[cloud] 当前环境不支持微信云开发，请在微信小程序端运行')
    return false
  }
  cloud.init({
    env: CLOUD_ENV_ID,
    traceUser: true
  })
  initialized = true
  return true
}

export function callFunction(name, data = {}) {
  return new Promise((resolve, reject) => {
    const cloud = getWxCloud()
    if (!cloud) {
      reject(new Error('当前环境不支持微信云开发'))
      return
    }
    cloud
      .callFunction({ name, data })
      .then((res) => resolve(res.result))
      .catch((err) => reject(err))
  })
}

export function uploadFile(filePath, cloudPath) {
  return new Promise((resolve, reject) => {
    const cloud = getWxCloud()
    if (!cloud) {
      reject(new Error('当前环境不支持微信云开发'))
      return
    }
    cloud
      .uploadFile({
        cloudPath,
        filePath
      })
      .then((res) => resolve(res.fileID))
      .catch((err) => reject(err))
  })
}

export function getTempFileURL(fileList) {
  return new Promise((resolve, reject) => {
    const cloud = getWxCloud()
    if (!cloud) {
      reject(new Error('当前环境不支持微信云开发'))
      return
    }
    const list = Array.isArray(fileList) ? fileList : [fileList]
    cloud
      .getTempFileURL({ fileList: list })
      .then((res) => resolve(res.fileList))
      .catch((err) => reject(err))
  })
}

export function buildCloudPath(dir, filePath) {
  const ext = (filePath || '').split('.').pop() || 'png'
  const rand = Math.random().toString(36).slice(2, 8)
  return `${dir}/${Date.now()}-${rand}.${ext}`
}
