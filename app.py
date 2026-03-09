import asyncio
import json
import logging
import os
import shutil
import traceback
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Callable, Dict, List, Tuple
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from werkzeug.utils import secure_filename

from video_analyzer_agent import VideoAnalyzerAgent

app = Flask(__name__)
app.secret_key = "video-analyzer-secret-key"

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOAD_ROOT = (PROJECT_ROOT / "uploads").resolve()
OUTPUT_ROOT = (PROJECT_ROOT / "outputs").resolve()
HISTORY_PATH = (PROJECT_ROOT / "history.json").resolve()
UPLOAD_SESSION_ROOT = (UPLOAD_ROOT / ".upload_sessions").resolve()

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = str(UPLOAD_ROOT)
app.config["OUTPUT_FOLDER"] = str(OUTPUT_ROOT)

ALLOWED_EXTENSIONS = {
    "mp4",
    "avi",
    "mov",
    "mkv",
    "wmv",
    "flv",
    "webm",
    "m4v",
    "mpg",
    "mpeg",
    "3gp",
    "ts",
    "m2ts",
}
ALLOWED_WHISPER_MODELS = {"tiny", "base", "small", "medium", "large"}
MAX_HISTORY = 50
MAX_VISION_CALLS = 10
FPS_MIN = 0.1
FPS_MAX = 10.0
DEFAULT_UPLOAD_CHUNK_SIZE = 8 * 1024 * 1024
MAX_UPLOAD_CHUNK_SIZE = 32 * 1024 * 1024

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
UPLOAD_SESSION_ROOT.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
history_lock = RLock()
upload_session_lock = RLock()
batch_progress_lock = Lock()
batch_progress: Dict[str, Any] = {
    "total": 0,
    "current": 0,
    "status": "idle",
    "current_file": "",
    "stage": "idle",
    "message": "",
}
single_progress_lock = Lock()
single_progress: Dict[str, Any] = {
    "status": "idle",
    "current_file": "",
    "stage": "idle",
    "message": "",
}


def _update_batch_progress(**kwargs: Any) -> None:
    with batch_progress_lock:
        batch_progress.update(kwargs)


def _update_single_progress(**kwargs: Any) -> None:
    with single_progress_lock:
        single_progress.update(kwargs)


def _vite_dev_server() -> str | None:
    server = os.getenv("VITE_DEV_SERVER", "").strip()
    if not server:
        return None
    return server.rstrip("/")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _safe_int(
    value: Any, default: int, min_value: int | None = None, max_value: int | None = None
) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    if min_value is not None:
        number = max(min_value, number)
    if max_value is not None:
        number = min(max_value, number)
    return number


def _safe_float(
    value: Any,
    default: float,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if min_value is not None:
        number = max(min_value, number)
    if max_value is not None:
        number = min(max_value, number)
    return number


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _json_payload() -> Dict[str, Any]:
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else {}


def _assert_within(path: Path, root: Path, field_name: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{field_name} 不在允许目录内") from exc


def _resolve_upload_filepath(raw_path: Any) -> Path:
    if not raw_path:
        raise ValueError("文件路径不能为空")
    path = Path(str(raw_path)).expanduser().resolve(strict=False)
    _assert_within(path, UPLOAD_ROOT, "filepath")
    if not path.exists() or not path.is_file():
        raise FileNotFoundError("文件不存在")
    return path


def _resolve_output_dir(raw_output_dir: Any, must_exist: bool = True) -> Path:
    if not raw_output_dir:
        raise ValueError("输出目录不能为空")
    candidate = Path(str(raw_output_dir))
    if not candidate.is_absolute():
        candidate = OUTPUT_ROOT / candidate
    output_dir = candidate.expanduser().resolve(strict=False)
    _assert_within(output_dir, OUTPUT_ROOT, "output_dir")
    if must_exist and not output_dir.exists():
        raise FileNotFoundError("输出目录不存在")
    return output_dir


def _read_history_unlocked() -> List[Dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_history_unlocked(history: List[Dict[str, Any]]) -> None:
    tmp_path = HISTORY_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    tmp_path.replace(HISTORY_PATH)


def load_history() -> List[Dict[str, Any]]:
    with history_lock:
        return _read_history_unlocked()


def save_history(record: Dict[str, Any]) -> None:
    with history_lock:
        history = _read_history_unlocked()
        history.insert(0, record)
        _write_history_unlocked(history[:MAX_HISTORY])


def delete_history_record(record_id: str) -> None:
    with history_lock:
        history = _read_history_unlocked()
        history = [r for r in history if r.get("id") != record_id]
        _write_history_unlocked(history)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _build_unique_upload_path(filename: str) -> Path:
    safe_name = secure_filename(filename)
    if not safe_name:
        safe_name = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    candidate = UPLOAD_ROOT / safe_name
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1

    while candidate.exists():
        candidate = UPLOAD_ROOT / f"{stem}_{counter}{suffix}"
        counter += 1

    return candidate


def _normalize_upload_id(raw_upload_id: Any) -> str:
    upload_id = secure_filename(str(raw_upload_id or "")).strip()
    if not upload_id:
        return ""
    if len(upload_id) > 120:
        raise ValueError("upload_id 无效")
    return upload_id


def _upload_session_json_path(upload_id: str) -> Path:
    session_path = (UPLOAD_SESSION_ROOT / f"{upload_id}.json").resolve(strict=False)
    _assert_within(session_path, UPLOAD_SESSION_ROOT, "upload_id")
    return session_path


def _upload_session_temp_path(upload_id: str) -> Path:
    temp_path = (UPLOAD_SESSION_ROOT / f"{upload_id}.part").resolve(strict=False)
    _assert_within(temp_path, UPLOAD_SESSION_ROOT, "upload_id")
    return temp_path


def _normalize_received_chunks(raw_chunks: Any, total_chunks: int) -> List[int]:
    if total_chunks <= 0 or not isinstance(raw_chunks, list):
        return []
    received: set[int] = set()
    for item in raw_chunks:
        idx = _safe_int(item, -1)
        if 0 <= idx < total_chunks:
            received.add(idx)
    return sorted(received)


def _load_upload_session(upload_id: str) -> Dict[str, Any] | None:
    session_path = _upload_session_json_path(upload_id)
    if not session_path.exists():
        return None
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            session = json.load(f)
        return session if isinstance(session, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _save_upload_session(upload_id: str, session: Dict[str, Any]) -> None:
    session_path = _upload_session_json_path(upload_id)
    tmp_path = session_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    tmp_path.replace(session_path)


def _delete_upload_session(upload_id: str) -> None:
    for path in (_upload_session_json_path(upload_id), _upload_session_temp_path(upload_id)):
        if not path.exists():
            continue
        try:
            path.unlink()
        except OSError:
            logger.warning("删除上传会话文件失败: %s", path)


def _create_unique_output_dir(video_path: Path) -> Path:
    base_name = secure_filename(video_path.stem) or "video"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = OUTPUT_ROOT / f"{base_name}_{timestamp}"
    counter = 1

    while candidate.exists():
        candidate = OUTPUT_ROOT / f"{base_name}_{timestamp}_{counter}"
        counter += 1

    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def _normalize_processing_options(data: Dict[str, Any]) -> Tuple[str, bool, bool, int, float]:
    whisper_model = str(data.get("whisper_model", "base")).strip().lower() or "base"
    if whisper_model not in ALLOWED_WHISPER_MODELS:
        whisper_model = "base"

    use_video = _as_bool(data.get("use_video", False))
    web_search = _as_bool(data.get("web_search", False))
    max_vision = _safe_int(data.get("max_vision", 10), 10, 0, MAX_VISION_CALLS)
    fps = _safe_float(data.get("fps", 1.0), 1.0, FPS_MIN, FPS_MAX)
    return whisper_model, use_video, web_search, max_vision, fps


def process_video(
    video_path: Path,
    api_key: str,
    whisper_model: str,
    use_video: bool,
    web_search: bool,
    max_vision: int,
    fps: float = 1.0,
    progress_callback: Callable[[str, str], None] | None = None,
) -> Tuple[List[Dict[str, Any]], str, str, str, bool]:
    def report(stage: str, message: str) -> None:
        if progress_callback:
            progress_callback(stage, message)

    report("prepare", "\u6b63\u5728\u51c6\u5907\u5206\u6790\u4efb\u52a1...")
    output_dir = _create_unique_output_dir(video_path)

    video_dest = output_dir / video_path.name
    if not video_dest.exists():
        shutil.copy2(video_path, video_dest)

    agent = VideoAnalyzerAgent(api_key if api_key else None, whisper_model)
    srt_path = None

    if not use_video:
        report("subtitle", "\u6b63\u5728\u751f\u6210\u5b57\u5e55...")
        srt_path = agent.generate_subtitles(str(video_path), str(output_dir))
        report("analysis", "\u6b63\u5728\u5206\u6790\u5b57\u5e55\u5185\u5bb9...")
        steps = _run_async(agent.analyze_subtitles(srt_path))
    else:
        report("subtitle", "\u6b63\u5728\u5c1d\u8bd5\u751f\u6210\u5b57\u5e55...")
        try:
            srt_path = agent.generate_subtitles(str(video_path), str(output_dir))
        except Exception as exc:
            logger.warning("Whisper 字幕生成失败，继续视频分析模式: %s", exc)
            srt_path = None
        report("analysis", "\u6b63\u5728\u5206\u6790\u89c6\u9891\u753b\u9762...")
        steps = _run_async(agent.analyze_video(str(video_path), fps))

    if not steps:
        report("analysis", "\u672a\u8bc6\u522b\u5230\u6709\u6548\u6b65\u9aa4")
        return [], "", str(output_dir), str(output_dir / "operation_guide.pdf"), False

    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)
    report("screenshots", "\u6b63\u5728\u751f\u6210\u5173\u952e\u622a\u56fe...")
    agent.generate_screenshots_from_steps(str(video_path), steps, str(image_dir))

    if max_vision > 0 and not use_video and srt_path:
        report("vision", "\u6b63\u5728\u8fdb\u884c\u89c6\u89c9\u589e\u5f3a...")
        steps = _run_async(
            agent.enhance_steps_with_vision(
                steps, str(image_dir), srt_path=srt_path, max_calls=max_vision
            )
        )

    output_md = output_dir / "operation_guide.md"
    report("document", "\u6b63\u5728\u751f\u6210\u603b\u7ed3\u6587\u6863...")
    _run_async(
        agent.generate_step_document(
            steps=steps,
            output_path=str(output_md),
            srt_path=srt_path if srt_path else None,
            image_dir="images",
            web_search=web_search,
        )
    )

    output_pdf = output_dir / "operation_guide.pdf"
    report("pdf", "\u6b63\u5728\u751f\u6210 PDF...")
    agent.generate_pdf(str(output_md), str(output_pdf))
    agent.save_results(steps, str(output_dir / "steps.json"))
    report("done", "\u5f53\u524d\u89c6\u9891\u5206\u6790\u5b8c\u6210")

    has_steps = len(steps) > 0
    if has_steps:
        record = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_name": video_path.name,
            "output_dir": str(output_dir),
            "steps_count": len(steps),
            "mode": "video" if use_video else "subtitle",
            "whisper_model": whisper_model,
            "use_video": use_video,
            "web_search": web_search,
            "max_vision": max_vision,
            "pdf_path": str(output_pdf),
        }
        save_history(record)

    with open(output_md, "r", encoding="utf-8") as f:
        md_content = f.read()

    return steps, md_content, str(output_dir), str(output_pdf), has_steps


@app.route("/")
def index():
    return render_template("index.html", vite_dev_server=_vite_dev_server())


@app.route("/main.css")
def maincss():
    return send_from_directory("static", "main.css")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "没有选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式"}), 400

    save_path = _build_unique_upload_path(file.filename)
    file.save(str(save_path))
    return jsonify({"filename": save_path.name, "filepath": str(save_path)})


@app.route("/upload_chunk_init", methods=["POST"])
def upload_chunk_init():
    data = _json_payload()
    filename = str(data.get("filename", "")).strip()
    if not filename:
        return jsonify({"error": "文件名不能为空"}), 400
    if not allowed_file(filename):
        return jsonify({"error": "不支持的文件格式"}), 400

    total_size = _safe_int(data.get("total_size"), 0, 1)
    if total_size <= 0:
        return jsonify({"error": "文件大小无效"}), 400

    requested_chunk_size = _safe_int(
        data.get("chunk_size", DEFAULT_UPLOAD_CHUNK_SIZE),
        DEFAULT_UPLOAD_CHUNK_SIZE,
        256 * 1024,
        MAX_UPLOAD_CHUNK_SIZE,
    )
    file_key = str(data.get("file_key", "")).strip()

    try:
        requested_upload_id = _normalize_upload_id(data.get("upload_id", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with upload_session_lock:
        session: Dict[str, Any] | None = None
        upload_id = requested_upload_id

        if upload_id:
            session = _load_upload_session(upload_id)
            if session is not None:
                same_name = str(session.get("filename", "")) == filename
                same_size = _safe_int(session.get("total_size"), -1) == total_size
                same_key = not file_key or str(session.get("file_key", "")) == file_key
                if not (same_name and same_size and same_key):
                    session = None

        if session is None:
            upload_id = uuid4().hex
            total_chunks = max(1, (total_size + requested_chunk_size - 1) // requested_chunk_size)
            session = {
                "upload_id": upload_id,
                "filename": filename,
                "file_key": file_key,
                "total_size": total_size,
                "chunk_size": requested_chunk_size,
                "total_chunks": total_chunks,
                "received_chunks": [],
                "created_at": now_text,
                "updated_at": now_text,
            }
            _save_upload_session(upload_id, session)
        else:
            total_chunks = _safe_int(session.get("total_chunks"), 1, 1)
            session["received_chunks"] = _normalize_received_chunks(
                session.get("received_chunks", []), total_chunks
            )
            session["updated_at"] = now_text
            _save_upload_session(upload_id, session)

    return jsonify(
        {
            "success": True,
            "upload_id": upload_id,
            "chunk_size": _safe_int(session.get("chunk_size"), DEFAULT_UPLOAD_CHUNK_SIZE, 1),
            "total_chunks": _safe_int(session.get("total_chunks"), 1, 1),
            "received_chunks": session.get("received_chunks", []),
        }
    )


@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    if "chunk" not in request.files:
        return jsonify({"error": "缺少分片文件"}), 400

    try:
        upload_id = _normalize_upload_id(request.form.get("upload_id", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if not upload_id:
        return jsonify({"error": "upload_id 不能为空"}), 400

    chunk_index = _safe_int(request.form.get("chunk_index"), -1)
    if chunk_index < 0:
        return jsonify({"error": "chunk_index 无效"}), 400

    chunk_file = request.files["chunk"]
    chunk_data = chunk_file.read() or b""

    with upload_session_lock:
        session = _load_upload_session(upload_id)
        if session is None:
            return jsonify({"error": "上传会话不存在，请重新开始上传"}), 404

        total_chunks = _safe_int(session.get("total_chunks"), 0, 1)
        chunk_size = _safe_int(
            session.get("chunk_size"), DEFAULT_UPLOAD_CHUNK_SIZE, 1, MAX_UPLOAD_CHUNK_SIZE
        )
        total_size = _safe_int(session.get("total_size"), 0, 1)

        if chunk_index >= total_chunks:
            return jsonify({"error": "chunk_index 超出范围"}), 400

        offset = chunk_index * chunk_size
        if offset >= total_size:
            return jsonify({"error": "分片偏移量无效"}), 400

        expected_max_size = min(chunk_size, total_size - offset)
        if len(chunk_data) == 0 and expected_max_size > 0:
            return jsonify({"error": "分片内容为空"}), 400
        if len(chunk_data) > expected_max_size:
            return jsonify({"error": "分片大小超出限制"}), 400

        temp_path = _upload_session_temp_path(upload_id)
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        if not temp_path.exists():
            with open(temp_path, "wb"):
                pass

        with open(temp_path, "r+b") as f:
            f.seek(offset)
            f.write(chunk_data)

        received_chunks = set(
            _normalize_received_chunks(session.get("received_chunks", []), total_chunks)
        )
        received_chunks.add(chunk_index)
        session["received_chunks"] = sorted(received_chunks)
        session["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _save_upload_session(upload_id, session)

    return jsonify(
        {
            "success": True,
            "upload_id": upload_id,
            "uploaded_chunks": len(session["received_chunks"]),
            "total_chunks": total_chunks,
        }
    )


@app.route("/upload_chunk_finalize", methods=["POST"])
def upload_chunk_finalize():
    data = _json_payload()
    try:
        upload_id = _normalize_upload_id(data.get("upload_id", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not upload_id:
        return jsonify({"error": "upload_id 不能为空"}), 400

    with upload_session_lock:
        session = _load_upload_session(upload_id)
        if session is None:
            return jsonify({"error": "上传会话不存在，请重新开始上传"}), 404

        filename = str(session.get("filename", "")).strip()
        if not filename or not allowed_file(filename):
            return jsonify({"error": "原始文件名无效"}), 400

        total_chunks = _safe_int(session.get("total_chunks"), 0, 1)
        total_size = _safe_int(session.get("total_size"), 0, 1)
        received_chunks = _normalize_received_chunks(session.get("received_chunks", []), total_chunks)

        if len(received_chunks) < total_chunks:
            received_set = set(received_chunks)
            missing_chunks = [i for i in range(total_chunks) if i not in received_set][:10]
            missing_text = ",".join(str(i) for i in missing_chunks)
            suffix = "..." if len(received_chunks) + len(missing_chunks) < total_chunks else ""
            return jsonify({"error": f"分片未上传完整，缺少分片: {missing_text}{suffix}"}), 400

        temp_path = _upload_session_temp_path(upload_id)
        if not temp_path.exists():
            return jsonify({"error": "临时文件不存在，请重新上传"}), 400

        if temp_path.stat().st_size < total_size:
            return jsonify({"error": "文件尚未完整上传，请继续上传缺失分片"}), 400

        save_path = _build_unique_upload_path(filename)
        shutil.move(str(temp_path), str(save_path))
        if save_path.stat().st_size > total_size:
            with open(save_path, "r+b") as f:
                f.truncate(total_size)

        _delete_upload_session(upload_id)

    return jsonify({"success": True, "filename": save_path.name, "filepath": str(save_path)})


@app.route("/analyze", methods=["POST"])
def analyze():
    data = _json_payload()
    api_key = str(data.get("api_key", "")).strip()
    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    whisper_model, use_video, web_search, max_vision, fps = _normalize_processing_options(
        data
    )

    try:
        video_path = _resolve_upload_filepath(data.get("filepath"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"error": "文件不存在"}), 400

    try:
        _update_single_progress(
            status="processing",
            current_file=video_path.name,
            stage="prepare",
            message="\u4efb\u52a1\u5df2\u542f\u52a8\uff0c\u6b63\u5728\u521d\u59cb\u5316...",
        )

        def _single_progress_callback(stage: str, message: str) -> None:
            _update_single_progress(
                status="processing",
                current_file=video_path.name,
                stage=stage,
                message=message,
            )

        steps, md_content, output_dir, output_pdf, has_steps = process_video(
            video_path,
            api_key,
            whisper_model,
            use_video,
            web_search,
            max_vision,
            fps,
            progress_callback=_single_progress_callback,
        )
        if not has_steps:
            _update_single_progress(
                status="failed",
                stage="failed",
                message="\u672a\u80fd\u8bc6\u522b\u5230\u64cd\u4f5c\u6b65\u9aa4",
            )
            return jsonify({"error": "未能识别到操作步骤"}), 500

        _update_single_progress(
            status="completed",
            stage="done",
            message="\u89c6\u9891\u5206\u6790\u5df2\u5b8c\u6210",
        )
        return jsonify(
            {
                "success": True,
                "steps": steps,
                "markdown": md_content,
                "output_dir": output_dir,
                "pdf_path": output_pdf,
            }
        )
    except Exception as exc:
        _update_single_progress(
            status="failed",
            stage="failed",
            message=str(exc),
        )
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)


@app.route("/download_zip/<output_dir>")
def download_zip(output_dir):
    try:
        output_path = _resolve_output_dir(output_dir, must_exist=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"error": "文件不存在"}), 404

    md_file = output_path / "operation_guide.md"
    pdf_file = output_path / "operation_guide.pdf"
    images_dir = output_path / "images"

    if not md_file.exists():
        return jsonify({"error": "文件不存在"}), 404

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(md_file, "operation_guide.md")
        if pdf_file.exists():
            zf.write(pdf_file, "operation_guide.pdf")
        if images_dir.exists():
            for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
                for img_file in images_dir.glob(pattern):
                    zf.write(img_file, f"images/{img_file.name}")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{output_path.name}.zip",
    )


@app.route("/output/<path:filename>")
def serve_output_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)


@app.route("/regenerate", methods=["POST"])
def regenerate_document():
    data = _json_payload()
    api_key = str(data.get("api_key", "")).strip()
    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    steps = data.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return jsonify({"error": "没有步骤数据"}), 400

    try:
        output_dir = _resolve_output_dir(data.get("output_dir"), must_exist=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"error": "输出目录不存在"}), 400

    web_search = _as_bool(data.get("web_search", False))

    try:
        agent = VideoAnalyzerAgent(api_key)
        output_path = output_dir / "operation_guide.md"
        _run_async(
            agent.generate_step_document(
                steps=steps,
                output_path=str(output_path),
                srt_path=None,
                image_dir="images",
                web_search=web_search,
            )
        )

        output_pdf = output_dir / "operation_guide.pdf"
        agent.generate_pdf(str(output_path), str(output_pdf))
        agent.save_results(steps, str(output_dir / "steps.json"))

        with open(output_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        return jsonify(
            {
                "success": True,
                "steps": steps,
                "markdown": md_content,
                "output_dir": str(output_dir),
                "pdf_path": str(output_pdf),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500


@app.route("/cleanup/<filename>")
def cleanup(filename):
    try:
        safe_name = secure_filename(filename)
        if not safe_name:
            return jsonify({"error": "文件名无效"}), 400

        upload_file_path = UPLOAD_ROOT / safe_name
        if upload_file_path.exists():
            upload_file_path.unlink()

        # 兼容旧目录命名: outputs/<stem>
        legacy_output_dir = OUTPUT_ROOT / Path(safe_name).stem
        if legacy_output_dir.exists() and legacy_output_dir.is_dir():
            shutil.rmtree(legacy_output_dir)

        # 新目录命名: outputs/<stem>_<timestamp>
        stem_prefix = secure_filename(Path(safe_name).stem)
        if stem_prefix:
            for output_dir in OUTPUT_ROOT.glob(f"{stem_prefix}_*"):
                if output_dir.is_dir():
                    shutil.rmtree(output_dir)

        return jsonify({"success": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify({"history": load_history()})


@app.route("/history/<record_id>", methods=["GET"])
def get_history_record(record_id):
    history = load_history()
    for item in history:
        if item.get("id") != record_id:
            continue

        record = dict(item)
        output_dir_value = record.get("output_dir")
        if output_dir_value:
            try:
                output_dir = _resolve_output_dir(output_dir_value, must_exist=True)
            except (ValueError, FileNotFoundError):
                output_dir = None

            if output_dir:
                steps_path = output_dir / "steps.json"
                md_path = output_dir / "operation_guide.md"

                if steps_path.exists():
                    with open(steps_path, "r", encoding="utf-8") as f:
                        record["steps"] = json.load(f)
                if md_path.exists():
                    with open(md_path, "r", encoding="utf-8") as f:
                        record["markdown"] = f.read()

        return jsonify({"record": record})

    return jsonify({"error": "记录不存在"}), 404


@app.route("/history/<record_id>", methods=["DELETE"])
def delete_history(record_id):
    try:
        delete_history_record(record_id)
        return jsonify({"success": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/upload_batch", methods=["POST"])
def upload_batch_files():
    if "files" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "没有选择文件"}), 400

    uploaded = []
    errors = []

    for file in files:
        if not file or file.filename == "":
            continue
        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: 不支持的格式")
            continue

        try:
            save_path = _build_unique_upload_path(file.filename)
            file.save(str(save_path))
            uploaded.append({"filename": save_path.name, "filepath": str(save_path)})
        except Exception as exc:
            errors.append(f"{file.filename}: {str(exc)}")

    return jsonify({"uploaded": uploaded, "errors": errors, "total": len(files)})


@app.route("/batch_progress", methods=["GET"])
def get_batch_progress():
    with batch_progress_lock:
        return jsonify(dict(batch_progress))


@app.route("/single_progress", methods=["GET"])
def get_single_progress():
    with single_progress_lock:
        return jsonify(dict(single_progress))


@app.route("/analyze_batch", methods=["POST"])
def analyze_batch():
    data = _json_payload()
    api_key = str(data.get("api_key", "")).strip()
    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    raw_filepaths = data.get("filepaths", [])
    if not isinstance(raw_filepaths, list) or not raw_filepaths:
        return jsonify({"error": "没有视频文件"}), 400

    whisper_model, use_video, web_search, max_vision, fps = _normalize_processing_options(
        data
    )

    filepaths: List[Path] = []
    for raw_path in raw_filepaths:
        try:
            filepaths.append(_resolve_upload_filepath(raw_path))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except FileNotFoundError:
            return jsonify({"error": f"文件不存在: {raw_path}"}), 400

    _update_batch_progress(
        total=len(filepaths),
        current=0,
        status="processing",
        current_file="",
        stage="prepare",
        message="\u6279\u91cf\u4efb\u52a1\u5df2\u542f\u52a8\uff0c\u6b63\u5728\u7b49\u5f85\u5904\u7406...",
    )

    results = []
    try:
        for idx, filepath in enumerate(filepaths, start=1):
            _update_batch_progress(
                current=idx,
                current_file=filepath.name,
                stage="prepare",
                message=f"\u6b63\u5728\u51c6\u5907\u5904\u7406: {filepath.name}",
            )

            def _batch_progress_callback(stage: str, message: str, *, _idx=idx, _name=filepath.name):
                _update_batch_progress(
                    current=_idx,
                    current_file=_name,
                    stage=stage,
                    message=message,
                )

            try:
                steps, md_content, output_dir, output_pdf, has_steps = process_video(
                    filepath,
                    api_key,
                    whisper_model,
                    use_video,
                    web_search,
                    max_vision,
                    fps,
                    progress_callback=_batch_progress_callback,
                )

                if not has_steps:
                    _update_batch_progress(
                        current=idx,
                        current_file=filepath.name,
                        stage="failed",
                        message="\u672a\u80fd\u8bc6\u522b\u5230\u64cd\u4f5c\u6b65\u9aa4",
                    )
                    results.append(
                        {
                            "index": idx,
                            "filename": filepath.name,
                            "success": False,
                            "error": "未识别到操作步骤",
                        }
                    )
                    continue

                results.append(
                    {
                        "index": idx,
                        "filename": filepath.name,
                        "success": True,
                        "steps_count": len(steps) if steps else 0,
                        "output_dir": output_dir,
                        "pdf_path": output_pdf,
                        "markdown": md_content,
                        "steps": steps,
                    }
                )
                _update_batch_progress(
                    current=idx,
                    current_file=filepath.name,
                    stage="done",
                    message=f"{filepath.name} \u5206\u6790\u5b8c\u6210",
                )
            except Exception as exc:
                error_msg = str(exc)
                if "ToolNotOpen" in error_msg or "web search" in error_msg.lower():
                    error_msg = (
                        "联网搜索功能未开通，请在火山引擎控制台开通："
                        "https://console.volcengine.com/common-buy/CC_content_plugin"
                    )
                _update_batch_progress(
                    current=idx,
                    current_file=filepath.name,
                    stage="failed",
                    message=error_msg,
                )
                results.append(
                    {
                        "index": idx,
                        "filename": filepath.name,
                        "success": False,
                        "error": error_msg,
                    }
                )
    finally:
        _update_batch_progress(
            status="completed",
            current_file="",
            stage="done",
            message="\u6279\u91cf\u5206\u6790\u5df2\u5b8c\u6210",
        )

    success_count = sum(1 for r in results if r.get("success"))
    return jsonify(
        {
            "success": True,
            "results": results,
            "summary": {
                "total": len(filepaths),
                "success": success_count,
                "failed": len(filepaths) - success_count,
            },
        }
    )


@app.route("/download_batch_zip", methods=["POST"])
def download_batch_zip():
    data = _json_payload()
    output_dirs = data.get("output_dirs", [])
    if not isinstance(output_dirs, list) or not output_dirs:
        return jsonify({"error": "没有输出目录"}), 400

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for raw_output_dir in output_dirs:
            try:
                output_path = _resolve_output_dir(raw_output_dir, must_exist=True)
            except (ValueError, FileNotFoundError):
                continue

            base_name = output_path.name
            md_file = output_path / "operation_guide.md"
            pdf_file = output_path / "operation_guide.pdf"
            images_dir = output_path / "images"

            if md_file.exists():
                zf.write(md_file, f"{base_name}/operation_guide.md")
            if pdf_file.exists():
                zf.write(pdf_file, f"{base_name}/operation_guide.pdf")
            if images_dir.exists():
                for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
                    for img_file in images_dir.glob(pattern):
                        zf.write(img_file, f"{base_name}/images/{img_file.name}")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="batch_results.zip",
    )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes"}
    app.run(debug=debug_mode, port=5000)
