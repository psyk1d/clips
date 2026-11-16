# VerticalFrame Studio (1080×1920 Shorts & Reels Framer)

Automatically frame YouTube Shorts and Instagram Reels onto a solid white (`#FFFFFF`) **1080×1920 (9:16, 30 fps)** canvas with a bold top hook, focal-cropped center video, and centered bottom logo.

## Canvas Layout Specification
- **Output Canvas**: `1080×1920`, `30 fps`, solid `#FFFFFF` background, original audio preserved.
- **Caption Zone (`y = 0` to `600`)**: Left-aligned bold black (`#000000`) sans-serif hook (`56–64px`, `1.3` line spacing, `60px` side margins, max 3 lines with auto-fit) anchored cleanly above the video.
- **Video Zone (`y = 600` to `1410`)**: Scaled to `1080px` wide and focal-cropped to `1080×810` without stretching.
- **Logo Zone (`y = 1410` to `1920`)**: Transparent PNG logo centered horizontally at `250px` wide, `80px` below the video's bottom edge (`y = 1490`).

## Quick Deploy on GitHub Pages
1. Create a new GitHub repository and upload `index.html`, `process_videos.py`, and `README.md`.
2. Go to **Settings → Pages**, select **Deploy from a branch** (`main` / `/root`), and click **Save**.
3. Open your live GitHub Pages URL to upload your logo and Shorts/Reels directly in the browser.

## Local Batch CLI Usage (FFmpeg + Python)
```bash
python3 process_videos.py \
  --logo brand_logo.png \
  --videos clip1.mp4 clip2.mp4 \
  --hooks "Watching this build come together and you realize..."
```
Outputs `<original_name>_final.mp4` and `<original_name>_frame_check.png` in `./output/`.
