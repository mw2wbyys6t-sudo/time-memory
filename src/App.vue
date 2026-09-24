<script>
import { initCloud } from './utils/cloud.js'

export default {
  onLaunch() {
    initCloud()
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
page {
  background-color: #f7f8fc;
  color: #1f2430;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', Helvetica, sans-serif;
  font-size: 28rpx;
}

.tm-page {
  min-height: 100vh;
  padding: 24rpx;
  box-sizing: border-box;
}

.tm-card {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 32rpx rgba(31, 36, 48, 0.06);
}

.tm-primary-btn {
  background-image: linear-gradient(135deg, #7c6cf0, #9b8cff);
  color: #ffffff;
  border-radius: 999rpx;
  font-size: 30rpx;
  border: none;
}

.tm-primary-btn::after {
  border: none;
}

.tm-empty {
  padding: 120rpx 0;
  text-align: center;
  color: #9aa0b4;
  font-size: 26rpx;
}
</style>
