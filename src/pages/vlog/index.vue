<template>
  <view class="tm-page">
    <view class="head">
      <text class="head-title">我的 Vlog</text>
      <text class="head-sub">把时光串成一段影像</text>
    </view>

    <button class="tm-primary-btn create-btn" :loading="creating" @tap="createVlog">
      生成新 Vlog
    </button>

    <view v-if="loading" class="tm-empty">加载中…</view>
    <view v-else-if="!vlogs.length" class="tm-empty">还没有 Vlog，点上方按钮生成第一支吧</view>
    <view v-else>
      <view v-for="item in vlogs" :key="item._id" class="vlog-card" @tap="openPreview(item)">
        <image class="vlog-cover" :src="item.coverUrl || defaultCover" mode="aspectFill" />
        <view class="vlog-info">
          <text class="vlog-title">{{ item.title || '未命名 Vlog' }}</text>
          <text class="vlog-meta">{{ statusText(item) }} · {{ formatDate(item.createdAt) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { callFunction } from '../../utils/cloud.js'
import { formatDate } from '../../utils/format.js'

export default {
  data() {
    return {
      vlogs: [],
      loading: true,
      creating: false,
      defaultCover: ''
    }
  },
  onShow() {
    this.loadVlogs()
  },
  methods: {
    formatDate,
    statusText(item) {
      const map = {
        generating: '生成中',
        completed: '已完成',
        failed: '生成失败'
      }
      return map[item.status] || '未知'
    },
    async loadVlogs() {
      this.loading = true
      try {
        const res = await callFunction('vlog', { action: 'list' })
        this.vlogs = res.data || []
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async createVlog() {
      this.creating = true
      uni.showLoading({ title: '正在生成…' })
      try {
        const res = await callFunction('vlog', { action: 'create', title: '我的时光 Vlog' })
        uni.hideLoading()
        if (res.id) {
          uni.navigateTo({ url: `/pages/vlog/preview?id=${res.id}` })
        } else {
          uni.showToast({ title: res.message || '生成失败', icon: 'none' })
        }
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: '生成失败', icon: 'none' })
        console.error(err)
      } finally {
        this.creating = false
      }
    },
    openPreview(item) {
      uni.navigateTo({ url: `/pages/vlog/preview?id=${item._id}` })
    }
  }
}
</script>

<style scoped>
.head {
  padding: 32rpx 8rpx 24rpx;
}

.head-title {
  display: block;
  font-size: 44rpx;
  font-weight: 600;
}

.head-sub {
  display: block;
  margin-top: 10rpx;
  font-size: 26rpx;
  color: #9aa0b4;
}

.create-btn {
  margin-bottom: 32rpx;
}

.vlog-card {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 20rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(31, 36, 48, 0.06);
}

.vlog-cover {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  background-color: #f1f2f7;
}

.vlog-info {
  flex: 1;
  margin-left: 24rpx;
}

.vlog-title {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
}

.vlog-meta {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #9aa0b4;
}
</style>
