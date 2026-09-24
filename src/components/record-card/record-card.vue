<template>
  <view class="record-card" @tap="handleTap">
    <view class="card-head">
      <view class="meta">
        <text class="date">{{ displayTime }}</text>
        <text v-if="record.type === 'imported'" class="badge">导入</text>
      </view>
      <text v-if="record.mood" class="mood">{{ moodText }}</text>
    </view>

    <text class="content">{{ record.content || '（无文字内容）' }}</text>

    <view v-if="images.length" class="media-grid">
      <image
        v-for="(img, index) in images"
        :key="index"
        class="media-item"
        :src="img"
        mode="aspectFill"
      />
    </view>

    <view v-if="tags.length" class="tag-row">
      <text v-for="(tag, index) in tags" :key="index" class="tag"># {{ tag }}</text>
    </view>

    <view v-if="record.location" class="location">
      <text class="location-text">{{ record.location }}</text>
    </view>
  </view>
</template>

<script>
import { relativeTime } from '../../utils/format.js'

const MOOD_MAP = {
  happy: '开心',
  sad: '低落',
  neutral: '平静',
  excited: '兴奋'
}

export default {
  name: 'RecordCard',
  props: {
    record: {
      type: Object,
      required: true
    }
  },
  computed: {
    images() {
      return (this.record.images || []).slice(0, 9)
    },
    tags() {
      return this.record.tags || []
    },
    displayTime() {
      return relativeTime(this.record.originalTime || this.record.createdAt)
    },
    moodText() {
      return MOOD_MAP[this.record.mood] || ''
    }
  },
  methods: {
    handleTap() {
      this.$emit('tap', this.record)
    }
  }
}
</script>

<style scoped>
.record-card {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(31, 36, 48, 0.06);
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.meta {
  display: flex;
  align-items: center;
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

.mood {
  font-size: 22rpx;
  color: #ffb020;
}

.content {
  display: block;
  font-size: 28rpx;
  line-height: 1.6;
  color: #1f2430;
}

.media-grid {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16rpx;
}

.media-item {
  width: 200rpx;
  height: 200rpx;
  margin: 0 10rpx 10rpx 0;
  border-radius: 12rpx;
  background-color: #f1f2f7;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16rpx;
}

.tag {
  font-size: 22rpx;
  color: #7c6cf0;
  margin-right: 16rpx;
}

.location {
  margin-top: 16rpx;
}

.location-text {
  font-size: 22rpx;
  color: #9aa0b4;
}
</style>
