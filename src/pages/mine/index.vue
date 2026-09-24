<template>
  <view class="tm-page">
    <view class="profile">
      <image class="avatar" :src="user.avatar || defaultAvatar" mode="aspectFill" />
      <view class="profile-info">
        <text class="nickname">{{ user.nickname || '时光旅人' }}</text>
        <text class="openid">{{ maskedOpenid }}</text>
      </view>
    </view>

    <view class="stat-row">
      <view class="stat-card">
        <text class="stat-num">{{ stats.records }}</text>
        <text class="stat-label">条记录</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ stats.vlogs }}</text>
        <text class="stat-label">支 Vlog</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ stats.imported }}</text>
        <text class="stat-label">条导入</text>
      </view>
    </view>

    <view class="tm-card menu">
      <view class="menu-item" @tap="goCreate">
        <text class="menu-text">记录此刻</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goImport">
        <text class="menu-text">导入朋友圈</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="showEnv">
        <text class="menu-text">云开发环境</text>
        <text class="menu-value">{{ envShort }}</text>
      </view>
      <view class="menu-item" @tap="showAbout">
        <text class="menu-text">关于时光记忆</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script>
import { callFunction } from '../../utils/cloud.js'
import { CLOUD_ENV_ID, APP_NAME } from '../../config.js'

export default {
  data() {
    return {
      user: {},
      stats: { records: 0, vlogs: 0, imported: 0 },
      defaultAvatar: ''
    }
  },
  computed: {
    maskedOpenid() {
      const id = this.user.openid || ''
      if (!id) return '未登录'
      return `${id.slice(0, 6)}****${id.slice(-4)}`
    },
    envShort() {
      if (!CLOUD_ENV_ID || CLOUD_ENV_ID.indexOf('REPLACE') === 0) return '未配置'
      return `${CLOUD_ENV_ID.slice(0, 8)}…`
    }
  },
  onShow() {
    this.loadUser()
    this.loadStats()
  },
  methods: {
    async loadUser() {
      try {
        const res = await callFunction('login', {})
        this.user = { openid: res.openid, nickname: res.nickname, avatar: res.avatar }
      } catch (err) {
        console.error(err)
      }
    },
    async loadStats() {
      try {
        const res = await callFunction('record', { action: 'stats' })
        this.stats = res.data || this.stats
      } catch (err) {
        console.error(err)
      }
    },
    goCreate() {
      uni.navigateTo({ url: '/pages/create/index' })
    },
    goImport() {
      uni.navigateTo({ url: '/pages/import/index' })
    },
    showEnv() {
      uni.showModal({
        title: '云开发环境',
        content: CLOUD_ENV_ID,
        showCancel: false
      })
    },
    showAbout() {
      uni.showModal({
        title: APP_NAME,
        content: '记录生活，把时光串成一段影像。',
        showCancel: false
      })
    }
  }
}
</script>

<style scoped>
.profile {
  display: flex;
  align-items: center;
  padding: 40rpx 8rpx;
}

.avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background-color: #eceef6;
}

.profile-info {
  margin-left: 28rpx;
}

.nickname {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
}

.openid {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #9aa0b4;
}

.stat-row {
  display: flex;
  margin-bottom: 32rpx;
}

.stat-card {
  flex: 1;
  padding: 28rpx 0;
  margin-right: 20rpx;
  border-radius: 24rpx;
  background-color: #ffffff;
  text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(31, 36, 48, 0.06);
}

.stat-card:last-child {
  margin-right: 0;
}

.stat-num {
  display: block;
  font-size: 40rpx;
  font-weight: 600;
  color: #7c6cf0;
}

.stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #9aa0b4;
}

.menu {
  padding: 0 28rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 108rpx;
  border-bottom: 2rpx solid #f4f5fa;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-text {
  font-size: 30rpx;
}

.menu-arrow {
  font-size: 40rpx;
  color: #c8ccd8;
}

.menu-value {
  font-size: 26rpx;
  color: #9aa0b4;
}
</style>
