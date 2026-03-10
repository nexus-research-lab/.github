from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1280
HEIGHT = 360
FRAMES = 18
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
GIF_OUT = ASSETS / "nexus-profile-banner.gif"
PNG_OUT = ASSETS / "nexus-profile-banner-preview.png"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")
CN_FONT = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")


def rgba(hex_color: str, alpha: int = 255):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a, b, t):
    return a + (b - a) * t


def point_lerp(p0, p1, t):
    return (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t))


def add_glow(base: Image.Image, center, radius, color, blur):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_grid(draw: ImageDraw.ImageDraw, frame_index: int):
    x_offset = int((frame_index / FRAMES) * 24)
    y_offset = int((frame_index / FRAMES) * 16)

    for x in range(-x_offset, WIDTH + 32, 32):
        alpha = 24 if x % 128 else 36
        draw.line((x, 0, x, HEIGHT), fill=rgba("#6f84a6", alpha), width=1)

    for y in range(-y_offset, HEIGHT + 32, 32):
        alpha = 20 if y % 96 else 30
        draw.line((0, y, WIDTH, y), fill=rgba("#6f84a6", alpha), width=1)


def build_frame(frame_index: int):
    t = frame_index / FRAMES
    image = Image.new("RGBA", (WIDTH, HEIGHT), rgba("#07111d"))
    draw = ImageDraw.Draw(image)

    add_glow(image, (220, 100), 240, rgba("#0f2e57", 160), 96)
    add_glow(image, (930, 250), 320, rgba("#16c7ff", 48), 110)
    add_glow(image, (WIDTH // 2, HEIGHT // 2), 220, rgba("#18e2ff", 28), 120)

    draw_grid(draw, frame_index)

    cx = WIDTH * 0.57
    cy = HEIGHT * 0.5
    ring_radii = [68, 108, 154]
    pulse_scale = 1 + 0.015 * sin(2 * pi * t)

    for radius, width in zip(ring_radii, [3, 2, 2]):
        r = radius * pulse_scale
        box = (cx - r, cy - r, cx + r, cy + r)
        draw.ellipse(box, outline=rgba("#36506d", 160), width=width)

    nodes = {
        "core_top": (cx, cy - 92),
        "core_bottom": (cx, cy + 92),
        "left_mid": (cx - 114, cy),
        "right_mid": (cx + 114, cy),
        "left_outer": (cx - 230, cy - 96),
        "right_outer": (cx + 238, cy - 112),
        "far_right": (cx + 344, cy + 12),
        "far_left": (cx - 336, cy + 108),
        "lower_left": (cx - 206, cy + 136),
        "lower_right": (cx + 206, cy + 132),
        "top_arc": (cx - 40, cy - 154),
        "bottom_arc": (cx + 18, cy + 158),
    }

    edges = [
        ("core_top", "left_mid"),
        ("left_mid", "core_bottom"),
        ("core_top", "core_bottom"),
        ("core_top", "right_mid"),
        ("right_mid", "core_bottom"),
        ("left_outer", "lower_left"),
        ("left_outer", "left_mid"),
        ("far_left", "left_mid"),
        ("far_left", "far_right"),
        ("right_outer", "lower_right"),
        ("right_outer", "right_mid"),
        ("far_right", "lower_right"),
    ]

    for start_key, end_key in edges:
        start = nodes[start_key]
        end = nodes[end_key]
        draw.line((*start, *end), fill=rgba("#4b6889", 138), width=3)

    draw.line((*nodes["core_top"], *nodes["left_mid"]), fill=rgba("#6ddcff", 255), width=10)
    draw.line((*nodes["left_mid"], *nodes["core_bottom"]), fill=rgba("#6ddcff", 255), width=10)
    draw.line((*nodes["core_top"], *nodes["core_bottom"]), fill=rgba("#d1f8ff", 230), width=14)

    outer_ring = []
    orbit_radius = 270
    for idx in range(8):
        angle = (-0.13 + idx / 8) * 2 * pi
        outer_ring.append((cx + orbit_radius * cos(angle), cy + orbit_radius * sin(angle)))

    for point in outer_ring:
        draw.ellipse((point[0] - 7, point[1] - 7, point[0] + 7, point[1] + 7), fill=rgba("#dff8ff", 220))

    for start_index, end_index in ((0, 3), (2, 5), (4, 7)):
        draw.line((*outer_ring[start_index], *outer_ring[end_index]), fill=rgba("#314967", 130), width=2)

    for idx, (start_key, end_key) in enumerate(edges[:8]):
        pulse_t = (t * 1.6 + idx * 0.11) % 1
        pulse_xy = point_lerp(nodes[start_key], nodes[end_key], pulse_t)
        add_glow(image, pulse_xy, 14, rgba("#2af1ff", 160), 18)
        draw.ellipse((pulse_xy[0] - 5, pulse_xy[1] - 5, pulse_xy[0] + 5, pulse_xy[1] + 5), fill=rgba("#ffffff", 255))

    for x, y in nodes.values():
        add_glow(image, (x, y), 16, rgba("#21e5ff", 90), 14)
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=rgba("#d6fbff", 242))
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=rgba("#23e7ff", 255))

    draw.rounded_rectangle(
        (cx - 84, cy - 84, cx + 84, cy + 84),
        radius=28,
        outline=rgba("#dffbff", 235),
        width=5,
    )
    draw.rounded_rectangle(
        (cx - 52, cy - 52, cx + 52, cy + 52),
        radius=20,
        fill=rgba("#07111d", 220),
        outline=rgba("#3be6ff", 255),
        width=4,
    )

    title_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Bold.ttf"), 54)
    mono_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 20)
    serif_font = ImageFont.truetype(str(CN_FONT), 28)

    draw.text((84, 84), "NEXUS", font=title_font, fill=rgba("#eef8ff", 250))
    draw.text((84, 136), "RESEARCH LAB", font=title_font, fill=rgba("#6adfff", 230))
    draw.text(
        (84, 186),
        "connecting research, systems, and intelligence",
        font=mono_font,
        fill=rgba("#9fb6d1", 240),
    )
    draw.text(
        (84, 224),
        "连接研究、系统与智能",
        font=serif_font,
        fill=rgba("#dce9ff", 232),
    )

    for idx, label in enumerate(("AGENTS", "SYSTEMS", "MEMORY", "INTERFACES")):
        draw.text((84 + idx * 128, 292), label, font=mono_font, fill=rgba("#6f84a6", 214))

    scan_x = int(lerp(-180, WIDTH + 80, t))
    scan = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sd.rectangle((scan_x, 0, scan_x + 96, HEIGHT), fill=rgba("#cfffff", 20))
    scan = scan.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(scan)

    return image


def save_gif(frames):
    palettes = []
    for frame in frames:
        palettes.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

    palettes[0].save(
        GIF_OUT,
        save_all=True,
        append_images=palettes[1:],
        optimize=True,
        duration=90,
        loop=0,
        disposal=2,
    )


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    frames = [build_frame(i) for i in range(FRAMES)]
    frames[0].save(PNG_OUT)
    save_gif(frames)


if __name__ == "__main__":
    main()
