<template>
  <view class="tm-page">
    <view v-if="loading" class="tm-empty">加载中…</view>
    <view v-else-if="!record" class="tm-empty">记录不存在或已删除</view>

    <view v-else>
      <view class="tm-card">
        <view class="head-row">
          <text class="date">{{ formatDate(record.originalTime || record.createdAt, true) }}</text>
          <text v-if="record.type === 'imported'" class="badge">导入</text>
        </view>
        <text class="content">{{ record.content || '（无文字内容）' }}</text>
        <view v-if="images.length" class="media-grid">
          <image
            v-for="(img, index) in images"
            :key="index"
            class="media-item"
            :src="img"
            mode="widthFix"
            @tap="previewImage(index)"
          />
        </view>
        <view v-if="tags.length" class="tag-row">
          <text v-for="(tag, index) in tags" :key="index" class="tag"># {{ tag }}</text>
        </view>
        <view v-if="record.location" class="location">
          <text class="location-text">{{ record.location }}</text>
        </view>
      </view>

      <button class="danger-btn" @tap="remove">删除记录</button>
    </view>
  </view>
</template>

<script>
import { callFunction } from '../../utils/cloud.js'
import { formatDate } from '../../utils/format.js'

export default {
  data() {
    return {
      id: '',
      record: null,
      loading: true
    }
  },
  computed: {
    images() {
      return (this.record && this.record.images) || []
    },
    tags() {
      return (this.record && this.record.tags) || []
    }
  },
  onLoad(options) {
    this.id = options.id || ''
    this.loadRecord()
  },
  methods: {
    formatDate,
    previewImage(index) {
      uni.previewImage({ urls: this.images, current: this.images[index] })
    },
    async loadRecord() {
      try {
        const res = await callFunction('record', { action: 'get', id: this.id })
        this.record = res.data || null
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    remove() {
      uni.showModal({
        title: '确认删除',
        content: '删除后不可恢复',
        success: async (res) => {
          if (!res.confirm) return
          try {
            await callFunction('record', { action: 'remove', id: this.id })
            uni.showToast({ title: '已删除', icon: 'success' })
            setTimeout(() => uni.navigateBack(), 500)
          } catch (err) {
            uni.showToast({ title: '删除失败', icon: 'none' })
            console.error(err)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.head-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.date {
  font-size: 24rpx;
  color: #9aa0b4;
}

.badge {
  margin-left: 12rpx;
  padding: 2rpx 12rpx;
  font-size: 20rpx;
  color: #7c6cf0;
  background-color: rgba(124, 108, 240, 0.1);
  border-radius: 8rpx;
}

.content {
  display: block;
  font-size: 30rpx;
  line-height: 1.7;
}

.media-grid {
  margin-top: 20rpx;
}

.media-item {
  width: 100%;
  margin-bottom: 16rpx;
  border-radius: 16rpx;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16rpx;
}

.tag {
  font-size: 24rpx;
  color: #7c6cf0;
  margin-right: 16rpx;
}

.location-text {
  display: block;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #9aa0b4;
}

.danger-btn {
  margin-top: 40rpx;
  background-color: #ffffff;
  color: #ff5b5b;
  border-radius: 999rpx;
  font-size: 30rpx;
}
</style>
