<template>
  <view class="tm-page">
    <view v-if="loading" class="tm-empty">加载中…</view>

    <view v-else-if="!vlog" class="tm-empty">没有找到这支 Vlog</view>

    <view v-else>
      <view v-if="vlog.status === 'completed' && vlog.videoUrl" class="player-wrap">
        <video
          class="player"
          :src="vlog.videoUrl"
          :poster="vlog.coverUrl"
          controls
          show-center-play-btn
        />
      </view>

      <view v-else class="status-card">
        <text class="status-title">
          {{ vlog.status === 'failed' ? '生成失败' : '视频生成中…' }}
        </text>
        <text class="status-desc">
          {{
            vlog.status === 'failed'
              ? '请稍后重试，或检查 AI 视频服务是否已接入'
              : 'AI 正在挑素材、卡节奏、配音乐，请稍等'
          }}
        </text>
        <button
          v-if="vlog.status !== 'failed'"
          class="plain-btn retry-btn"
          @tap="refresh"
        >
          刷新状态
        </button>
      </view>

      <view class="tm-card info-card">
        <text class="vlog-title">{{ vlog.title || '未命名 Vlog' }}</text>
        <text class="vlog-desc">{{ vlog.description || '暂无描述' }}</text>
        <view class="info-row">
          <text class="info-label">素材数量</text>
          <text class="info-value">{{ (vlog.recordIds || []).length }} 条记录</text>
        </view>
        <view class="info-row">
          <text class="info-label">时长</text>
          <text class="info-value">{{ vlog.duration ? formatDuration(vlog.duration) : '—' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">创建时间</text>
          <text class="info-value">{{ formatDate(vlog.createdAt, true) }}</text>
        </view>
      </view>

      <button v-if="vlog.status === 'completed'" class="tm-primary-btn save-btn" @tap="saveVideo">
        保存到相册
      </button>
    </view>
  </view>
</template>

<script>
import { callFunction } from '../../utils/cloud.js'
import { formatDate, formatDuration } from '../../utils/format.js'

export default {
  data() {
    return {
      id: '',
      vlog: null,
      loading: true,
      timer: null
    }
  },
  onLoad(options) {
    this.id = options.id || ''
    this.loadVlog()
  },
  onUnload() {
    if (this.timer) clearInterval(this.timer)
  },
  methods: {
    formatDate,
    formatDuration,
    async loadVlog() {
      if (!this.id) {
        this.loading = false
        return
      }
      try {
        const res = await callFunction('vlog', { action: 'get', id: this.id })
        this.vlog = res.data || null
        if (this.vlog && this.vlog.status === 'generating') {
          this.startPolling()
        }
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    startPolling() {
      if (this.timer) return
      this.timer = setInterval(() => {
        if (this.vlog && this.vlog.status !== 'generating') {
          clearInterval(this.timer)
          this.timer = null
          return
        }
        this.refresh()
      }, 5000)
    },
    refresh() {
      this.loadVlog()
    },
    saveVideo() {
      uni.showLoading({ title: '保存中…' })
      uni.downloadFile({
        url: this.vlog.videoUrl,
        success: (res) => {
          uni.saveVideoToPhotosAlbum({
            filePath: res.tempFilePath,
            success: () => uni.showToast({ title: '已保存到相册', icon: 'success' }),
            fail: () => uni.showToast({ title: '保存失败，请检查授权', icon: 'none' })
          })
        },
        fail: () => uni.showToast({ title: '下载失败', icon: 'none' }),
        complete: () => uni.hideLoading()
      })
    }
  }
}
</script>

<style scoped>
.player-wrap {
  border-radius: 24rpx;
  overflow: hidden;
  background-color: #000000;
}

.player {
  width: 100%;
  height: 420rpx;
}

.status-card {
  padding: 60rpx 32rpx;
  border-radius: 24rpx;
  background-color: #ffffff;
  text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(31, 36, 48, 0.06);
}

.status-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #7c6cf0;
}

.status-desc {
  display: block;
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #9aa0b4;
  line-height: 1.7;
}

.retry-btn {
  margin-top: 32rpx;
  background-color: #ffffff;
  color: #7c6cf0;
  border-radius: 999rpx;
  font-size: 28rpx;
}

.info-card {
  margin-top: 24rpx;
}

.vlog-title {
  display: block;
  font-size: 34rpx;
  font-weight: 600;
}

.vlog-desc {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #6b7280;
  line-height: 1.7;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-top: 24rpx;
}

.info-label {
  font-size: 26rpx;
  color: #9aa0b4;
}

.info-value {
  font-size: 26rpx;
  color: #1f2430;
}

.save-btn {
  margin-top: 32rpx;
}
</style>
