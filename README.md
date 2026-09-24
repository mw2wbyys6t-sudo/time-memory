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
