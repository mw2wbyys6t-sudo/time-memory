# time-memory · 时光记忆

一个记录生活、并把记录生成 Vlog 的微信小程序，支持把朋友圈内容导入进来。

## 技术栈

- 前端：uni-app（Vue 3 + Vite），一套代码可编译到微信小程序 / H5
- 后端：微信云开发（云函数 + 云数据库 + 云存储）

## 目录结构

```
time-memory/
├── src/                          # uni-app 前端源码
│   ├── pages/                    # 页面
│   │   ├── index/                # 首页 · 时光时间线
│   │   ├── create/               # 记录此刻
│   │   ├── import/               # 导入朋友圈（截图识别 / 手动粘贴）
│   │   ├── vlog/                 # Vlog 列表 + 预览
│   │   ├── record/               # 记录详情
│   │   └── mine/                 # 我的
│   ├── components/               # 公共组件
│   │   └── record-card/          # 记录卡片
│   ├── utils/                    # 工具
│   │   ├── cloud.js              # 云开发初始化与封装
│   │   ├── ocr.js                # 截图识别封装
│   │   └── format.js             # 日期/文本格式化
│   ├── config.js                 # 全局配置（云环境 ID、集合名等）
│   ├── App.vue / main.js         # 应用入口
│   ├── pages.json                # 页面路由与 tabBar
│   ├── manifest.json             # 应用配置
│   └── uni.scss                  # 全局样式变量
├── cloudfunctions/               # 微信云函数
│   ├── login/                    # 登录 / 初始化用户
│   ├── record/                   # 记录 CRUD 与统计
│   ├── import/                   # 朋友圈截图 OCR 识别
│   ├── vlog/                     # Vlog 生成与管理
│   └── initDatabase/             # 一键创建数据库集合
├── project.config.json           # 微信开发者工具配置
└── package.json
```

## 数据库集合

| 集合 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 用户表 | `_openid`、`nickname`、`avatar` |
| `records` | 生活记录（核心） | `content`、`type`、`tags`、`mood`、`originalTime` |
| `media` | 媒体文件 | `recordId`、`fileID`、`type` |
| `vlogs` | Vlog | `recordIds`、`videoFileID`、`status`、`config` |
| `ocr_results` | 截图识别缓存 | `imageFileID`、`rawText`、`parsedData` |

## 本地开发

```bash
npm install
npm run dev:mp-weixin     # 编译到微信小程序（开发模式）
npm run build:mp-weixin   # 编译到微信小程序（生产模式）
npm run dev:h5            # 浏览器预览
```

编译产物位于 `dist/dev/mp-weixin/`（开发）与 `dist/build/mp-weixin/`（生产）。

## 云开发配置步骤

1. 先执行 `npm install` 和 `npm run dev:mp-weixin`，生成小程序源码目录 `dist/dev/mp-weixin/`。
2. 用微信开发者工具「导入项目」，目录选择本项目根目录 `time-memory`（根目录的 `project.config.json` 已配置 `miniprogramRoot` 与 `cloudfunctionRoot`）。
3. 在开发者工具中开通「云开发」，创建一个环境，复制环境 ID。
4. 把环境 ID 填入 `src/config.js` 的 `CLOUD_ENV_ID`，替换 `REPLACE_WITH_YOUR_ENV_ID`。
5. 右键 `cloudfunctions` 下每个云函数，选择「上传并部署：云端安装依赖」。
6. 运行一次 `initDatabase` 云函数，自动创建全部数据库集合。
7. 在云开发控制台 → 数据库 → 权限设置，把各集合设为「仅创建者可读写」。

> 注意：微信未开放读取朋友圈的官方 API，因此导入采用「截图 OCR 识别」与「手动粘贴」两种方式。
> Vlog 的 AI 自动剪辑需要接入第三方视频生成服务，云函数 `vlog` 中已预留 `VLOG_PROVIDER` 接入点。

## 本地调试完整流程

### 一、准备工具

1. 安装 [Node.js](https://nodejs.org/)（建议 18 及以上）。
2. 安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)（稳定版即可）。
3. 注册一个小程序账号（[mp.weixin.qq.com](https://mp.weixin.qq.com/)），拿到 AppID。

### 二、本地编译

```bash
# 进入项目根目录
cd time-memory

# 安装依赖（首次或拉取新代码后都要跑一次）
npm install

# 开发模式：实时编译到 dist/dev/mp-weixin/
npm run dev:mp-weixin
```

> 开发模式下文件改动会自动重新编译，**不要关闭终端**。

### 三、导入微信开发者工具

1. 打开微信开发者工具 → 「导入项目」。
2. **目录选项目根目录 `time-memory`**（不是 dist），工具会自动读取 `project.config.json`。
3. AppID 填你的真实 AppID（或选「测试号」体验）。
4. 点击导入，工具会自动定位到 `dist/dev/mp-weixin/`。

### 四、开通云开发（关键步骤）

1. 在开发者工具顶部点「云开发」按钮 → 开通 → 创建环境（取名如 `time-memory-prod`）。
2. 复制环境 ID（形如 `time-memory-1a2b3c`）。
3. 打开 [src/config.js](src/config.js)，把 `CLOUD_ENV_ID` 的值改成你的环境 ID。
4. 同时把 AppID 填入 [src/manifest.json](src/manifest.json) 的 `mp-weixin.appid` 和 [project.config.json](project.config.json) 的 `appid`。
5. 回到终端，`dev` 模式会自动重新编译；如果没启动，重启 `npm run dev:mp-weixin`。

### 五、上传云函数

在开发者工具中：

1. 找到左侧 `cloudfunctions/` 目录。
2. **每个云函数都要单独上传**：右键 → 「上传并部署：云端安装依赖」。
3. 涉及的云函数：`login`、`record`、`import`、`vlog`、`initDatabase`。

### 六、初始化数据库

1. 开发者工具 → 云开发控制台 → 云函数 → 找到 `initDatabase`。
2. 点击「测试」或在前端调用一次。
3. 返回 `{ success: true, total: 5, ... }` 即成功。
4. 进入「数据库」标签，能看到 `users / records / media / vlogs / ocr_results` 五个集合。
5. **权限设置**：每个集合点「权限设置」→ 改为「仅创建者可读写」。

### 七、开始测试

回到小程序模拟器：

- **首页**：应显示空状态「还没有记录」。
- **记录此刻**：输入文字 + 选图 + 保存 → 回到首页应看到新记录。
- **导入朋友圈**：上传一张朋友圈截图 → 等 OCR 识别（首次可能需开通能力）。
- **生成 Vlog**：先有记录后，进入 Vlog 页 → 点「生成」→ 会返回"尚未接入"提示（这是预期的）。
- **我的**：显示你的 openid 和统计。

### 八、常见问题

| 现象 | 原因 | 解决 |
|------|------|------|
| 调用云函数报 `-404011 cloud init` | `CLOUD_ENV_ID` 未填或填错 | 检查 `src/config.js` |
| 上传云函数报权限错 | 未登录或 AppID 不对 | 工具右上角重新登录 |
| OCR 报"不可用" | 未开通文字识别能力 | 云开发控制台 → 设置 → 全局能力 → 开通 |
| Vlog 永远"生成中" | 未接 AI 服务（预期） | 接入 `VLOG_PROVIDER` 后才会真的生成 |
| 图片显示空白 | 集合权限设错 | 改为「仅创建者可读写」|

## 已知限制与后续计划

- **朋友圈导入**：微信未开放读朋友圈 API，只能走截图 OCR + 手动粘贴。
- **AI Vlog 生成**：当前云函数 `vlog/index.js` 的 `generateVideo` 仅返回占位结果。接入真实服务需配置环境变量 `VLOG_PROVIDER` 与对应密钥。
- **Vlog 素材选择**：当前自动取最近 20 条记录，未支持手动挑选（待后续迭代）。
