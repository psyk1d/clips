#!/usr/bin/env python3
"""
VerticalFrame Batch CLI Processor
Automatically frames Shorts/Reels onto a 1080x1920 30fps white canvas
with a bold black caption on top, 1080x810 focal-cropped video in the middle,
and a 250px transparent PNG logo centered 80px below the video.
"""

import argparse
import json
import os
import subprocess
import textwrap
from pathlib import Path


def inspect_video(video_path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        str(video_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    v_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    a_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    return {
        "width": int(v_stream.get("width", 1080)),
        "height": int(v_stream.get("height", 1920)),
        "duration": float(data.get("format", {}).get("duration", 0)),
        "has_audio": a_stream is not None,
    }


def generate_default_hook(video_path: Path) -> str:
    topic = video_path.stem.replace("_", " ").replace("-", " ").strip().lower()
    if len(topic) < 3:
        topic = "this moment"
    hook = f"Watching {topic} and you realize how much detail goes into it..."
    return hook[0].upper() + hook[1:]


def format_caption(text: str) -> tuple[str, int]:
    cleaned = text.strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    font_size = 60
    wrap_width = 30
    lines = textwrap.wrap(cleaned, width=wrap_width)
    while len(lines) > 3 and font_size > 44:
        font_size -= 4
        wrap_width += 3
        lines = textwrap.wrap(cleaned, width=wrap_width)
    if len(lines) > 3:
        lines = lines[:3]
        if not lines[-1].endswith("..."):
            lines[-1] = lines[-1].rstrip(".,!? ") + "..."
    return "\n".join(lines), font_size


def process_single_video(
    video_path: Path,
    logo_path: Path,
    output_dir: Path,
    hook_text: str | None = None,
    focal_y: float = 0.5,
    font_path: str | None = None,
):
    meta = inspect_video(video_path)
    print(f"[Inspect] {video_path.name}: {meta['width']}x{meta['height']}, {meta['duration']:.2f}s, audio={meta['has_audio']}")

    raw_hook = hook_text if hook_text else generate_default_hook(video_path)
    wrapped_hook, font_size = format_caption(raw_hook)
    escaped_hook = (
        wrapped_hook.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )

    line_spacing = int(round(font_size * 0.3))
    font_opt = f":fontfile='{font_path}'" if font_path else ""

    filter_complex = (
        f"color=white:s=1080x1920:r=30[bg];"
        f"[0:v]scale=1080:-2:force_original_aspect_ratio=increase,"
        f"crop=1080:810:0:(ih-810)*{focal_y:.2f}[vid];"
        f"[1:v]scale=250:-1[logo];"
        f"[bg][vid]overlay=0:600[tmp1];"
        f"[tmp1][logo]overlay=(W-w)/2:1490[tmp2];"
        f"[tmp2]drawtext=text='{escaped_hook}'{font_opt}:fontcolor=black:"
        f"fontsize={font_size}:x=60:y=560-text_h:line_spacing={line_spacing}[out]"
    )

    output_mp4 = output_dir / f"{video_path.stem}_final.mp4"
    check_png = output_dir / f"{video_path.stem}_frame_check.png"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(logo_path),
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4),
    ]
    subprocess.run(cmd, check=True)

    # Extract 1 verification frame to verify caption, crop, and logo alignment
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(output_mp4), "-vframes", "1", str(check_png)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[Done] Saved {output_mp4} (check frame: {check_png})")


def main():
    parser = argparse.ArgumentParser(description="Batch frame Shorts/Reels onto a 1080x1920 white canvas.")
    parser.add_argument("--logo", required=True, help="Path to transparent PNG logo")
    parser.add_argument("--videos", nargs="+", required=True, help="Input video file(s)")
    parser.add_argument("--hooks", nargs="*", default=[], help="Optional caption hooks matching input videos")
    parser.add_argument("--focal-y", type=float, default=0.5, help="Vertical crop anchor 0.0 (top) to 1.0 (bottom)")
    parser.add_argument("--font", default=None, help="Optional path to bold .ttf/.otf font")
    parser.add_argument("--out-dir", default="output", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    logo_path = Path(args.logo)

    for i, vid in enumerate(args.videos):
        hook = args.hooks[i] if i < len(args.hooks) else None
        process_single_video(Path(vid), logo_path, out_dir, hook_text=hook, focal_y=args.focal_y, font_path=args.font)


if __name__ == "__main__":
    main()
