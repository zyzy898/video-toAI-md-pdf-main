import os
import json
import asyncio
import logging
import subprocess
import re
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from volcenginesdkarkruntime import AsyncArk
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

try:
    import ffmpeg
except Exception:  # pragma: no cover - 兜底兼容
    ffmpeg = None

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoAnalyzerAgent:
    FONT_PATHS = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\SIMSUN.TTC",
    ]

    def __init__(self, api_key: str = None, whisper_model: str = "base"):
        """
        初始化视频分析AI Agent
        :param api_key: 火山引擎ARK API Key，如果为None则从.env文件读取
        :param whisper_model: Whisper 模型名称，默认 "base"
        """
        load_dotenv()

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("ARK_API_KEY")
            if not self.api_key:
                raise ValueError("ARK_API_KEY 未设置，请在.env文件中设置或通过参数传入")

        self.client = AsyncArk(
            base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=self.api_key
        )
        self.model = "doubao-seed-2-0-pro-260215"
        self.whisper_model = whisper_model
        self.ffmpeg_cmd = self._prepare_ffmpeg_command()

    def _prepare_ffmpeg_command(self) -> str:
        """
        优先使用 imageio-ffmpeg 提供的二进制并注入 PATH，
        这样无需手工安装系统级 ffmpeg。
        """
        try:
            import imageio_ffmpeg
        except Exception as exc:
            logging.warning("imageio-ffmpeg 不可用，回退到系统 ffmpeg: %s", exc)
            return "ffmpeg"

        ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
        if not ffmpeg_exe.exists():
            logging.warning("imageio-ffmpeg ffmpeg 路径无效，回退到系统 ffmpeg: %s", ffmpeg_exe)
            return "ffmpeg"

        shim_dir = Path(__file__).resolve().parent / ".runtime_bin"
        shim_dir.mkdir(parents=True, exist_ok=True)

        if os.name == "nt":
            shim_path = shim_dir / "ffmpeg.cmd"
            shim_content = f'@echo off\r\n"{ffmpeg_exe}" %*\r\n'
        else:
            shim_path = shim_dir / "ffmpeg"
            shim_content = f'#!/usr/bin/env sh\nexec "{ffmpeg_exe}" "$@"\n'

        existing_content = ""
        if shim_path.exists():
            existing_content = shim_path.read_text(encoding="utf-8", errors="ignore")
        if existing_content != shim_content:
            shim_path.write_text(shim_content, encoding="utf-8")
        if os.name != "nt":
            shim_path.chmod(0o755)

        current_path = os.environ.get("PATH", "")
        path_parts = current_path.split(os.pathsep) if current_path else []
        shim_dir_str = str(shim_dir)
        if shim_dir_str not in path_parts:
            os.environ["PATH"] = shim_dir_str + (os.pathsep + current_path if current_path else "")

        logging.info("ffmpeg 二进制已就绪: %s", ffmpeg_exe)
        return str(ffmpeg_exe)

    def _extract_response_text(self, response) -> str:
        """从模型响应中提取文本内容"""
        for item in response.output:
            if (
                hasattr(item, "role")
                and item.role == "assistant"
                and hasattr(item, "content")
            ):
                for content_item in item.content:
                    if hasattr(content_item, "text"):
                        return content_item.text
        return ""

    async def _call_api_with_retry(self, api_func, *args, **kwargs):
        """API 调用重试逻辑"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return await api_func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(
                        f"  请求频率过快，等待 {wait_time} 秒后重试 ({attempt + 1}/{max_retries})..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise

    def _strip_code_fence(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _extract_json_fragment(
        self, text: str, opener: str, closer: str
    ) -> Optional[str]:
        start = text.find(opener)
        end = text.rfind(closer)
        if start == -1 or end == -1 or end <= start:
            return None
        return text[start : end + 1]

    def _parse_json_response(self, result: str) -> List[Dict]:
        """解析 JSON 响应"""
        cleaned = self._strip_code_fence(result)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            json_fragment = self._extract_json_fragment(cleaned, "[", "]")
            if not json_fragment:
                raise ValueError(f"无法解析模型返回的JSON格式: {result}")
            parsed = json.loads(json_fragment)

        if not isinstance(parsed, list):
            raise ValueError(f"JSON 格式不是数组: {type(parsed).__name__}")
        return parsed

    def _parse_json_object_response(self, result: str) -> Dict[str, Any]:
        cleaned = self._strip_code_fence(result)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            json_fragment = self._extract_json_fragment(cleaned, "{", "}")
            if not json_fragment:
                raise ValueError(f"无法解析模型返回的JSON对象: {result}")
            parsed = json.loads(json_fragment)

        if not isinstance(parsed, dict):
            raise ValueError(f"JSON 格式不是对象: {type(parsed).__name__}")
        return parsed

    def _parse_timestamp(self, time_str: str) -> int:
        """解析时间字符串为秒数"""
        parts = [int(part) for part in time_str.split(":")]
        if len(parts) == 2:
            minutes, seconds = parts
            return minutes * 60 + seconds
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        raise ValueError(f"不支持的时间格式: {time_str}")

    # ========== Whisper 字幕生成 ==========

    def generate_subtitles(self, video_path: str, output_dir: str = ".") -> str:
        """
        调用本地 whisper 命令行从视频生成 SRT 字幕文件
        :param video_path: 视频文件路径
        :param output_dir: 字幕输出目录
        :return: 生成的 SRT 文件路径
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "whisper",
            str(video_path),
            "--model",
            self.whisper_model,
            "--language",
            "zh",
            "--output_format",
            "srt",
            "--output_dir",
            str(output_dir),
        ]
        print(f"正在使用 Whisper ({self.whisper_model}) 生成字幕...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Whisper 字幕生成失败: {result.stderr}")

        # whisper 输出文件名为 视频文件名.srt
        srt_filename = Path(video_path).stem + ".srt"
        srt_path = output_dir / srt_filename

        if not srt_path.exists():
            raise FileNotFoundError(f"Whisper 未生成字幕文件: {srt_path}")

        print(f"字幕已生成: {srt_path}")
        return str(srt_path)

    # ========== 字幕分析：识别操作步骤（默认模式，纯文本，便宜） ==========

    async def analyze_subtitles(self, srt_path: str) -> List[Dict]:
        """
        通过分析字幕文本识别操作步骤（Chat Completions API，纯文本调用）
        :param srt_path: SRT字幕文件路径
        :return: 操作步骤列表
        """
        subtitles = self.parse_srt(srt_path)
        subtitle_text = "\n".join(
            [
                f"[{sub['start_time']} --> {sub['end_time']}] {sub['text']}"
                for sub in subtitles
            ]
        )

        system_prompt = """你是一个专业的操作视频分析助手。我会给你一段操作视频的字幕内容（带时间戳），请根据字幕的语义分析出视频中展示的所有操作步骤。

对于每个步骤，请提供：
1. step: 步骤编号（从1开始）
2. time: 该步骤最关键的时间点，格式为 "MM:SS"（选择该步骤中最能代表操作内容的一句话对应的时间）
3. title: 步骤标题（简洁，5-15个字）
4. description: 详细的操作说明（描述具体如何操作，30-100个字）
5. confidence: 你对这个步骤识别的自信度（0.0-1.0），评判标准：
   - 1.0: 字幕明确描述了具体操作，非常确定
   - 0.7-0.9: 字幕大致能推断操作，但细节不够清晰
   - 0.4-0.6: 字幕模糊，需要看画面才能确认具体操作
   - 0.0-0.3: 几乎无法从字幕判断，纯靠猜测

请按照以下JSON格式输出：
[
    {
        "step": 1,
        "time": "00:15",
        "title": "打开设置页面",
        "description": "点击屏幕左上角的菜单图标，在弹出的侧边栏中选择「设置」选项，进入系统设置页面。",
        "confidence": 0.9
    }
]

注意：
- 步骤数量没有限制，有多少步就输出多少步，不要人为合并或凑数，完全根据字幕内容如实拆分,当视频长度越长时拆分的越多，最多次数为10次，最少次数为1次。
- 时间格式必须为 "MM:SS"
- 根据字幕语义判断步骤的起止范围，time 取该步骤中最关键操作的时间点
- description 要具体、可操作，结合字幕内容让读者能照着做
- confidence 要诚实评估，不确定的地方就给低分
- 只输出JSON，不要添加其他文字"""

        user_prompt = f"""以下是操作视频的字幕内容：

{subtitle_text}

请分析字幕，识别出所有操作步骤。"""

        print("正在通过字幕分析识别操作步骤...")

        async def call_api():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

        response = await self._call_api_with_retry(call_api)
        result = response.choices[0].message.content
        steps = self._parse_json_response(result)

        return steps

    # ========== 视频分析：识别操作步骤（可选增强模式，上传视频，较贵） ==========

    async def analyze_video(
        self, video_path: str, fps: float = 1.0, file_id: str = None
    ) -> List[Dict]:
        """
        分析视频，识别操作步骤
        :param video_path: 视频文件路径
        :param fps: 抽帧频率，默认1帧/秒
        :param file_id: 已上传的文件ID（可选，跳过上传）
        :return: 操作步骤列表
        """
        system_prompt = """你是一个专业的操作视频分析助手。请仔细观看上传的视频，识别出视频中展示的所有操作步骤。

对于每个步骤，请提供：
1. step: 步骤编号（从1开始）
2. time: 该步骤画面最具代表性的时间点（用于截图）
3. title: 步骤标题（简洁，5-15个字）
4. description: 详细的操作说明（描述具体如何操作，30-100个字）

请按照以下JSON格式输出：
[
    {
        "step": 1,
        "time": "00:15",
        "title": "打开设置页面",
        "description": "点击屏幕左上角的菜单图标，在弹出的侧边栏中选择「设置」选项，进入系统设置页面。"
    },
    {
        "step": 2,
        "time": "00:42",
        "title": "修改用户名",
        "description": "在设置页面中找到「个人信息」区域，点击用户名右侧的编辑按钮，输入新的用户名后点击保存。"
    }
]

注意：
- 时间格式必须为 "MM:SS"
- 选择每个步骤中最能展示操作内容的画面时间点
- description 要具体、可操作，让读者能照着做
- 只输出JSON，不要添加其他文字"""

        try:
            if not file_id:
                print(f"正在上传视频: {video_path}")
                with open(video_path, "rb") as f:
                    file = await self.client.files.create(
                        file=f,
                        purpose="user_data",
                        preprocess_configs={"video": {"fps": fps}},
                    )
                file_id = file.id
                print(f"视频上传成功，File ID: {file_id}")

                await self.client.files.wait_for_processing(file_id)
                print(f"文件处理完成: {file_id}")
            else:
                print(f"使用已上传的文件: {file_id}")

            # 调用模型分析视频（带重试）
            print("正在分析视频，识别操作步骤...")

            async def call_api():
                return await self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_video", "file_id": file_id},
                                {
                                    "type": "input_text",
                                    "text": "请分析这个操作视频，识别出所有操作步骤",
                                },
                            ],
                        },
                    ],
                )

            response = await self._call_api_with_retry(call_api)
            result = self._extract_response_text(response)
            steps = self._parse_json_response(result)

            return steps

        except Exception as e:
            print(f"分析视频时出错: {e}")
            return []

    # ========== 截图生成 ==========

    def generate_screenshot(
        self, video_path: Path, output_dir: Path, timestamp: int, step_num: int = None
    ) -> Optional[Path]:
        """
        使用 ffmpeg-python 生成截图
        :param step_num: 步骤编号，如果提供则使用 step_XX 命名
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if step_num is not None:
            filename = f"step_{step_num:02d}.jpg"
        else:
            mm = timestamp // 60
            ss = timestamp % 60
            filename = f"screenshot_{mm:02d}_{ss:02d}.jpg"

        output_path = output_dir / filename

        logging.info("生成截图：step=%s, time=%ss, file=%s", step_num, timestamp, output_path)
        if ffmpeg is None:
            logging.warning("ffmpeg-python 未安装，回退到命令行 ffmpeg。")
            cmd = [
                self.ffmpeg_cmd,
                "-ss",
                str(timestamp),
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output_path),
                "-y",
            ]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if result.returncode != 0:
                logging.warning(
                    "截图失败：step=%s, time=%ss, rc=%s, stderr=%s",
                    step_num,
                    timestamp,
                    result.returncode,
                    (result.stderr or "").strip()[-240:],
                )
                return None
        else:
            try:
                (
                    ffmpeg.input(str(video_path), ss=max(0, int(timestamp)))
                    .output(str(output_path), vframes=1, **{"q:v": 2})
                    .overwrite_output()
                    .run(
                        cmd=self.ffmpeg_cmd,
                        capture_stdout=True,
                        capture_stderr=True,
                        quiet=True,
                    )
                )
            except ffmpeg.Error as exc:
                stderr_text = ""
                if exc.stderr:
                    stderr_text = exc.stderr.decode("utf-8", errors="ignore").strip()[-240:]
                logging.warning(
                    "截图失败：step=%s, time=%ss, stderr=%s",
                    step_num,
                    timestamp,
                    stderr_text,
                )
                return None
            except Exception as exc:
                logging.warning("截图异常：step=%s, time=%ss, err=%s", step_num, timestamp, exc)
                return None

        if not output_path.exists():
            logging.warning("截图失败：step=%s, time=%ss, 输出文件不存在", step_num, timestamp)
            return None
        return output_path

    def generate_screenshots_from_steps(
        self,
        video_path: str,
        steps: List[Dict],
        output_dir: str = "images",
        max_workers: Optional[int] = None,
    ) -> List[Path]:
        """
        根据步骤列表批量生成截图
        :return: 截图文件路径列表
        """
        video_path = Path(video_path)
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        screenshot_tasks = []
        for idx, step in enumerate(steps, start=1):
            time_str = step.get("time")
            if not time_str:
                logging.warning(f"步骤缺少 'time' 字段，跳过: {step}")
                continue

            try:
                timestamp = self._parse_timestamp(str(time_str))
            except (TypeError, ValueError) as e:
                logging.warning(f"时间格式错误 {time_str}: {e}，跳过")
                continue

            try:
                step_num = int(step.get("step", idx))
            except (TypeError, ValueError):
                step_num = idx
            screenshot_tasks.append((step_num, timestamp))

        if not screenshot_tasks:
            return []

        if max_workers is None:
            max_workers = min(4, os.cpu_count() or 2)
        max_workers = max(1, min(max_workers, len(screenshot_tasks)))

        screenshot_paths: List[Path] = []
        if max_workers == 1:
            for step_num, timestamp in screenshot_tasks:
                screenshot_path = self.generate_screenshot(
                    video_path, output_dir_path, timestamp, step_num=step_num
                )
                if screenshot_path:
                    screenshot_paths.append(screenshot_path)
                    print(f"已生成截图: {screenshot_path}")
            return screenshot_paths

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(
                    self.generate_screenshot,
                    video_path,
                    output_dir_path,
                    timestamp,
                    step_num,
                ): step_num
                for step_num, timestamp in screenshot_tasks
            }

            for future in as_completed(future_map):
                step_num = future_map[future]
                screenshot_path = future.result()
                if screenshot_path:
                    screenshot_paths.append(screenshot_path)
                    print(f"已生成截图: {screenshot_path}")
                else:
                    logging.warning("步骤 %s 截图生成失败", step_num)

        screenshot_paths.sort(key=lambda p: p.name)

        return screenshot_paths

    # ========== AI 看图增强（低自信度步骤） ==========

    async def enhance_steps_with_vision(
        self,
        steps: List[Dict],
        image_dir: str,
        srt_path: str = None,
        max_calls: int = 10,
    ) -> List[Dict]:
        """
        对低自信度的步骤，调用 AI 看截图来增强描述
        :param steps: 步骤列表（含 confidence）
        :param image_dir: 截图目录
        :param srt_path: SRT字幕文件（可选，提供对应时间段的字幕给 AI 参考）
        :param max_calls: 最多调用 AI 看图的次数
        :return: 增强后的步骤列表
        """
        # 按 confidence 排序，取最低的 max_calls 个
        steps_with_idx = [(i, step) for i, step in enumerate(steps)]
        steps_with_idx.sort(key=lambda x: x[1].get("confidence", 1.0))
        to_enhance = steps_with_idx[:max_calls]

        # 解析字幕备用
        subtitles = []
        if srt_path and os.path.exists(srt_path):
            subtitles = self.parse_srt(srt_path)

        print(
            f"将对 {len(to_enhance)} 个低自信度步骤进行 AI 看图增强（最多 {max_calls} 次）"
        )

        for idx, step in to_enhance:
            step_num = step.get("step", idx + 1)
            confidence = step.get("confidence", 0)
            img_path = Path(image_dir) / f"step_{step_num:02d}.jpg"

            if not img_path.exists():
                print(f"  步骤{step_num}: 截图不存在，跳过")
                continue

            if not step.get("title") or not step.get("description"):
                print(f"  步骤{step_num}: 缺少 title 或 description，跳过")
                continue

            # 读取图片转 base64
            with open(img_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
            img_data_url = f"data:image/jpeg;base64,{img_base64}"

            # 提取该步骤时间段内的字幕
            step_subtitle = ""
            if subtitles:
                time_str = step.get("time", "00:00")
                try:
                    step_seconds = self._parse_timestamp(str(time_str))
                except (TypeError, ValueError):
                    step_seconds = 0
                nearby = [
                    s for s in subtitles if abs(s["start_seconds"] - step_seconds) < 30
                ]
                if nearby:
                    step_subtitle = "\n".join(
                        [f"[{s['start_time']}] {s['text']}" for s in nearby]
                    )

            user_content = [
                {
                    "type": "text",
                    "text": f"这是操作视频第{step_num}步的截图。\n\n当前字幕分析结果：\n- 标题：{step.get('title', '未知')}\n- 描述：{step.get('description', '未知')}\n- 自信度：{confidence}",
                },
                {"type": "image_url", "image_url": {"url": img_data_url}},
            ]
            if step_subtitle:
                user_content.append(
                    {"type": "text", "text": f"\n该时间段附近的字幕：\n{step_subtitle}"}
                )
            user_content.append(
                {
                    "type": "text",
                    "text": '\n请根据截图画面，修正或补充这个步骤的标题和描述。只输出JSON，格式：{"title": "...", "description": "..."}',
                }
            )

            print(f"  步骤{step_num} (confidence={confidence:.1f}): AI 看图分析中...")

            max_retries = 5
            response = None
            for attempt in range(max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "你是一个专业的操作视频分析助手。请根据截图画面内容，修正或补充操作步骤的标题和描述。描述要具体、准确、可操作。只输出JSON。",
                            },
                            {"role": "user", "content": user_content},
                        ],
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        print(f"    请求频率过快，等待 {wait_time} 秒后重试...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"    AI 看图失败: {e}，保留原始结果")
                        break

            if response is None:
                continue

            try:
                result = response.choices[0].message.content
                enhanced = self._parse_json_object_response(result)

                old_title = steps[idx]["title"]
                steps[idx]["title"] = enhanced.get("title", steps[idx]["title"])
                steps[idx]["description"] = enhanced.get(
                    "description", steps[idx]["description"]
                )
                steps[idx]["enhanced"] = True
                print(f"    ✓ 已增强: 「{old_title}」→「{steps[idx]['title']}」")
            except Exception as e:
                print(f"    解析增强结果失败: {e}，保留原始结果")

        return steps

    # ========== 步骤操作文档生成 ==========

    async def generate_step_document(
        self,
        steps: List[Dict],
        output_path: str = "operation_guide.md",
        srt_path: str = None,
        image_dir: str = "images",
        web_search: bool = False,
    ) -> str:
        """
        生成步骤操作文档（Markdown格式）
        :param steps: AI识别出的步骤列表
        :param output_path: 输出文件路径
        :param srt_path: SRT字幕文件路径（可选，用于补充文字内容）
        :param image_dir: 截图目录
        :param web_search: 是否启用联网搜索增强
        """
        # 准备字幕信息（如果有）
        subtitle_text = ""
        if srt_path and os.path.exists(srt_path):
            subtitles = self.parse_srt(srt_path)
            subtitle_text = "\n".join(
                [f"[{sub['start_time']}] {sub['text']}" for sub in subtitles]
            )

        # 准备步骤和截图的对应关系
        steps_info = json.dumps(steps, ensure_ascii=False, indent=2)

        # 构建截图列表（发送给 AI 时使用路径占位符）
        screenshot_list = []
        for step in steps:
            step_num = step.get("step", 0)
            filename = f"step_{step_num:02d}.jpg"
            screenshot_list.append(
                f"步骤{step_num}: ![步骤{step_num}截图]({image_dir}/{filename})"
            )

        if web_search:
            system_prompt = """你是一个专业的技术文档编写专家。请根据提供的操作步骤信息、截图和字幕内容，生成一份清晰、专业的步骤操作文档。

你拥有联网搜索能力，请主动搜索以下内容来丰富文档：
- 视频中涉及的软件/平台/工具的官方介绍和功能说明
- 相关的最佳实践、使用技巧或注意事项
- 专业术语的准确解释

要求：
1. 使用 Markdown 格式
2. 每个步骤包含：标题（## 步骤 X：标题）、截图、详细操作说明
3. 操作说明要具体、准确，让读者能照着操作
4. 结合联网搜索到的信息，补充更丰富的上下文（如软件介绍、功能说明、注意事项等）
5. 如果有字幕内容，结合字幕让描述更加准确和详细
6. 在文档开头添加一个简短的概述（可结合搜索到的产品介绍）
7. 保持语言简洁专业
8. 在文档末尾添加「## 参考资料」章节，列出所有搜索引用的信息来源（标题+链接）
9. 直接返回 Markdown 内容，不要添加其他说明"""
        else:
            system_prompt = """你是一个专业的技术文档编写专家。请根据提供的操作步骤信息、截图和字幕内容，生成一份清晰、专业的步骤操作文档。

要求：
1. 使用 Markdown 格式
2. 每个步骤包含：标题（## 步骤 X：标题）、截图、详细操作说明
3. 操作说明要具体、准确，让读者能照着操作
4. 如果有字幕内容，结合字幕让描述更加准确和详细
5. 在文档开头添加一个简短的概述
6. 保持语言简洁专业
7. 直接返回 Markdown 内容，不要添加其他说明"""

        user_prompt = f"""操作步骤信息：
{steps_info}

截图对应关系：
{chr(10).join(screenshot_list)}
"""
        if subtitle_text:
            user_prompt += f"""
视频字幕内容（供参考）：
{subtitle_text}
"""
        if web_search:
            user_prompt += "\n请先联网搜索相关信息，然后生成完整的步骤操作文档。"
        else:
            user_prompt += "\n请生成完整的步骤操作文档。"

        if web_search:
            print("正在调用 AI 生成步骤操作文档（联网搜索增强）...")

            async def call_api():
                return await self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    tools=[{"type": "web_search"}],
                )

            response = await self._call_api_with_retry(call_api)
            markdown_content = self._extract_response_text(response)
        else:
            print("正在调用 AI 生成步骤操作文档...")

            async def call_api():
                return await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )

            response = await self._call_api_with_retry(call_api)
            markdown_content = response.choices[0].message.content

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"步骤操作文档已保存到: {output_path}")
        return output_path

    # ========== PDF 生成 ==========

    def generate_pdf(self, md_path: str, pdf_path: str = None) -> str:
        """
        将 Markdown 文档转换为 PDF（图片嵌入）
        :param md_path: Markdown 文件路径
        :param pdf_path: PDF 输出路径（默认同名 .pdf）
        :return: PDF 文件路径
        """
        import markdown
        from fpdf import FPDF, XPos, YPos

        if not pdf_path:
            pdf_path = str(Path(md_path).with_suffix(".pdf"))

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        html_body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

        font_paths = self.FONT_PATHS
        chinese_font_added = False
        font_family = "helvetica"

        for fp in font_paths:
            if Path(fp).exists():
                font_family = "Chinese"
                break

        class PDF(FPDF):
            def header(self):
                self.set_font(font_family, "B", 15)
                self.cell(0, 10, "Video Analysis", border=False, align="C")
                self.ln(20)

        pdf = PDF()

        for fp in font_paths:
            if Path(fp).exists():
                try:
                    pdf.add_font("Chinese", "", fp)
                    pdf.add_font("Chinese", "B", fp)
                    chinese_font_added = True
                    break
                except Exception:
                    continue

        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        import re
        from html import unescape

        def parse_html_to_pdf(html_text: str):
            temp_text = re.sub(
                r"<h1[^>]*>(.*?)</h1>", r"\n=== \1 ===\n", html_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<h2[^>]*>(.*?)</h2>", r"\n== \1 ==\n", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<h3[^>]*>(.*?)</h3>", r"\n= \1 =\n", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<p[^>]*>(.*?)</p>", r"\1\n", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(r"<br\s*/?>", r"\n", temp_text, flags=re.IGNORECASE)
            temp_text = re.sub(
                r"<strong[^>]*>(.*?)</strong>", r"**\1**", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<b[^>]*>(.*?)</b>", r"**\1**", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<em[^>]*>(.*?)</em>", r"*\1*", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<i[^>]*>(.*?)</i>", r"*\1*", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<code[^>]*>(.*?)</code>", r"`\1`", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(r"<table[^>]*>", r"", temp_text, flags=re.DOTALL)
            temp_text = re.sub(r"</table>", r"", temp_text)
            temp_text = re.sub(r"<tr>", r"", temp_text)
            temp_text = re.sub(r"</tr>", r"\n", temp_text)
            temp_text = re.sub(
                r"<td[^>]*>(.*?)</td>", r"\1 | ", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(
                r"<th[^>]*>(.*?)</th>", r"**\1** | ", temp_text, flags=re.DOTALL
            )
            temp_text = re.sub(r"<thead[^>]*>", r"", temp_text, flags=re.DOTALL)
            temp_text = re.sub(r"</thead>", r"", temp_text)
            temp_text = re.sub(r"<tbody[^>]*>", r"", temp_text, flags=re.DOTALL)
            temp_text = re.sub(r"</tbody>", r"", temp_text)
            temp_text = re.sub(
                r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
                r"[Image: \1]",
                temp_text,
                flags=re.DOTALL,
            )
            temp_text = re.sub(r"<[^>]+>", r"", temp_text)
            temp_text = unescape(temp_text)
            temp_text = re.sub(r"\n{3,}", r"\n\n", temp_text)
            return temp_text.strip()

        text = parse_html_to_pdf(html_body)
        base_dir = Path(md_path).parent

        current_font = "Chinese" if chinese_font_added else "helvetica"

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue

            if line.startswith("==="):
                title = line.strip("= ").strip()
                pdf.set_font(current_font, "B", 16)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(
                    0, 10, title, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
                pdf.ln(5)
            elif line.startswith("=="):
                title = line.strip("= ").strip()
                pdf.set_font(current_font, "B", 14)
                pdf.set_text_color(44, 62, 80)
                pdf.cell(0, 8, title, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(3)
            elif line.startswith("="):
                title = line.strip("= ").strip()
                pdf.set_font(current_font, "B", 12)
                pdf.set_text_color(60, 60, 60)
                pdf.cell(0, 7, title, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
            elif line.startswith("[Image:"):
                img_match = re.search(r"\[Image: ([^\]]+)\]", line)
                if img_match:
                    img_path = img_match.group(1).strip()
                    img_full_path = base_dir / img_path
                    if img_full_path.exists():
                        try:
                            pdf.image(str(img_full_path), w=170)
                            pdf.ln(3)
                        except Exception:
                            pdf.cell(
                                0,
                                7,
                                f"[图片: {img_path}]",
                                border=False,
                                new_x=XPos.LMARGIN,
                                new_y=YPos.NEXT,
                            )
                    else:
                        pdf.cell(
                            0,
                            7,
                            f"[图片: {img_path}]",
                            border=False,
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
            else:
                pdf.set_font(current_font, "", 10)
                pdf.set_text_color(51, 51, 51)
                pdf.multi_cell(0, 5, line)
                pdf.ln(2)

        pdf.output(pdf_path)

        print(f"PDF 文档已生成: {pdf_path}")
        return pdf_path

    # ========== 工具方法 ==========

    def save_results(self, results: List[Dict], output_path: str):
        """将分析结果保存到JSON文件"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到: {output_path}")

    def parse_srt(self, srt_path):
        """解析srt文件，返回字幕列表"""
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace("\r\n", "\n").replace("\r", "\n")
        subtitle_blocks = re.split(r"\n{2,}", content.strip())
        subtitles = []

        for block in subtitle_blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    time_range = lines[1].strip()
                    text = " ".join(lines[2:])
                    start_time, end_time = [
                        item.strip() for item in time_range.split(" --> ", 1)
                    ]
                    start_seconds = self.time_to_seconds(start_time)
                    subtitles.append(
                        {
                            "index": index,
                            "start_time": start_time,
                            "end_time": end_time,
                            "start_seconds": start_seconds,
                            "text": text,
                        }
                    )
                except Exception:
                    continue

        return subtitles

    def time_to_seconds(self, time_str):
        """将SRT时间字符串转换为秒数"""
        time_str = time_str.strip().replace(".", ",")
        h, m, s = time_str.split(":")
        if "," in s:
            s, ms = s.split(",", 1)
        else:
            ms = "0"
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
