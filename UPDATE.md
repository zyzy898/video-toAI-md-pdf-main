# 更新文档

## 2026-03-09

### 本次更新概览

- 统一前端为 `Vue 3` 单文件组件方案（`static/App.vue`）。
- 在现有 Flask 项目中接入 `Vite` 工程化构建能力。
- 新增/完善项目文档，补齐启动流程与排错说明。

### 前端与构建

- 新增 Vite 配置：`vite.config.js`
  - `root` 指向 `static/`
  - 开发时 `base=/`
  - 构建时 `base=/static/dist/`
  - 构建入口为 `static/app.js`
  - 输出目录为 `static/dist/`
- 前端入口调整为：
  - `static/App.vue`（页面主组件）
  - `static/app.js`（Vite 启动入口）
- `package.json` 脚本更新：
  - `npm run dev`
  - `npm run build`
  - `npm run preview`

### Flask 集成

- `templates/index.html` 支持按环境自动切换前端资源：
  - 开发模式通过 `VITE_DEV_SERVER` 加载 Vite Dev Server（含 `@vite/client`）。
  - 生产模式加载 `static/dist/app.js`。
- `app.py` 增加 `VITE_DEV_SERVER` 读取逻辑并传入模板。

### 启动流程（结论）

- 开发模式：需要同时启动 2 个进程（`npm run dev` + `python app.py`）。
- 生产模式：先 `npm run build`，然后只启动 `python app.py`。

### 文档维护

- `README.md` 已重写：
  - 项目结构与依赖说明
  - 开发/生产完整启动命令
  - “只启动 app.py 是否可行”的明确结论
  - 常见问题排查（127.0.0.1 无法访问、资源 404、环境变量缺失等）

## 2026-03-09（补充）

### Python 依赖改造（ffmpeg 链路）

- `requirements.txt` 新增：
  - `ffmpeg-python>=0.2.0`
  - `imageio-ffmpeg>=0.5.1`
- 保留 `openai-whisper`，继续用于字幕生成。

### 截图能力升级

- 新增运行时 ffmpeg 准备逻辑：
  - 优先使用 `imageio-ffmpeg` 自带二进制
  - 自动注入运行时 PATH
  - 不可用时回退系统 `ffmpeg`
- 增加兼容兜底：
  - 若 `ffmpeg-python` 未安装，自动回退命令行调用，避免程序直接崩溃。

### 工程细节

- 新增运行时目录忽略：`.runtime_bin`（见 `.gitignore`）。

### 文档同步

- `README.md` 已补充：
  - ffmpeg 运行机制说明
  - `whisper/ffmpeg` 相关错误排查更新
