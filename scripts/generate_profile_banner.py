from dataclasses import dataclass
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1280
HEIGHT = 360
FRAMES = 18
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")
CN_FONT = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    glow_left: str
    glow_right: str
    glow_center: str
    grid_minor: str
    grid_major: str
    ring: str
    orbit_line: str
    chain_base: str
    chain_primary: str
    hub_fill: str
    hub_outline: str
    text_primary: str
    text_accent: str
    text_secondary: str
    strip_text: str
    node_outer: str
    node_inner: str
    human: str
    ai: str
    bridge: str
    pulse: str
    scan: str


THEMES = (
    Theme(
        name="dark",
        bg="#07111d",
        glow_left="#11325c",
        glow_right="#16325a",
        glow_center="#18dfff",
        grid_minor="#6f84a6",
        grid_major="#8aa3c2",
        ring="#3a5371",
        orbit_line="#304867",
        chain_base="#4c6686",
        chain_primary="#6ddcff",
        hub_fill="#091321",
        hub_outline="#dffbff",
        text_primary="#eef8ff",
        text_accent="#70e2ff",
        text_secondary="#a3b8d4",
        strip_text="#7d93af",
        node_outer="#d8fbff",
        node_inner="#25e7ff",
        human="#7de0ff",
        ai="#9aa7ff",
        bridge="#dbf9ff",
        pulse="#2af1ff",
        scan="#d7ffff",
    ),
    Theme(
        name="light",
        bg="#f6f9fd",
        glow_left="#d5e7ff",
        glow_right="#d8f7ff",
        glow_center="#8ae7ff",
        grid_minor="#d4dceb",
        grid_major="#bcc9dd",
        ring="#9db0c9",
        orbit_line="#c3d0e2",
        chain_base="#8ea3bf",
        chain_primary="#1a8ec0",
        hub_fill="#ffffff",
        hub_outline="#1b344b",
        text_primary="#163149",
        text_accent="#1094c7",
        text_secondary="#4c6784",
        strip_text="#687c97",
        node_outer="#ffffff",
        node_inner="#16a6dc",
        human="#1599d3",
        ai="#6f85ee",
        bridge="#24425b",
        pulse="#0ecbff",
        scan="#ffffff",
    ),
)


def rgba(hex_color: str, alpha: int = 255):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a, b, t):
    return a + (b - a) * t


def point_lerp(p0, p1, t):
    return (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t))


def center_text(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text((xy[0] - width / 2, xy[1] - height / 2), text, font=font, fill=fill)


def add_glow(base: Image.Image, center, radius, color, blur):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_grid(draw: ImageDraw.ImageDraw, frame_index: int, theme: Theme):
    x_offset = int((frame_index / FRAMES) * 18)
    y_offset = int((frame_index / FRAMES) * 12)

    for x in range(-x_offset, WIDTH + 32, 32):
        alpha = 30 if x % 128 else 48
        color = theme.grid_minor if x % 128 else theme.grid_major
        draw.line((x, 0, x, HEIGHT), fill=rgba(color, alpha), width=1)

    for y in range(-y_offset, HEIGHT + 32, 32):
        alpha = 26 if y % 96 else 40
        color = theme.grid_minor if y % 96 else theme.grid_major
        draw.line((0, y, WIDTH, y), fill=rgba(color, alpha), width=1)


def draw_node(image: Image.Image, draw: ImageDraw.ImageDraw, point, theme: Theme, size=12):
    add_glow(image, point, size + 8, rgba(theme.node_inner, 78), 14)
    draw.ellipse((point[0] - size, point[1] - size, point[0] + size, point[1] + size), fill=rgba(theme.node_outer, 238))
    draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=rgba(theme.node_inner))


def build_frame(frame_index: int, theme: Theme):
    t = frame_index / FRAMES
    image = Image.new("RGBA", (WIDTH, HEIGHT), rgba(theme.bg))
    draw = ImageDraw.Draw(image)

    add_glow(image, (190, 105), 220, rgba(theme.glow_left, 140), 90)
    add_glow(image, (1020, 92), 170, rgba(theme.glow_right, 78), 76)
    add_glow(image, (1015, 284), 170, rgba(theme.ai, 44), 72)
    add_glow(image, (775, 180), 260, rgba(theme.glow_center, 24), 118)

    draw_grid(draw, frame_index, theme)

    hub = (790, 178)
    human = (1086, 104)
    ai = (1086, 256)
    right_bridge = (948, 178)
    stages = [
        ("REQ", (430, 82)),
        ("DESIGN", (525, 126)),
        ("BUILD", (555, 201)),
        ("TEST", (505, 271)),
        ("OPS", (420, 312)),
    ]

    pulse_scale = 1 + 0.016 * sin(2 * pi * t)
    for radius, width in zip((92, 136, 192), (3, 2, 2)):
        r = radius * pulse_scale
        box = (hub[0] - r, hub[1] - r, hub[0] + r, hub[1] + r)
        draw.ellipse(box, outline=rgba(theme.ring, 148), width=width)

    chain_points = [pos for _, pos in stages] + [hub]
    for idx in range(len(chain_points) - 1):
        a = chain_points[idx]
        b = chain_points[idx + 1]
        draw.line((*a, *b), fill=rgba(theme.chain_base, 145), width=4)

    for idx in range(len(stages) - 1):
        a = stages[idx][1]
        b = stages[idx + 1][1]
        draw.line((*a, *b), fill=rgba(theme.chain_primary, 228), width=8)

    draw.line((*hub, *right_bridge), fill=rgba(theme.bridge, 230), width=11)
    draw.line((*right_bridge, *human), fill=rgba(theme.human, 216), width=6)
    draw.line((*right_bridge, *ai), fill=rgba(theme.ai, 202), width=6)
    draw.arc((938, 62, 1234, 304), start=225, end=315, fill=rgba(theme.ring, 135), width=2)
    draw.arc((938, 62, 1234, 304), start=45, end=136, fill=rgba(theme.ring, 135), width=2)

    orbit_radius = 226
    orbit_points = []
    for idx in range(7):
        angle = (-0.14 + idx / 7) * 2 * pi
        orbit_points.append((hub[0] + orbit_radius * cos(angle), hub[1] + orbit_radius * sin(angle)))
    for point in orbit_points:
        draw.ellipse((point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6), fill=rgba(theme.node_outer, 190))
    for start_index, end_index in ((0, 3), (2, 5)):
        draw.line((*orbit_points[start_index], *orbit_points[end_index]), fill=rgba(theme.orbit_line, 120), width=2)

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
        pulse_t = (t * 1.38 + idx * 0.16) % 1
        pulse_xy = point_lerp(start, end, pulse_t)
        add_glow(image, pulse_xy, 15, rgba(theme.pulse, 150), 18)
        draw.ellipse((pulse_xy[0] - 5, pulse_xy[1] - 5, pulse_xy[0] + 5, pulse_xy[1] + 5), fill=rgba("#ffffff", 255))

    diamond = [
        (hub[0], hub[1] - 84),
        (hub[0] + 84, hub[1]),
        (hub[0], hub[1] + 84),
        (hub[0] - 84, hub[1]),
    ]
    draw.polygon(diamond, outline=rgba(theme.hub_outline, 230), fill=rgba(theme.hub_fill, 228), width=5)
    draw.rounded_rectangle(
        (hub[0] - 74, hub[1] - 74, hub[0] + 74, hub[1] + 74),
        radius=28,
        outline=rgba(theme.chain_primary, 240),
        width=4,
    )

    title_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Bold.ttf"), 54)
    mono_font = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 20)
    mono_small = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 16)
    cn_font = ImageFont.truetype(str(CN_FONT), 27)

    draw.text((84, 82), "NEXUS", font=title_font, fill=rgba(theme.text_primary, 250))
    draw.text((84, 134), "RESEARCH LAB", font=title_font, fill=rgba(theme.text_accent, 232))
    draw.text((84, 184), "the ai-centered hub for software creation", font=mono_font, fill=rgba(theme.text_secondary, 238))
    draw.text((84, 221), "道枢：以 AI 为核心枢纽，打通端到端软件开发全链路", font=cn_font, fill=rgba(theme.text_primary, 232))
    draw.text((84, 296), "full-chain hub  |  human <-> ai symbiosis", font=mono_small, fill=rgba(theme.strip_text, 220))

    for label, (x, y) in stages:
        draw_node(image, draw, (x, y), theme)
        draw.text((x - 28, y - 33), label, font=mono_small, fill=rgba(theme.text_secondary, 236))

    for label, point, fill in (("HUMAN", human, theme.human), ("AI", ai, theme.ai)):
        add_glow(image, point, 24, rgba(fill, 64), 16)
        draw.ellipse((point[0] - 15, point[1] - 15, point[0] + 15, point[1] + 15), fill=rgba(theme.node_outer, 235))
        draw.ellipse((point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6), fill=rgba(fill))
        draw.text((point[0] - 30, point[1] - 39), label, font=mono_small, fill=rgba(theme.text_secondary, 235))

    center_text(draw, (hub[0], hub[1] - 11), "NEXUS", mono_font, rgba(theme.text_primary, 255))
    center_text(draw, (hub[0], hub[1] + 19), "CORE HUB", mono_small, rgba(theme.text_accent, 255))

    scan_x = int(lerp(-180, WIDTH + 80, t))
    scan = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan)
    scan_draw.rectangle((scan_x, 0, scan_x + 86, HEIGHT), fill=rgba(theme.scan, 18))
    scan = scan.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(scan)

    return image


def save_gif(frames, path: Path):
    paletted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    paletted[0].save(
        path,
        save_all=True,
        append_images=paletted[1:],
        optimize=True,
        duration=90,
        loop=0,
        disposal=2,
    )


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        frames = [build_frame(i, theme) for i in range(FRAMES)]
        frames[0].save(ASSETS / f"nexus-profile-banner-{theme.name}-preview.png")
        save_gif(frames, ASSETS / f"nexus-profile-banner-{theme.name}.gif")


if __name__ == "__main__":
    main()
