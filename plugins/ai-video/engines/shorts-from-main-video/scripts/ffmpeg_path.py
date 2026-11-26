import os, shutil


def ffmpeg_exe():
    """FFMPEG env var > ffmpeg on PATH > imageio_ffmpeg's bundled full build (pip install imageio-ffmpeg)."""
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    p = shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()
