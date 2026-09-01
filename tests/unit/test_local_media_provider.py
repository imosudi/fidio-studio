import pytest

from packages.providers.local_media import LocalMediaProvider


@pytest.mark.asyncio
async def test_local_media_provider_generates_real_media_assets():
    provider = LocalMediaProvider()

    visual = await provider.generate_visual("A neon cyberpunk city skyline at twilight")
    assert visual.mime_type in {"image/png", "image/svg+xml"}
    assert visual.file_size_bytes > 0

    audio = await provider.generate_audio("Welcome to the future.")
    assert audio.mime_type in {"audio/mpeg", "audio/wav"}
    assert audio.file_size_bytes > 0

    render = await provider.render_video(plan_id="demo-plan", scenes_count=2)
    assert render.mime_type == "video/mp4"
    assert render.file_size_bytes > 0
    assert render.duration_seconds > 0
