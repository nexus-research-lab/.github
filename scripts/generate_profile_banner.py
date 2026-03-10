from math import cos, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")

HERO_OUT = ASSETS / "nexus-profile-hero-monochrome.png"
HERO_PREVIEW = ASSETS / "nexus-profile-hero-monochrome-preview.png"
MOTION_OUT = ASSETS / "nexus-system-motion-monochrome.gif"
MOTION_PREVIEW = ASSETS / "nexus-system-motion-monochrome-preview.png"

WIDTH = 1440
HERO_HEIGHT = 460
MOTION_HEIGHT = 520
FRAMES = 14


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def add_card(canvas, box, radius=34):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=(0, 0, 0, 24))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow, (x0, y0 + 10))

    card = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    border = ImageDraw.Draw(card)
    border.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, outline=(22, 22, 22, 54), width=2)
    canvas.alpha_composite(card, (x0, y0))


def fit_text(draw, text, font_path, max_size, min_size, max_width):
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return ImageFont.truetype(str(font_path), min_size)


def draw_brand_mark(size):
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    c = size // 2
    line = (8, 8, 8, 255)
    soft = (8, 8, 8, 104)

    for radius, width, color in ((112, 12, line), (84, 8, soft), (54, 6, soft)):
        draw.ellipse((c - radius, c - radius, c + radius, c + radius), outline=color, width=width)

    outer = []
    ring = 112
    for idx in range(6):
        angle = -1.5708 + idx * 1.0472
        outer.append((c + ring * cos(angle), c + ring * sin(angle)))

    for point in outer:
        draw.ellipse((point[0] - 12, point[1] - 12, point[0] + 12, point[1] + 12), fill=line)

    for start, end in ((0, 2), (2, 4), (4, 0), (1, 3), (3, 5), (5, 1)):
        draw.line((*outer[start], c, c), fill=soft, width=6)
        draw.line((*outer[start], *outer[end]), fill=soft, width=5)

    diamond = [
        (c, c - 70),
        (c + 70, c),
        (c, c + 70),
        (c - 70, c),
    ]
    draw.polygon(diamond, outline=line, fill=(255, 255, 255, 255), width=10)
    draw.rounded_rectangle((c - 58, c - 58, c + 58, c + 58), radius=20, outline=line, width=8)
    draw.line((c - 94, c, c + 94, c), fill=line, width=8)
    draw.line((c, c - 94, c, c + 94), fill=line, width=8)

    return icon


def generate_hero_card():
    canvas = Image.new("RGBA", (WIDTH, HERO_HEIGHT), (0, 0, 0, 0))
    add_card(canvas, (28, 24, WIDTH - 28, HERO_HEIGHT - 24), radius=34)
    draw = ImageDraw.Draw(canvas)

    icon = draw_brand_mark(270)
    canvas.alpha_composite(icon, (120, 94))

    mono = FONT_DIR / "IBMPlexMono-Regular.ttf"
    title_font = fit_text(draw, "NEXUS", FONT_DIR / "Outfit-Bold.ttf", 142, 92, 630)
    sub_font = fit_text(draw, "RESEARCH LAB", FONT_DIR / "Outfit-Bold.ttf", 82, 48, 630)
    meta_font = ImageFont.truetype(str(mono), 22)

    draw.text((454, 112), "NEXUS", font=title_font, fill=(7, 7, 7, 255))
    draw.text((460, 244), "RESEARCH LAB", font=sub_font, fill=(7, 7, 7, 255))
    draw.text((462, 334), "AI-centered hub for full-chain software creation", font=meta_font, fill=(82, 82, 82, 255))
    canvas.save(HERO_OUT)
    canvas.save(HERO_PREVIEW)


def draw_grid(draw, card_box):
    x0, y0, x1, y1 = card_box
    for x in range(x0 + 36, x1 - 35, 36):
        alpha = 18 if (x - x0) % 144 else 28
        draw.line((x, y0 + 24, x, y1 - 24), fill=(0, 0, 0, alpha), width=1)
    for y in range(y0 + 24, y1 - 23, 36):
        alpha = 16 if (y - y0) % 108 else 24
        draw.line((x0 + 24, y, x1 - 24, y), fill=(0, 0, 0, alpha), width=1)


def node(draw, xy, label, fill=(17, 17, 17, 255), text_fill=(70, 70, 70, 255)):
    x, y = xy
    draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=fill)
    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 255, 255, 255))
    font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 24)
    draw.text((x - 28, y - 42), label, font=font, fill=text_fill)


def lerp(a, b, t):
    return a + (b - a) * t


def point_lerp(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def generate_motion_frames():
    frames = []
    mono = FONT_DIR / "IBMPlexMono-Regular.ttf"
    title_font = ImageFont.truetype(str(FONT_DIR / "Outfit-Bold.ttf"), 52)
    meta_font = ImageFont.truetype(str(mono), 22)
    small_font = ImageFont.truetype(str(mono), 18)

    card_box = (28, 24, WIDTH - 28, MOTION_HEIGHT - 24)
    hub = (836, 274)
    human = (1196, 184)
    ai = (1196, 352)
    bridge = (1002, 274)
    stages = [
        ("REQ", (500, 164)),
        ("DESIGN", (596, 214)),
        ("BUILD", (630, 284)),
        ("TEST", (574, 360)),
        ("OPS", (480, 416)),
    ]
    paths = [
        (stages[0][1], stages[1][1]),
        (stages[1][1], stages[2][1]),
        (stages[2][1], stages[3][1]),
        (stages[3][1], stages[4][1]),
        (stages[4][1], hub),
        (hub, bridge),
        (bridge, human),
        (bridge, ai),
    ]

    for i in range(FRAMES):
        t = i / FRAMES
        canvas = Image.new("RGBA", (WIDTH, MOTION_HEIGHT), (0, 0, 0, 0))
        add_card(canvas, card_box, radius=34)
        draw = ImageDraw.Draw(canvas)

        draw_grid(draw, card_box)

        draw.text((88, 68), "SYSTEM MOTION", font=title_font, fill=(10, 10, 10, 255))
        draw.text((88, 124), "full-chain orchestration routed through a Nexus core hub", font=meta_font, fill=(86, 86, 86, 255))
        draw.text((88, 160), "requirements  ->  design  ->  build  ->  test  ->  operate  ->  human-ai", font=small_font, fill=(116, 116, 116, 255))

        for radius, width in ((96, 2), (148, 2), (210, 1)):
            draw.ellipse((hub[0] - radius, hub[1] - radius, hub[0] + radius, hub[1] + radius), outline=(40, 40, 40, 36), width=width)

        for start, end in paths:
            draw.line((*start, *end), fill=(22, 22, 22, 185), width=6 if end == hub or start == hub else 5)

        diamond = [
            (hub[0], hub[1] - 90),
            (hub[0] + 90, hub[1]),
            (hub[0], hub[1] + 90),
            (hub[0] - 90, hub[1]),
        ]
        draw.polygon(diamond, outline=(0, 0, 0, 255), fill=(255, 255, 255, 255), width=5)
        draw.rounded_rectangle((hub[0] - 78, hub[1] - 78, hub[0] + 78, hub[1] + 78), radius=30, outline=(0, 0, 0, 255), width=4)
        draw.text((hub[0], hub[1] - 8), "NEXUS", font=meta_font, fill=(0, 0, 0, 255), anchor="mm")
        draw.text((hub[0], hub[1] + 24), "CORE HUB", font=small_font, fill=(55, 55, 55, 255), anchor="mm")

        for label, xy in stages:
            node(draw, xy, label)

        node(draw, human, "HUMAN")
        node(draw, ai, "AI")

        orbit_points = []
        for j in range(7):
            angle = (-0.13 + j / 7) * 6.28318
            orbit_points.append((hub[0] + 228 * cos(angle), hub[1] + 228 * sin(angle)))
        for point in orbit_points:
            draw.ellipse((point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6), fill=(20, 20, 20, 70))
        for a, b in ((0, 3), (2, 5)):
            draw.line((*orbit_points[a], *orbit_points[b]), fill=(20, 20, 20, 60), width=2)

        pulse_paths = [
            (stages[0][1], stages[1][1]),
            (stages[1][1], stages[2][1]),
            (stages[2][1], stages[3][1]),
            (stages[3][1], stages[4][1]),
            (stages[4][1], hub),
            (hub, bridge),
            (bridge, human),
            (bridge, ai),
        ]
        for idx, (start, end) in enumerate(pulse_paths):
            pulse_t = (t * 1.35 + idx * 0.14) % 1
            px, py = point_lerp(start, end, pulse_t)
            draw.ellipse((px - 8, py - 8, px + 8, py + 8), fill=(5, 5, 5, 255))

        frames.append(canvas)

    return frames


def save_gif(frames):
    paletted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=32) for frame in frames]
    paletted[0].save(
        MOTION_OUT,
        save_all=True,
        append_images=paletted[1:],
        optimize=True,
        duration=110,
        loop=0,
        disposal=2,
    )


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_hero_card()
    frames = generate_motion_frames()
    frames[0].save(MOTION_PREVIEW)
    save_gif(frames)


if __name__ == "__main__":
    main()
