# 视频转文档 - AI 视频操作总结生成器

将视频通过 AI 自动转换为带截图、分步骤的 Markdown/PDF 操作指南。

## 功能特点

- **字幕驱动分析** - Whisper 提取语音转字幕，AI 分析字幕识别操作步骤（低成本、快速）
- **视频上传分析** - 直接看画面识别（上传视频给 AI 更准确、费用较高）
- **AI 看图增强** - 对低自信度步骤进行截图分析，修正描述
- **联网搜索增强** - 自动搜索相关信息，丰富文档内容
- **批量处理** - 支持一次性处理多个视频文件
- **多格式输出** - 支持 Markdown 和 PDF 格式
- **Web 界面** - 可视化操作界面，支持拖拽上传
- **历史记录** - 自动保存处理历史，支持查看和重新加载
- **步骤编辑** - 支持编辑、删除、拖拽排序步骤，重新生成文档

## 支持格式

- **视频**: mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg, 3gp, ts, m2ts
- **输出**: Markdown (.md), PDF (.pdf)

## 项目结构

```
video-to-doc/
├── app.py                      # Flask Web 应用主程序
├── video_analyzer_agent.py     # 视频分析 AI Agent 核心模块
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量配置（需创建）
├── templates/
│   └── index.html              # Web 界面 HTML
├── static/
│   └── main.css                # 样式文件
├── uploads/                    # 上传的视频文件
├── outputs/                    # 生成的文档和截图
└── history.json               # 历史记录
```

## 工作流程

1. **Whisper 字幕提取** — 从视频提取语音转文字（带时间戳）
2. **AI 分析步骤** — 识别操作步骤、最佳截图时间点、自信度评分
3. **FFmpeg 截图** — 根据时间点截取视频画面
4. **AI 看图增强** — 对低自信度步骤（最多 4 个）看图修正描述
5. **生成文档** — AI 生成 Markdown 操作文档
6. **PDF 转换** — 转换为 PDF（截图自动嵌入）

## 环境要求

- Python 3.8+
- ffmpeg（需添加到系统 PATH）
- 火山引擎 ARK API Key

## 配置说明

### 1. 安装 ffmpeg

- 下载 ffmpeg: https://ffmpeg.org/download.html
- 解压后将 `bin` 目录添加到系统 PATH 环境变量

```

### 2. 安装 Whisper

```bash
pip install openai-whisper

```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Web 界面

```bash
python app.py
```

访问 http://localhost:5000

### 3. 使用 Web 界面

1. 输入火山引擎 ARK API Key(目前仅支持 doubao-seed-2-0-pro)
2. 选择 Whisper 字幕模型（默认 base）
3. 可选配置：
   - 开启「视频上传模式」直接上传视频给 AI 分析
   - 开启「联网搜索增强」自动搜索相关信息
   - 调整「AI 看图增强次数」
4. 上传视频文件
5. 点击「开始分析」
6. 分析完成后可编辑步骤、下载文档

## Whisper 模型

| 模型 | 大小 | 速度 | 精度 |
|------|------|------|------|
| tiny | ~75 MB | 最快 | 较低 |
| base | ~140 MB | 快 | 中等 |
| small | ~500 MB | 中等 | 较好 |
| medium | ~1.5 GB | 较慢 | 高 |
| large | ~3 GB | 最慢 | 最高 |

## 输出结构

```
outputs/
├── video_name/
│   ├── video_name.mp4        # 原始视频
│   ├── video_name.srt        # 字幕文件
│   ├── images/
│   │   ├── step_01.jpg
│   │   └── step_02.jpg
│   ├── steps.json           # 步骤数据
│   ├── operation_guide.md   # Markdown 文档
│   └── operation_guide.pdf  # PDF 文档
```

## 两种模式对比

| 特性 | 字幕驱动 | 视频上传 |
|------|---------|---------|
| 费用 | 低 | 高 |
| 速度 | 快 | 较慢 |
| 准确度 | 中等 | 高 |
| 适用 | 教学视频 | 复杂操作 |

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/upload` | POST | 上传视频 |
| `/analyze` | POST | 分析视频 |
| `/analyze_batch` | POST | 批量分析 |
| `/regenerate` | POST | 重新生成文档 |
| `/history` | GET | 历史记录列表 |
| `/download_zip` | POST | 下载 ZIP |

## 注意事项

1. 视频需有清晰语音解说效果最佳
2. 联网搜索需在火山引擎控制台开通：https://console.volcengine.com/common-buy/CC_content_plugin
3. 使用视频上传模式时会消耗更多 API 配额
4. 建议首次使用时先试用字幕驱动模式(默认)，效果满意后再考虑视频上传模式

## 常见问题

### Q: 提示 "Whisper 字幕生成失败"？
A: 确保已正确安装 ffmpeg 并添加到系统 PATH。运行 `ffmpeg -version` 验证安装。

### Q: 提示 "ARK_API_KEY 未设置"？
A: 需要在 Web 界面输入 API Key
### Q: 联网搜索功能报错？
A: 需在火山引擎控制台开通联网搜索功能：https://console.volcengine.com/common-buy/CC_content_plugin

### Q: PDF 中文显示为方块？
A: 系统需要安装中文字体。项目会自动尝试使用 `msyh.ttc`（微软雅黑）或 `simsun.ttc`（宋体）。

## 致谢
感谢赞助商 浩嵐传媒 荘总 赞助支持

本项目基于 https://github.com/lxfater/video-to-doc 改造而来。原项目实现了视频转学习笔记的基本功能，本项目在此基础上进行了以下改进：

- 新增 多视频批处理流程
- 新增 分析后的文档历史记录列表
- 新增 编辑识别步骤功能
- 新增 更多可分析的视频格式
- 新增 Web操作界面，简化了使用流程
- 新增 一键下载总结文档
