#!/usr/bin/env python3
"""
MLX-Audio FastAPI 服务器
使用 Apple Silicon GPU 加速 Qwen3-TTS
性能: 3-7 秒生成（vs Docker CPU 的 39-66 秒）
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import logging
from pathlib import Path
import mlx.core as mx
from mlx_audio.tts import load
import soundfile as sf
import numpy as np
import time
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Qwen3-TTS MLX Server",
    description="Apple Silicon GPU 加速的 TTS 服务器",
    version="1.0.0"
)

# 全局变量
model = None
OUTPUT_DIR = Path("/tmp/qwen3-tts-outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 支持的音色
SUPPORTED_SPEAKERS = ["Vivian", "Chelsie", "Ethan"]


@app.on_event("startup")
async def load_model():
    """启动时加载模型"""
    global model
    logger.info("=" * 60)
    logger.info("🚀 启动 MLX-Audio TTS 服务器...")
    logger.info(f"📍 Metal GPU 可用: {mx.metal.is_available()}")
    logger.info(f"📍 MLX 设备: {mx.default_device()}")

    start = time.time()
    try:
        model = load("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
        load_time = time.time() - start
        logger.info(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")
        logger.info(f"📊 支持的音色: {', '.join(SUPPORTED_SPEAKERS)}")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {e}", exc_info=True)
        raise


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "Qwen3-TTS MLX Server",
        "version": "1.0.0",
        "metal_gpu": mx.metal.is_available(),
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "tts": "/api/tts",
            "tts_to_speaker": "/api/tts_to_speaker"
        }
    }


@app.get("/health")
async def health():
    """健康检查端点"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "metal_gpu": mx.metal.is_available(),
        "device": str(mx.default_device()),
        "supported_speakers": SUPPORTED_SPEAKERS
    }


@app.post("/api/tts")
async def text_to_speech(
    text: str = Query(..., description="要合成的文本"),
    speed: float = Query(1.0, ge=0.5, le=2.0, description="语速倍率 (0.5-2.0)"),
    language: Optional[str] = Query("Chinese", description="语言"),
    speaker: Optional[str] = Query("Vivian", description="音色")
):
    """
    文本转语音 API（与 Docker 版本兼容）

    性能: 3-7 秒（GPU 加速）vs 39-66 秒（Docker CPU）
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    logger.info(f"📝 TTS 请求: {text} (speaker={speaker}, speed={speed}, language={language})")

    try:
        start_time = time.time()

        # 生成语音
        result_gen = model.generate(
            text=text,
            voice=speaker,
            speed=speed,
            stream=False
        )

        # 提取音频
        audio_chunks = []
        sample_rate = 24000
        for chunk in result_gen:
            if hasattr(chunk, 'audio'):
                audio_chunks.append(chunk.audio)
            if hasattr(chunk, 'sample_rate'):
                sample_rate = chunk.sample_rate

        if not audio_chunks:
            raise Exception("未生成音频数据")

        # 合并音频
        if len(audio_chunks) == 1:
            full_audio = audio_chunks[0]
        else:
            full_audio = mx.concatenate(audio_chunks, axis=0)

        # 保存为 WAV
        output_file = OUTPUT_DIR / f"tts_{int(time.time() * 1000)}.wav"
        audio_np = np.array(full_audio)
        sf.write(str(output_file), audio_np, sample_rate)

        gen_time = time.time() - start_time
        duration = full_audio.shape[0] / sample_rate
        realtime_factor = duration / gen_time if gen_time > 0 else 0

        logger.info(
            f"✅ 语音生成完成，耗时: {gen_time:.2f}s "
            f"(音频时长: {duration:.2f}s, 实时率: {realtime_factor:.2f}x)"
        )

        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename="output.wav",
            headers={
                "X-Generation-Time": str(gen_time),
                "X-Audio-Duration": str(duration),
                "X-Realtime-Factor": str(realtime_factor)
            }
        )

    except Exception as e:
        logger.error(f"❌ 生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts_to_speaker")
async def tts_to_speaker(
    text: str = Query(..., description="要合成的文本"),
    speaker: str = Query(..., description="音色名称"),
    speed: float = Query(1.0, ge=0.5, le=2.0, description="语速倍率")
):
    """
    指定音色的 TTS API（与 Docker 版本兼容）
    """
    return await text_to_speech(
        text=text,
        speed=speed,
        language="Chinese",
        speaker=speaker
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("启动 Uvicorn 服务器...")
    logger.info("监听地址: 0.0.0.0:7861")
    logger.info("访问 http://localhost:7861/docs 查看 API 文档")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7861,
        log_level="info"
    )
