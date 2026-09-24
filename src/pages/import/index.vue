<template>
  <view class="tm-page">
    <view class="tip-card">
      <text class="tip-title">两种导入方式</text>
      <text class="tip-text">① 上传朋友圈截图，自动识别文字与时间</text>
      <text class="tip-text">② 手动粘贴文字，再补充照片</text>
    </view>

    <view class="action-row">
      <button class="tm-primary-btn action-btn" @tap="pickScreenshot">上传截图识别</button>
    </view>

    <view v-if="recognizing" class="tm-empty">正在识别截图…</view>

    <view v-if="showForm" class="tm-card form-card">
      <text class="section-title">{{ fromScreenshot ? '识别结果（可修改）' : '粘贴内容' }}</text>
      <textarea
        v-model="form.content"
        class="content-input"
        :placeholder="fromScreenshot ? '识别到的文字' : '从朋友圈复制文字粘贴到这里'"
        maxlength="2000"
        auto-height
      />
      <input
        v-model="form.originalTime"
        class="plain-input"
        placeholder="原始发布时间，如 2026-09-24 20:30（选填）"
      />
      <view class="media-grid">
        <view v-for="(img, index) in form.images" :key="index" class="media-wrap">
          <image class="media-item" :src="img" mode="aspectFill" />
          <view class="media-remove" @tap="removeImage(index)">×</view>
        </view>
        <view v-if="form.images.length < 9" class="media-add" @tap="chooseImage">+</view>
      </view>
      <button class="tm-primary-btn submit" :loading="saving" @tap="confirmImport">
        确认导入
      </button>
    </view>

    <view v-else class="action-row">
      <button class="plain-btn action-btn" @tap="startManual">手动粘贴文字</button>
    </view>
  </view>
</template>

<script>
import { recognizeScreenshot } from '../../utils/ocr.js'
import { callFunction, uploadFile, buildCloudPath } from '../../utils/cloud.js'

export default {
  data() {
    return {
      recognizing: false,
      showForm: false,
      saving: false,
      fromScreenshot: false,
      form: {
        content: '',
        originalTime: '',
        images: [],
        imageFileIDs: []
      },
      ocrFileID: ''
    }
  },
  methods: {
    pickScreenshot() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          await this.doRecognize(res.tempFilePaths[0])
        }
      })
    },
    async doRecognize(filePath) {
      this.recognizing = true
      uni.showLoading({ title: '识别中…' })
      try {
        const result = await recognizeScreenshot(filePath)
        this.form.content = result.content || ''
        this.form.originalTime = result.originalTime || ''
        this.ocrFileID = result.fileID || ''
        this.form.images = [filePath]
        this.form.imageFileIDs = this.ocrFileID ? [this.ocrFileID] : []
        this.fromScreenshot = true
        this.showForm = true
      } catch (err) {
        uni.showToast({ title: '识别失败，请改用手动导入', icon: 'none' })
        console.error(err)
        this.startManual()
      } finally {
        this.recognizing = false
        uni.hideLoading()
      }
    },
    startManual() {
      this.fromScreenshot = false
      this.ocrFileID = ''
      this.showForm = true
    },
    chooseImage() {
      uni.chooseImage({
        count: 9 - this.form.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.form.images = this.form.images.concat(res.tempFilePaths)
          this.form.imageFileIDs = this.form.imageFileIDs.concat(new Array(res.tempFilePaths.length).fill(''))
        }
      })
    },
    removeImage(index) {
      this.form.images.splice(index, 1)
      this.form.imageFileIDs.splice(index, 1)
    },
    async confirmImport() {
      if (!this.form.content.trim() && !this.form.images.length) {
        uni.showToast({ title: '内容为空', icon: 'none' })
        return
      }
      this.saving = true
      uni.showLoading({ title: '导入中…' })
      try {
        const fileIDs = []
        for (let i = 0; i < this.form.images.length; i++) {
          const cached = this.form.imageFileIDs[i]
          if (cached) {
            fileIDs.push(cached)
          } else {
            const fileID = await uploadFile(this.form.images[i], buildCloudPath('records', this.form.images[i]))
            fileIDs.push(fileID)
          }
        }
        await callFunction('record', {
          action: 'create',
          content: this.form.content.trim(),
          fileIDs,
          originalTime: this.form.originalTime.trim(),
          type: 'imported',
          sourceType: this.fromScreenshot ? 'screenshot' : 'manual'
        })
        uni.hideLoading()
        uni.showToast({ title: '导入成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 600)
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: '导入失败', icon: 'none' })
        console.error(err)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.tip-card {
  padding: 28rpx;
  border-radius: 24rpx;
  background-color: rgba(124, 108, 240, 0.08);
}

.tip-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #7c6cf0;
  margin-bottom: 12rpx;
}

.tip-text {
  display: block;
  font-size: 24rpx;
  color: #6b7280;
  line-height: 1.8;
}

.action-row {
  margin-top: 32rpx;
}

.action-btn {
  width: 100%;
}

.plain-btn {
  background-color: #ffffff;
  color: #7c6cf0;
  border-radius: 999rpx;
  font-size: 30rpx;
}

.form-card {
  margin-top: 32rpx;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.content-input {
  width: 100%;
  min-height: 200rpx;
  font-size: 30rpx;
  line-height: 1.6;
}

.plain-input {
  height: 72rpx;
  margin-top: 16rpx;
  font-size: 26rpx;
  border-bottom: 2rpx solid #eceef6;
}

.media-grid {
  display: flex;
  flex-wrap: wrap;
  margin-top: 24rpx;
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

.submit {
  margin-top: 40rpx;
}
</style>
