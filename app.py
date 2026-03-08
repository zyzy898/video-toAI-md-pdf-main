import os
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from video_analyzer_agent import VideoAnalyzerAgent

app = Flask(__name__)
app.secret_key = "video-analyzer-secret-key"

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"

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

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

HISTORY_FILE = "history.json"
MAX_HISTORY = 50

batch_progress = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(record):
    """保存历史记录"""
    history = load_history()
    history.insert(0, record)
    history = history[:MAX_HISTORY]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def delete_history_record(record_id):
    """删除指定历史记录"""
    history = load_history()
    history = [r for r in history if r.get("id") != record_id]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def process_video(
    video_path, api_key, whisper_model, use_video, web_search, max_vision, fps=1.0
):
    from video_analyzer_agent import VideoAnalyzerAgent

    output_dir = Path(app.config["OUTPUT_FOLDER"]) / Path(video_path).stem
    output_dir.mkdir(exist_ok=True)

    # 复制视频到输出目录
    video_dest = output_dir / Path(video_path).name
    if not video_dest.exists():
        shutil.copy2(video_path, video_dest)

    agent = VideoAnalyzerAgent(api_key if api_key else None, whisper_model)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    srt_path = None

    if not use_video:
        # 字幕驱动模式
        srt_path = agent.generate_subtitles(str(video_path), str(output_dir))
        steps = loop.run_until_complete(agent.analyze_subtitles(srt_path))
    else:
        # 视频上传模式 - 先尝试生成字幕作为参考
        try:
            srt_path = agent.generate_subtitles(str(video_path), str(output_dir))
        except Exception as e:
            print(f"Whisper 字幕生成失败: {e}，将继续不使用字幕")
            srt_path = None

        # 上传视频给 AI 分析
        steps = loop.run_until_complete(agent.analyze_video(str(video_path), fps))

    # 复制字幕到输出目录
    if srt_path:
        srt_dest = output_dir / Path(srt_path).name
        if not srt_dest.exists():
            shutil.copy2(srt_path, srt_dest)

    if not steps:
        loop.close()
        return [], "", str(output_dir), str(output_dir / "operation_guide.pdf"), False

    print(f"识别到 {len(steps)} 个步骤，正在生成截图...")

    # 生成截图（两种模式都需要）
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)
    agent.generate_screenshots_from_steps(str(video_path), steps, str(image_dir))

    print("截图生成完成，正在进行 AI 看图增强...")

    # AI 看图增强仅在字幕驱动模式下进行
    if max_vision > 0 and not use_video and srt_path:
        steps = loop.run_until_complete(
            agent.enhance_steps_with_vision(
                steps, str(image_dir), srt_path=srt_path, max_calls=max_vision
            )
        )

    print("AI 看图增强完成，正在生成 Markdown 文档...")

    output_md = output_dir / "operation_guide.md"
    loop.run_until_complete(
        agent.generate_step_document(
            steps=steps,
            output_path=str(output_md),
            srt_path=srt_path if srt_path else None,
            image_dir="images",
            web_search=web_search,
        )
    )

    print("Markdown 文档生成完成，正在生成 PDF...")

    # 生成 PDF 文档
    output_pdf = output_dir / "operation_guide.pdf"
    agent.generate_pdf(str(output_md), str(output_pdf))

    print("PDF 生成完成")

    loop.close()

    # 保存步骤分析结果
    agent.save_results(steps, str(output_dir / "steps.json"))

    # 根据是否有步骤决定是否保存历史记录
    has_steps = len(steps) > 0

    # 保存历史记录
    if has_steps:
        record = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_name": Path(video_path).name,
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
    return render_template("index.html")


@app.route("/main.css")
def maincss():
    return send_from_directory("static", "main.css")


@app.route("/upload", methods=["POST"])
def upload_file():
    # 确保上传目录存在
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "没有选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    return jsonify({"filename": filename, "filepath": filepath})


@app.route("/analyze", methods=["POST"])
def analyze():
    # 确保输出目录存在
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    data = request.json
    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    filepath = data.get("filepath")
    whisper_model = data.get("whisper_model", "base")
    use_video = data.get("use_video", False)
    web_search = data.get("web_search", False)
    max_vision = int(data.get("max_vision", 10))
    fps = float(data.get("fps", 1.0))

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "文件不存在"}), 400

    try:
        steps, md_content, output_dir, output_pdf, has_steps = process_video(
            filepath, api_key, whisper_model, use_video, web_search, max_vision, fps
        )

        if not has_steps:
            return jsonify({"error": "未能识别到操作步骤"}), 500

        return jsonify(
            {
                "success": True,
                "steps": steps,
                "markdown": md_content,
                "output_dir": output_dir,
                "pdf_path": output_pdf,
            }
        )
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["OUTPUT_FOLDER"], filename, as_attachment=True
    )


@app.route("/download_zip/<output_dir>")
def download_zip(output_dir):
    """下载包含 md、pdf 和 images 的 zip 文件"""
    import zipfile
    from io import BytesIO

    output_path = Path(app.config["OUTPUT_FOLDER"]) / output_dir
    md_file = output_path / "operation_guide.md"
    pdf_file = output_path / "operation_guide.pdf"
    images_dir = output_path / "images"

    if not md_file.exists():
        return jsonify({"error": "文件不存在"}), 404

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        # 添加 md 文件
        zf.write(md_file, "operation_guide.md")

        # 添加 pdf 文件
        if pdf_file.exists():
            zf.write(pdf_file, "operation_guide.pdf")

        # 添加 images 文件夹
        if images_dir.exists():
            for img_file in images_dir.glob("*.jpg"):
                zf.write(img_file, f"images/{img_file.name}")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{output_dir}.zip",
    )


@app.route("/output/<path:filename>")
def serve_output_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)


@app.route("/regenerate", methods=["POST"])
def regenerate_document():
    """根据编辑后的步骤重新生成文档"""
    data = request.json

    api_key = data.get("api_key", "").strip()
    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    steps = data.get("steps", [])
    output_dir = data.get("output_dir")
    web_search = data.get("web_search", False)

    if not steps:
        return jsonify({"error": "没有步骤数据"}), 400

    if not output_dir:
        return jsonify({"error": "输出目录不存在"}), 400

    try:
        agent = VideoAnalyzerAgent(api_key)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        output_path = Path(output_dir) / "operation_guide.md"
        image_dir = "images"

        loop.run_until_complete(
            agent.generate_step_document(
                steps=steps,
                output_path=str(output_path),
                srt_path=None,
                image_dir=image_dir,
                web_search=web_search,
            )
        )

        output_pdf = Path(output_dir) / "operation_guide.pdf"
        agent.generate_pdf(str(output_path), str(output_pdf))

        loop.close()

        agent.save_results(steps, str(Path(output_dir) / "steps.json"))

        with open(output_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        return jsonify(
            {
                "success": True,
                "steps": steps,
                "markdown": md_content,
                "output_dir": output_dir,
                "pdf_path": str(output_pdf),
            }
        )
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/cleanup/<filename>")
def cleanup(filename):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        output_dir = os.path.join(app.config["OUTPUT_FOLDER"], Path(filename).stem)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    """获取历史记录列表"""
    history = load_history()
    return jsonify({"history": history})


@app.route("/history/<record_id>", methods=["GET"])
def get_history_record(record_id):
    """获取单条历史记录的详细信息"""
    history = load_history()
    for record in history:
        if record.get("id") == record_id:
            output_dir = record.get("output_dir")
            if output_dir and os.path.exists(output_dir):
                steps_path = os.path.join(output_dir, "steps.json")
                md_path = os.path.join(output_dir, "operation_guide.md")

                if os.path.exists(steps_path):
                    with open(steps_path, "r", encoding="utf-8") as f:
                        record["steps"] = json.load(f)

                if os.path.exists(md_path):
                    with open(md_path, "r", encoding="utf-8") as f:
                        record["markdown"] = f.read()

            return jsonify({"record": record})

    return jsonify({"error": "记录不存在"}), 404


@app.route("/history/<record_id>", methods=["DELETE"])
def delete_history(record_id):
    """删除历史记录"""
    try:
        delete_history_record(record_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload_batch", methods=["POST"])
def upload_batch_files():
    """批量上传多个视频文件"""
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    if "files" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    files = request.files.getlist("files")
    if not files or len(files) == 0:
        return jsonify({"error": "没有选择文件"}), 400

    uploaded = []
    errors = []

    for file in files:
        if file.filename == "":
            continue
        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: 不支持的格式")
            continue

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # 处理文件名冲突
        counter = 1
        base_name = Path(filename).stem
        extension = Path(filename).suffix
        while os.path.exists(filepath):
            filename = f"{base_name}_{counter}{extension}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            counter += 1

        try:
            file.save(filepath)
            uploaded.append({"filename": filename, "filepath": filepath})
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    return jsonify({"uploaded": uploaded, "errors": errors, "total": len(files)})


@app.route("/batch_progress", methods=["GET"])
def get_batch_progress():
    """获取批量处理进度"""
    return jsonify(batch_progress)


@app.route("/analyze_batch", methods=["POST"])
def analyze_batch():
    """批量分析多个视频"""
    global batch_progress
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    data = request.json
    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"error": "请输入 API Key"}), 400

    filepaths = data.get("filepaths", [])
    if not filepaths or len(filepaths) == 0:
        return jsonify({"error": "没有视频文件"}), 400

    whisper_model = data.get("whisper_model", "base")
    use_video = data.get("use_video", False)
    web_search = data.get("web_search", False)
    max_vision = int(data.get("max_vision", 10))
    fps = float(data.get("fps", 1.0))

    # 验证所有文件存在
    for fp in filepaths:
        if not os.path.exists(fp):
            return jsonify({"error": f"文件不存在: {fp}"}), 400

    # 初始化进度
    batch_progress = {
        "total": len(filepaths),
        "current": 0,
        "status": "processing",
        "current_file": "",
    }

    results = []

    for idx, filepath in enumerate(filepaths):
        # 更新进度
        batch_progress["current"] = idx + 1
        batch_progress["current_file"] = Path(filepath).name

        try:
            print(f"\n{'='*50}")
            print(f"处理第 {idx+1}/{len(filepaths)} 个视频: {Path(filepath).name}")
            print(f"{'='*50}")

            steps, md_content, output_dir, output_pdf, has_steps = process_video(
                filepath, api_key, whisper_model, use_video, web_search, max_vision, fps
            )

            if not has_steps:
                results.append(
                    {
                        "index": idx + 1,
                        "filename": Path(filepath).name,
                        "success": False,
                        "error": "未识别到操作步骤",
                    }
                )
                continue

            results.append(
                {
                    "index": idx + 1,
                    "filename": Path(filepath).name,
                    "success": True,
                    "steps_count": len(steps) if steps else 0,
                    "output_dir": output_dir,
                    "pdf_path": output_pdf,
                    "markdown": md_content,
                    "steps": steps,
                }
            )

        except Exception as e:
            error_msg = str(e)
            if "ToolNotOpen" in error_msg or "web search" in error_msg.lower():
                error_msg = "联网搜索功能未开通，请在火山引擎控制台开通：https://console.volcengine.com/common-buy/CC_content_plugin"
            results.append(
                {
                    "index": idx + 1,
                    "filename": Path(filepath).name,
                    "success": False,
                    "error": error_msg,
                }
            )

    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n批量处理完成: 成功 {success_count}/{len(filepaths)}")

    # 更新进度为完成
    batch_progress["status"] = "completed"

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
    """下载批量处理结果的 ZIP 文件"""
    import zipfile
    from io import BytesIO

    data = request.json
    output_dirs = data.get("output_dirs", [])

    if not output_dirs:
        return jsonify({"error": "没有输出目录"}), 400

    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for output_dir in output_dirs:
            output_path = Path(app.config["OUTPUT_FOLDER"]) / output_dir
            if not output_path.exists():
                continue

            base_name = output_dir

            md_file = output_path / "operation_guide.md"
            if md_file.exists():
                zf.write(md_file, f"{base_name}/operation_guide.md")

            pdf_file = output_path / "operation_guide.pdf"
            if pdf_file.exists():
                zf.write(pdf_file, f"{base_name}/operation_guide.pdf")

            images_dir = output_path / "images"
            if images_dir.exists():
                for img_file in images_dir.glob("*.jpg"):
                    zf.write(img_file, f"{base_name}/images/{img_file.name}")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="batch_results.zip",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
