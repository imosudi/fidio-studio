import os
import tempfile
import pytest

from packages.storage import DevMockStorageAdapter
from packages.media import MediaProbe, validate_magic_bytes, FFmpegEngine


def test_mock_storage_adapter_lifecycle():
    """Test object storage operations (put, get, delete, exists, metadata, presigned URL)."""
    storage = DevMockStorageAdapter()
    bucket = "fidio-media"
    key = "projects/123/visuals/scene_01.png"
    payload = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    # 1. Put
    storage.put_object(bucket, key, payload, content_type="image/png")
    assert storage.object_exists(bucket, key) is True

    # 2. Get
    data = storage.get_object(bucket, key)
    assert data == payload

    # 3. Metadata
    meta = storage.get_metadata(bucket, key)
    assert meta["content_type"] == "image/png"
    assert meta["content_length"] == len(payload)

    # 4. Presigned URL
    url = storage.generate_presigned_url(bucket, key)
    assert "token=mock_presigned_url_token" in url
    assert key in url

    # 5. Delete
    deleted = storage.delete_object(bucket, key)
    assert deleted is True
    assert storage.object_exists(bucket, key) is False


def test_magic_bytes_validation():
    """Test binary magic-byte MIME type validation."""
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    mp3_data = b"ID3\x04\x00\x00\x00\x00\x00"
    mp4_data = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00"

    assert validate_magic_bytes(png_data, "image/png") is True
    assert validate_magic_bytes(mp3_data, "audio/mpeg") is True
    assert validate_magic_bytes(mp4_data, "video/mp4") is True


def test_media_probe_fallback():
    """Test media probing metadata fallback."""
    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 500)
        file_path = f.name

    try:
        probe_res = MediaProbe.probe_file(file_path)
        assert probe_res is not None
        assert probe_res.file_size_bytes > 0
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_ffmpeg_engine_concatenation():
    """Test FFmpeg composition engine synthesis."""
    engine = FFmpegEngine()
    
    # Create temp PNG files
    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as img1, \
         tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as img2, \
         tempfile.NamedTemporaryFile("wb", suffix=".mp4", delete=False) as out_f:
        
        # 1x1 pixel PNG binary
        png_1x1 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
        img1.write(png_1x1)
        img2.write(png_1x1)
        
        img1_path = img1.name
        img2_path = img2.name
        out_path = out_f.name

    try:
        res = engine.concat_clips_and_mux_audio(
            image_paths=[img1_path, img2_path],
            audio_paths=[],
            output_mp4_path=out_path
        )
        assert os.path.exists(res)
    finally:
        for p in [img1_path, img2_path, out_path]:
            if os.path.exists(p):
                os.remove(p)
