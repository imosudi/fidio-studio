import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from packages.domain.media_providers import GeneratedMediaResult, MediaProvider
from packages.shared.config import settings
from packages.shared.exceptions import ProviderException
from packages.shared.logging import logger


class LocalMediaProvider(MediaProvider):
    """Local media generation provider that produces real files on disk without relying on external AI services.

    This is intentionally deterministic and offline-friendly for local development and testing.
    It creates actual image, audio, and video assets using FFmpeg and SVG/gradient generation,
    rather than returning a text-overlay-only placeholder.
    """

    def __init__(self):
        self.ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        self._root_dir = Path(tempfile.gettempdir()) / "fidio_media"
        self._root_dir.mkdir(parents=True, exist_ok=True)

    def _build_visual_svg(self, prompt: str, title: str, scene_number: int = 1) -> str:
        safe_prompt = prompt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        colors = [
            ("#0f172a", "#4f46e5", "#a855f7"),
            ("#111827", "#0ea5e9", "#14b8a6"),
            ("#1f2937", "#f97316", "#ef4444"),
        ]
        c1, c2, c3 = colors[(scene_number - 1) % len(colors)]
        snippet = safe_prompt[:110]
        return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1280\" height=\"720\" viewBox=\"0 0 1280 720\">
  <defs>
    <linearGradient id=\"bg\" x1=\"0%\" x2=\"100%\" y1=\"0%\" y2=\"100%\">
      <stop offset=\"0%\" stop-color=\"{c1}\"/>
      <stop offset=\"50%\" stop-color=\"{c2}\"/>
      <stop offset=\"100%\" stop-color=\"{c3}\"/>
    </linearGradient>
    <radialGradient id=\"glow\" cx=\"50%\" cy=\"35%\" r=\"55%\">
      <stop offset=\"0%\" stop-color=\"rgba(255,255,255,0.8)\"/>
      <stop offset=\"100%\" stop-color=\"rgba(255,255,255,0)\"/>
    </radialGradient>
  </defs>
  <rect width=\"1280\" height=\"720\" fill=\"url(#bg)\"/>
  <circle cx=\"650\" cy=\"220\" r=\"240\" fill=\"url(#glow)\"/>
  <circle cx=\"340\" cy=\"520\" r=\"180\" fill=\"rgba(167, 139, 250, 0.25)\"/>
  <circle cx=\"1020\" cy=\"180\" r=\"150\" fill=\"rgba(34, 211, 238, 0.18)\"/>
  <rect x=\"110\" y=\"110\" width=\"1060\" height=\"500\" rx=\"28\" fill=\"rgba(15,23,42,0.35)\" stroke=\"rgba(148, 163, 184, 0.55)\" stroke-width=\"2\"/>
  <text x=\"640\" y=\"250\" font-family=\"Inter, Segoe UI, sans-serif\" font-size=\"28\" font-weight=\"700\" fill=\"#e2e8f0\" text-anchor=\"middle\">FÍDÍÒ SCENE {scene_number}</text>
  <text x=\"640\" y=\"330\" font-family=\"Inter, Segoe UI, sans-serif\" font-size=\"44\" font-weight=\"800\" fill=\"#ffffff\" text-anchor=\"middle\">{safe_title}</text>
  <text x=\"640\" y=\"435\" font-family=\"Inter, Segoe UI, sans-serif\" font-size=\"20\" font-weight=\"500\" fill=\"#dbeafe\" text-anchor=\"middle\">{snippet}</text>
  <text x=\"640\" y=\"520\" font-family=\"Inter, Segoe UI, sans-serif\" font-size=\"18\" fill=\"#cbd5e1\" text-anchor=\"middle\">Imagine. Create. Fídíò.</text>
</svg>"""

    def _write_file(self, filename: str, data: bytes, folder: str = "media") -> str:
        target_dir = self._root_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename
        file_path.write_bytes(data)
        return str(file_path)

    async def generate_visual(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> GeneratedMediaResult:
        logger.info(f"LocalMediaProvider generating visual asset for prompt: '{prompt[:60]}...'")
        asset_id = uuid.uuid4()
        title = f"Scene {asset_id.hex[:4]}"
        svg_text = self._build_visual_svg(prompt=prompt, title=title, scene_number=1)
        svg_path = self._write_file(f"visual_{asset_id.hex[:8]}.svg", svg_text.encode("utf-8"), folder="visuals")
        file_size = os.path.getsize(svg_path)
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_MEDIA,
            object_key=f"visuals/local_{asset_id.hex[:8]}.svg",
            mime_type="image/svg+xml",
            file_size_bytes=file_size,
            duration_seconds=5.0,
            width=1280,
            height=720,
        )

    async def generate_audio(
        self,
        script: str,
        voice: Optional[str] = "natural"
    ) -> GeneratedMediaResult:
        logger.info(f"LocalMediaProvider generating narration audio for script: '{script[:50]}...'")
        asset_id = uuid.uuid4()
        output_path = self._write_file(f"audio_{asset_id.hex[:8]}.mp3", b"", folder="audio")
        duration_seconds = max(3.0, min(10.0, len(script.split()) * 0.35 + 1.5))
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(duration_seconds),
            "-q:a", "9",
            "-acodec", "libmp3lame",
            output_path,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            raise ProviderException("LocalMediaProvider", f"Audio generation failed: {exc}") from exc

        file_size = os.path.getsize(output_path)
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_MEDIA,
            object_key=f"audio/local_{asset_id.hex[:8]}.mp3",
            mime_type="audio/mpeg",
            file_size_bytes=file_size,
            duration_seconds=duration_seconds,
        )

    async def render_video(
        self,
        plan_id: str,
        scenes_count: int,
        resolution: str = "1920x1080"
    ) -> GeneratedMediaResult:
        logger.info(f"LocalMediaProvider composing video render for plan_id={plan_id} ({scenes_count} scenes)")
        render_id = uuid.uuid4()
        output_path = self._write_file(f"render_{render_id.hex[:8]}.mp4", b"", folder="renders")
        duration_seconds = max(6.0, min(30.0, scenes_count * 5.0))
        width, height = (1920, 1080) if resolution == "1920x1080" else (1280, 720)
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f", "lavfi",
            "-i", f"testsrc2=size={width}x{height}:rate=30:duration={duration_seconds}",
            "-vf",
            "format=yuv420p,eq=brightness=0.08:saturation=1.3:contrast=1.2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration_seconds),
            output_path,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            raise ProviderException("LocalMediaProvider", f"Video render failed: {exc}") from exc

        file_size = os.path.getsize(output_path)
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_RENDERS,
            object_key=f"renders/local_{render_id.hex[:8]}.mp4",
            mime_type="video/mp4",
            file_size_bytes=file_size,
            duration_seconds=duration_seconds,
            width=width,
            height=height,
        )
