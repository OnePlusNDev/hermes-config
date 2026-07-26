---
name: ascii-media
description: "Unified index for ASCII art — static text banners, character images, and animated ASCII video."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# ASCII Media — Index & Quick Guide

Two sibling skills handle all ASCII creative work. Choose based on the task type.

## Skills at a glance

| Skill | What it does | When to use | Install footprint |
|-------|-------------|-------------|-----------------|
| **ascii-art** (static) | Text banners, character images, image-to-ASCII, pre-made ASCII art, QR codes via pyfiglet, cowsay, boxes, toilet, jp2a, ascii-image-converter | Single-frame text art — banners, avatars, terminal decorations, printable ASCII | `pyfiglet`, `cowsay`, `boxes`, `ascii-image-converter` (~50MB total) |
| **ascii-video** (animation) | Convert video/audio/images into colored ASCII MP4/GIF — audio-reactive visualizers, generative ASCII animations, video-to-ASCII recreations | Animated output — music visualizers, matrix-style effects, retro CRT aesthetic videos | Python 3.10+, NumPy, SciPy, Pillow, ffmpeg (~250MB + GPU optional) |

## Quick decision tree

1. **User wants a static image** (banner, ASCII cat, QR code) → `ascii-art`
2. **User wants animated output** (music video, glitch effect, character animation) → `ascii-video`
3. **Both needed** (animated banner with text art header) → combine both

## Usage patterns

### Static ASCII Art (via ascii-art skill)

```python
from hermes_tools import skill_view

# Load the full static ASCII art reference
skill_view(name="ascii-art")
```

Common tasks: text banners (`pyfiglet`), message art (`cowsay`), decorative borders (`boxes`), image-to-ASCII, pre-made ASCII from ascii.co.uk.

### Animated ASCII Video (via ascii-video skill)

```python
from hermes_tools import skill_view

# Load the full animation pipeline reference
skill_view(name="ascii-video")
```

Common tasks: audio-reactive music visualizers, video-to-ASCII conversion, generative procedural animations. See `ascii-video/references/` for 17 reference docs covering effects, palettes, shading, optimization, and scene design.

### Combining Both

Example: a music video with ASCII art title header followed by animated visualizer:

```bash
# Step 1 — Create title banner (static)
python3 -m pyfiglet "MY TITLE" -f doom | boxes -d stone > /tmp/banner.txt

# Step 2 — Generate the animated visualizer from audio file
# (see ascii-video skill for full pipeline)
python ascii_video_script.py --input song.mp3 --mode audio-reactive
```

## Related creative skills

- **manim-video** — math/algorithm animations in real vector graphics (3Blue1Brown style). Choose when you need mathematical or scientific animation where ASCII lacks fidelity.
- **excalidraw** — hand-drawn-style diagrams (architecture, flows, whiteboard sketches). Different domain but same audience of visual thinkers.
- **architecture-diagram** — dark-themed SVG architecture diagrams for system design docs. Production-quality visuals instead of rough ASCII.

## Pitfalls

1. **Don't confuse the two skills.** ascii-art = static terminal output; ascii-video = animated video pipeline. They share nothing except the character set.
2. **Large installations add up.** If you install both ascii-video + manim-video + comfyui, expect gigabytes of Python packages and models in total space. Check disk before proceeding.
3. **Terminal vs file output.** ascii-art produces terminal-safe text; ascii-video produces mp4/gif files. Make sure the deliverable format matches the user's need.
