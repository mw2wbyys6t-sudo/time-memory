const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()

exports.main = async () => {
  const { OPENID, APPID, UNIONID } = cloud.getWXContext()
  if (!OPENID) {
    return { openid: '', message: '获取用户身份失败' }
  }

  const users = db.collection('users')
  const existing = await users.where({ _openid: OPENID }).limit(1).get()

  if (existing.data.length === 0) {
    const now = new Date()
    await users.add({
      data: {
        _openid: OPENID,
        nickname: '',
        avatar: '',
        createdAt: now,
        updatedAt: now
      }
    })
    return { openid: OPENID, appid: APPID, unionid: UNIONID || '', nickname: '', avatar: '' }
  }

  const user = existing.data[0]
  return {
    openid: OPENID,
    appid: APPID,
    unionid: UNIONID || '',
    nickname: user.nickname || '',
    avatar: user.avatar || ''
  }
}
