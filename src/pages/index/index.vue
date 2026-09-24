<template>
  <view class="tm-page">
    <view class="hero">
      <text class="hero-title">{{ greeting }}</text>
      <text class="hero-sub">已记录 {{ total }} 条时光</text>
    </view>

    <view class="entry-row">
      <view class="entry-card" @tap="goCreate">
        <text class="entry-title">记录此刻</text>
        <text class="entry-desc">写下今天的心情</text>
      </view>
      <view class="entry-card entry-card--alt" @tap="goImport">
        <text class="entry-title">导入朋友圈</text>
        <text class="entry-desc">截图识别 · 一键搬运</text>
      </view>
    </view>

    <view v-if="loading" class="tm-empty">加载中…</view>
    <view v-else-if="errorMsg" class="tm-empty">{{ errorMsg }}</view>
    <view v-else-if="!records.length" class="tm-empty">
      还没有记录，点击上方「记录此刻」开始吧
    </view>
    <view v-else class="timeline">
      <record-card
        v-for="item in records"
        :key="item._id"
        :record="item"
        @tap="goDetail"
      />
    </view>
  </view>
</template>

<script>
import RecordCard from '../../components/record-card/record-card.vue'
import { callFunction } from '../../utils/cloud.js'

export default {
  components: { RecordCard },
  data() {
    return {
      records: [],
      total: 0,
      loading: true,
      errorMsg: ''
    }
  },
  computed: {
    greeting() {
      const hour = new Date().getHours()
      if (hour < 6) return '夜深了'
      if (hour < 11) return '早上好'
      if (hour < 14) return '中午好'
      if (hour < 18) return '下午好'
      return '晚上好'
    }
  },
  onShow() {
    this.loadRecords()
  },
  onPullDownRefresh() {
    this.loadRecords().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadRecords() {
      this.loading = true
      this.errorMsg = ''
      try {
        const res = await callFunction('record', { action: 'list', limit: 30 })
        this.records = res.data || []
        this.total = res.total || this.records.length
      } catch (err) {
        this.errorMsg = '加载失败，请检查云开发环境是否已配置'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    goCreate() {
      uni.navigateTo({ url: '/pages/create/index' })
    },
    goImport() {
      uni.navigateTo({ url: '/pages/import/index' })
    },
    goDetail(record) {
      uni.navigateTo({ url: `/pages/record/detail?id=${record._id}` })
    }
  }
}
</script>

<style scoped>
.hero {
  padding: 32rpx 8rpx 40rpx;
}

.hero-title {
  display: block;
  font-size: 48rpx;
  font-weight: 600;
  color: #1f2430;
}

.hero-sub {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #9aa0b4;
}

.entry-row {
  display: flex;
  margin-bottom: 32rpx;
}

.entry-card {
  flex: 1;
  padding: 32rpx 28rpx;
  border-radius: 24rpx;
  background-image: linear-gradient(135deg, #7c6cf0, #9b8cff);
  box-shadow: 0 12rpx 32rpx rgba(124, 108, 240, 0.28);
}

.entry-card--alt {
  margin-left: 20rpx;
  background-image: linear-gradient(135deg, #ffb020, #ffcf6b);
  box-shadow: 0 12rpx 32rpx rgba(255, 176, 32, 0.28);
}

.entry-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
}

.entry-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.85);
}
</style>
