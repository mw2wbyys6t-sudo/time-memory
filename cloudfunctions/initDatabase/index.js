const cloud = require('wx-server-sdk')
const { COLLECTIONS } = require('./schema.js')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()

async function ensureCollection(name) {
  try {
    await db.createCollection(name)
    return { name, created: true }
  } catch (err) {
    const message = (err && err.message) || ''
    if (/already exists|exists|已存在/i.test(message) || err.errCode === -501001) {
      return { name, created: false, existed: true }
    }
    return { name, created: false, error: message }
  }
}

exports.main = async () => {
  const results = []
  for (const item of COLLECTIONS) {
    results.push(await ensureCollection(item.name))
  }
  return {
    success: true,
    total: COLLECTIONS.length,
    results
  }
}
