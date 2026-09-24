<template>
  <view class="tm-page">
    <view class="tm-card">
      <textarea
        v-model="form.content"
        class="content-input"
        placeholder="记录一下此刻的心情…"
        maxlength="1000"
        auto-height
      />
      <text class="counter">{{ form.content.length }}/1000</text>
    </view>

    <view class="tm-card section">
      <text class="section-title">照片</text>
      <view class="media-grid">
        <view v-for="(img, index) in form.images" :key="index" class="media-wrap">
          <image class="media-item" :src="img" mode="aspectFill" />
          <view class="media-remove" @tap="removeImage(index)">×</view>
        </view>
        <view v-if="form.images.length < 9" class="media-add" @tap="chooseImage">+</view>
      </view>
    </view>

    <view class="tm-card section">
      <text class="section-title">心情</text>
      <view class="mood-row">
        <view
          v-for="item in moods"
          :key="item.value"
          class="mood-item"
          :class="{ active: form.mood === item.value }"
          @tap="form.mood = item.value"
        >
          <text class="mood-emoji">{{ item.emoji }}</text>
          <text class="mood-label">{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="tm-card section">
      <text class="section-title">标签</text>
      <view class="tag-row">
        <view
          v-for="(tag, index) in form.tags"
          :key="index"
          class="tag-item"
          @tap="removeTag(index)"
        >
          # {{ tag }}
        </view>
        <input
          v-model="tagInput"
          class="tag-input"
          placeholder="输入后回车添加"
          confirm-type="done"
          @confirm="addTag"
        />
      </view>
    </view>

    <view class="tm-card section">
      <text class="section-title">地点</text>
      <input v-model="form.location" class="plain-input" placeholder="选填，如：杭州 · 西湖" />
    </view>

    <button class="tm-primary-btn submit" :loading="saving" @tap="submit">保存记录</button>
  </view>
</template>

<script>
import { uploadFile, buildCloudPath, callFunction } from '../../utils/cloud.js'

export default {
  data() {
    return {
      form: {
        content: '',
        images: [],
        mood: '',
        tags: [],
        location: ''
      },
      tagInput: '',
      saving: false,
      moods: [
        { value: 'happy', label: '开心', emoji: '😊' },
        { value: 'excited', label: '兴奋', emoji: '🤩' },
        { value: 'neutral', label: '平静', emoji: '😌' },
        { value: 'sad', label: '低落', emoji: '😔' }
      ]
    }
  },
  methods: {
    chooseImage() {
      uni.chooseImage({
        count: 9 - this.form.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.form.images = this.form.images.concat(res.tempFilePaths)
        }
      })
    },
    removeImage(index) {
      this.form.images.splice(index, 1)
    },
    addTag() {
      const value = this.tagInput.trim().replace(/^#/, '')
      if (value && !this.form.tags.includes(value)) {
        this.form.tags.push(value)
      }
      this.tagInput = ''
    },
    removeTag(index) {
      this.form.tags.splice(index, 1)
    },
    async submit() {
      if (!this.form.content.trim() && !this.form.images.length) {
        uni.showToast({ title: '写点内容或加张照片吧', icon: 'none' })
        return
      }
      this.saving = true
      uni.showLoading({ title: '保存中…' })
      try {
        const fileIDs = []
        for (const path of this.form.images) {
          const fileID = await uploadFile(path, buildCloudPath('records', path))
          fileIDs.push(fileID)
        }
        await callFunction('record', {
          action: 'create',
          content: this.form.content.trim(),
          mood: this.form.mood,
          tags: this.form.tags,
          location: this.form.location.trim(),
          fileIDs,
          type: 'original',
          sourceType: 'manual'
        })
        uni.hideLoading()
        uni.showToast({ title: '已保存', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 600)
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: '保存失败', icon: 'none' })
        console.error(err)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.content-input {
  width: 100%;
  min-height: 220rpx;
  font-size: 30rpx;
  line-height: 1.6;
}

.counter {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #b6bbcc;
}

.section {
  margin-top: 24rpx;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.media-grid {
  display: flex;
  flex-wrap: wrap;
}

.media-wrap {
  position: relative;
  margin: 0 16rpx 16rpx 0;
}

.media-item {
  width: 180rpx;
  height: 180rpx;
  border-radius: 16rpx;
  background-color: #f1f2f7;
}

.media-remove {
  position: absolute;
  top: -12rpx;
  right: -12rpx;
  width: 40rpx;
  height: 40rpx;
  line-height: 36rpx;
  text-align: center;
  border-radius: 50%;
  background-color: rgba(31, 36, 48, 0.72);
  color: #ffffff;
  font-size: 30rpx;
}

.media-add {
  width: 180rpx;
  height: 180rpx;
  border-radius: 16rpx;
  border: 2rpx dashed #d5d9e6;
  color: #b6bbcc;
  font-size: 56rpx;
  text-align: center;
  line-height: 176rpx;
}

.mood-row {
  display: flex;
}

.mood-item {
  flex: 1;
  margin-right: 16rpx;
  padding: 20rpx 0;
  border-radius: 16rpx;
  background-color: #f7f8fc;
  text-align: center;
}

.mood-item.active {
  background-color: rgba(124, 108, 240, 0.12);
}

.mood-emoji {
  display: block;
  font-size: 40rpx;
}

.mood-label {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #6b7280;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.tag-item {
  padding: 8rpx 20rpx;
  margin: 0 16rpx 16rpx 0;
  border-radius: 999rpx;
  background-color: rgba(124, 108, 240, 0.1);
  color: #7c6cf0;
  font-size: 24rpx;
}

.tag-input {
  flex: 1;
  min-width: 240rpx;
  height: 60rpx;
  font-size: 26rpx;
}

.plain-input {
  height: 60rpx;
  font-size: 28rpx;
}

.submit {
  margin-top: 40rpx;
}
</style>
