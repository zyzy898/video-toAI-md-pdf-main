# 视频转文档 - AI 视频总结工具

将视频自动分析为图文操作文档，输出 `Markdown` 与 `PDF`，支持单视频和批量处理。

## 项目简介

项目由 `Flask` 后端和 `Vue 3 + Vite` 前端组成：

- 后端负责上传、分析、文档生成、下载与历史记录管理。
- 前端负责参数配置、上传交互、结果展示与文档编辑。
- 通过 `Whisper + LLM + ffmpeg-python` 完成字幕识别、步骤抽取和截图增强。

## 核心功能

- 单视频分析与批量分析
- 字幕驱动模式与视频直传模式
- 低置信度步骤 AI 看图增强
- 结果文档重新生成（支持步骤编辑和排序）
- 历史记录查看、回放与删除
- 导出 Markdown / PDF，支持 ZIP 批量下载

## 技术栈

- 后端：`Python`、`Flask`
- 前端：`Vue 3`、`Vite`
- 多媒体/AI：`Whisper`、`ffmpeg-python`、`imageio-ffmpeg`、`ARK LLM`

## 目录结构

```text
video-toAI-md-pdf-main/
├─ app.py                     # Flask 入口
├─ video_analyzer_agent.py    # 视频分析核心逻辑
├─ requirements.txt           # Python 依赖
├─ package.json               # 前端依赖与脚本
├─ vite.config.js             # Vite 配置（root=static）
├─ templates/
│  └─ index.html              # Flask 模板（自动切换 dev/prod 前端资源）
├─ static/
│  ├─ App.vue                 # Vue 单文件组件
│  ├─ app.js                  # Vite 前端入口
│  ├─ main.css                # 全局样式
│  └─ dist/                   # Vite 构建产物
├─ uploads/                   # 上传目录
├─ outputs/                   # 输出目录
└─ history.json               # 历史记录
```

## 环境要求

- Python `3.8+`（建议 `3.10+`）
- Node.js `18+`（建议 `20+`）
- 建议可访问 Python 包源（用于安装 `ffmpeg-python` 与 `imageio-ffmpeg`）
- 可用的 `ARK_API_KEY`

## 安装依赖

```powershell
pip install -r requirements.txt
npm install
```

## 环境变量

<!-- - `ARK_API_KEY`：必填，后端分析模型调用使用。 -->
<!-- - `VITE_DEV_SERVER`：可选，仅开发模式需要，用于告诉 Flask 从 Vite 开发服务器加载前端资源。 -->

PowerShell 示例：

```powershell
# $env:ARK_API_KEY="你的ark_key"
# $env:VITE_DEV_SERVER="http://127.0.0.1:5173"
```

## ffmpeg 运行机制

- 截图链路优先使用 `ffmpeg-python`。
- 程序会优先尝试 `imageio-ffmpeg` 提供的 ffmpeg 二进制，并自动注入运行时 PATH。
- 若 `imageio-ffmpeg` 不可用，会自动回退到系统 `ffmpeg`。
- 若两者都不可用，截图步骤会失败，进而影响文档图片与部分分析结果。

## 启动方式

### 1) 开发模式（推荐）

开发模式需要两个终端同时运行：

终端 A（前端热更新）：

```powershell
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

终端 B（后端服务）：

```powershell
# $env:VITE_DEV_SERVER="http://127.0.0.1:5173"
python app.py
```

浏览器访问：

`http://127.0.0.1:5000`

### 2) 生产模式（本地构建后运行）

先构建前端，再仅启动 Flask：

```powershell
npm run build
Remove-Item Env:VITE_DEV_SERVER -ErrorAction SilentlyContinue
python app.py
```

浏览器访问：

`http://127.0.0.1:5000`

## 只启动 app.py 可以吗？

- 开发模式：不可以。需要同时启动 Vite（否则模板引用的前端资源不可用）。
- 生产模式：可以。前提是已经执行 `npm run build`，并且 `static/dist/app.js` 存在。

## 常见问题

### 找不到 `127.0.0.1` 页面

- 确认 `python app.py` 是否正常启动（默认端口 `5000`）。
- 若在开发模式，确认 `npm run dev` 也在运行（默认端口 `5173`）。
- 检查是否访问了正确地址：`http://127.0.0.1:5000`。

### 页面空白或前端资源 404

- 开发模式：确认 `VITE_DEV_SERVER` 值与 Vite 端口一致。
- 生产模式：确认已执行 `npm run build`，并生成 `static/dist/app.js`。

### `whisper` 或 `ffmpeg` 相关错误

- 优先确认已安装 Python 依赖：`pip install -r requirements.txt`。
- 若网络/代理受限，`imageio-ffmpeg` 可能安装失败，此时需安装系统 `ffmpeg` 并加入 PATH。
- 使用 `whisper --help` 和 `ffmpeg -version` 做基础自检。

### `ARK_API_KEY` 未设置

- 在当前终端执行：

```powershell
$env:ARK_API_KEY="你的ark_key"
python app.py
```

## 常用命令

```powershell
npm run dev
npm run build
npm run preview
python app.py
```

## 说明

本项目当前主要用于学习与内部验证场景，建议在可控环境中使用。
