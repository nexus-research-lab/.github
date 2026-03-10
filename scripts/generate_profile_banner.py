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


def center_text(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text((xy[0] - width / 2, xy[1] - height / 2), text, font=font, fill=fill)


def build_frame(frame_index: int):
    t = frame_index / FRAMES
    image = Image.new("RGBA", (WIDTH, HEIGHT), rgba("#07111d"))
    draw = ImageDraw.Draw(image)

    add_glow(image, (220, 110), 220, rgba("#0f2e57", 160), 96)
    add_glow(image, (1060, 96), 180, rgba("#23dfff", 56), 82)
    add_glow(image, (1010, 270), 180, rgba("#84a7ff", 42), 80)
    add_glow(image, (WIDTH // 2, HEIGHT // 2), 260, rgba("#18e2ff", 30), 120)

    draw_grid(draw, frame_index)

    hub = (760, 178)
    hub_box = (hub[0] - 74, hub[1] - 74, hub[0] + 74, hub[1] + 74)
    pulse_scale = 1 + 0.018 * sin(2 * pi * t)

    for radius, width in zip((88, 132, 186), (3, 2, 2)):
        r = radius * pulse_scale
        cx, cy = hub
        box = (cx - r, cy - r, cx + r, cy + r)
        draw.ellipse(box, outline=rgba("#36506d", 160), width=width)

    stages = [
        ("REQ", (430, 80)),
        ("DESIGN", (525, 130)),
        ("BUILD", (555, 225)),
        ("TEST", (505, 295)),
        ("OPS", (420, 335)),
    ]
    chain_points = [pos for _, pos in stages] + [hub]
    for idx in range(len(chain_points) - 1):
        a = chain_points[idx]
        b = chain_points[idx + 1]
        draw.line((*a, *b), fill=rgba("#4c6686", 168), width=4)
    for idx in range(len(stages) - 1):
        a = stages[idx][1]
        b = stages[idx + 1][1]
        draw.line((*a, *b), fill=rgba("#6ddcff", 210), width=8)

    human = (1060, 106)
    ai = (1060, 256)
    right_bridge = (934, 178)
    draw.line((*hub, *right_bridge), fill=rgba("#dbf9ff", 228), width=12)
    draw.line((*right_bridge, *human), fill=rgba("#6ddcff", 210), width=6)
    draw.line((*right_bridge, *ai), fill=rgba("#89a6ff", 195), width=6)
    draw.arc((915, 66, 1205, 306), start=224, end=315, fill=rgba("#3a5676", 148), width=2)
    draw.arc((915, 66, 1205, 306), start=45, end=136, fill=rgba("#3a5676", 148), width=2)

    orbit_radius = 224
    orbit_points = []
    for idx in range(7):
        angle = (-0.14 + idx / 7) * 2 * pi
        orbit_points.append((hub[0] + orbit_radius * cos(angle), hub[1] + orbit_radius * sin(angle)))
    for point in orbit_points:
        draw.ellipse((point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6), fill=rgba("#dff8ff", 215))
    for start_index, end_index in ((0, 3), (2, 5)):
        draw.line((*orbit_points[start_index], *orbit_points[end_index]), fill=rgba("#314967", 118), width=2)

    animated_paths = [
        (stages[0][1], stages[1][1]),
        (stages[1][1], stages[2][1]),
        (stages[2][1], stages[3][1]),
        (stages[3][1], stages[4][1]),
        (stages[4][1], hub),
        (human, right_bridge),
        (ai, right_bridge),
        (right_bridge, hub),
    ]
    for idx, (start, end) in enumerate(animated_paths):
        pulse_t = (t * 1.45 + idx * 0.14) % 1
        pulse_xy = point_lerp(start, end, pulse_t)
        add_glow(image, pulse_xy, 15, rgba("#2af1ff", 165), 18)
        draw.ellipse((pulse_xy[0] - 5, pulse_xy[1] - 5, pulse_xy[0] + 5, pulse_xy[1] + 5), fill=rgba("#ffffff", 255))

    hub_shape = [
        (hub[0], hub[1] - 84),
        (hub[0] + 84, hub[1]),
        (hub[0], hub[1] + 84),
        (hub[0] - 84, hub[1]),
    ]
    draw.polygon(hub_shape, outline=rgba("#dffbff", 230), fill=rgba("#08121e", 220), width=5)
    draw.rounded_rectangle(hub_box, radius=28, outline=rgba("#6de5ff", 255), width=4)

    title_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Bold.ttf"), 54)
    mono_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 20)
    mono_small = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 16)
    cn_font = ImageFont.truetype(str(CN_FONT), 28)

    draw.text((84, 84), "NEXUS", font=title_font, fill=rgba("#eef8ff", 250))
    draw.text((84, 136), "RESEARCH LAB", font=title_font, fill=rgba("#6adfff", 230))
    draw.text(
        (84, 186),
        "the full-chain core hub for software creation",
        font=mono_font,
        fill=rgba("#9fb6d1", 240),
    )
    draw.text(
        (84, 224),
        "道枢：以 AI 为核心枢纽，打通软件研发全链路",
        font=cn_font,
        fill=rgba("#dce9ff", 232),
    )
    draw.text(
        (84, 298),
        "full-chain hub  |  human <-> ai symbiosis",
        font=mono_small,
        fill=rgba("#6f84a6", 214),
    )

    for label, (x, y) in stages:
        add_glow(image, (x, y), 18, rgba("#20deff", 82), 16)
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=rgba("#d8fbff", 240))
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rgba("#25e6ff", 255))
        draw.text((x - 28, y - 33), label, font=mono_small, fill=rgba("#b5c7dd", 230))

    for label, point, fill in (("HUMAN", human, rgba("#7de0ff", 255)), ("AI", ai, rgba("#93a9ff", 255))):
        add_glow(image, point, 22, fill[:-1] + (88,), 16)
        draw.ellipse((point[0] - 15, point[1] - 15, point[0] + 15, point[1] + 15), fill=rgba("#dff8ff", 238))
        draw.ellipse((point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6), fill=fill)
        draw.text((point[0] - 28, point[1] - 38), label, font=mono_small, fill=rgba("#dce7ff", 236))

    center_text(draw, (hub[0], hub[1] - 10), "NEXUS", mono_font, rgba("#eef8ff", 255))
    center_text(draw, (hub[0], hub[1] + 18), "CORE HUB", mono_small, rgba("#6adfff", 255))

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
