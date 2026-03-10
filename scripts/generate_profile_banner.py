from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")

HERO_OUT = ASSETS / "nexus-profile-hero-monochrome.png"
MOTION_OUT = ASSETS / "nexus-system-motion-monochrome.gif"
MOTION_LIGHT_OUT = ASSETS / "nexus-system-motion-light.gif"
MOTION_DARK_OUT = ASSETS / "nexus-system-motion-dark.gif"
AVATAR_OUTS = [ASSETS / "nexus-avatar-final.png", ASSETS / "nexus-avatar.png"]

WIDTH = 1440
HERO_HEIGHT = 460
MOTION_HEIGHT = 520
FRAMES = 16
AVATAR_SIZE = 1024

THEMES = {
    "light": {
        "canvas_bg": (246, 248, 250, 255),
        "card_bg": (245, 245, 243, 255),
        "card_border": (26, 26, 26, 44),
        "grid_minor": (24, 24, 24, 20),
        "grid_major": (24, 24, 24, 34),
        "primary": (18, 18, 18, 255),
        "secondary": (84, 84, 84, 255),
        "muted": (116, 116, 116, 255),
        "line": (24, 24, 24, 210),
        "line_soft": (24, 24, 24, 92),
        "pulse": (10, 10, 10, 255),
        "hub_fill": (252, 252, 251, 255),
    },
    "dark": {
        "canvas_bg": (13, 17, 23, 255),
        "card_bg": (17, 21, 28, 255),
        "card_border": (236, 236, 236, 36),
        "grid_minor": (236, 236, 236, 12),
        "grid_major": (236, 236, 236, 20),
        "primary": (238, 240, 243, 255),
        "secondary": (184, 190, 198, 255),
        "muted": (138, 145, 154, 255),
        "line": (228, 232, 238, 210),
        "line_soft": (228, 232, 238, 72),
        "pulse": (255, 255, 255, 255),
        "hub_fill": (22, 28, 36, 255),
    },
}


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def fit_text(draw, text, font_name, max_size, min_size, max_width):
    for size in range(max_size, min_size - 1, -2):
        current = font(font_name, size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=current)
        if right - left <= max_width:
            return current
    return font(font_name, min_size)


def make_canvas(size, color=(0, 0, 0, 0)):
    return Image.new("RGBA", size, color)


def add_card(canvas, box, radius=34, bg=(245, 245, 243, 255), border=(26, 26, 26, 44)):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=(0, 0, 0, 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow, (x0, y0 + 8))

    card = Image.new("RGBA", (width, height), bg)
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        outline=border,
        width=1,
    )
    canvas.alpha_composite(card, (x0, y0))


def draw_diamond(draw, center, radius, outline, width):
    x, y = center
    points = [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)]
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def draw_nexus_mark(draw, center, radius):
    x, y = center
    outer = radius
    inner = int(radius * 0.66)
    diamond = int(radius * 0.78)
    outer_width = max(3, int(radius * 0.055))
    inner_width = max(2, int(radius * 0.025))
    frame_width = max(4, int(radius * 0.075))
    node_radius = max(8, int(radius * 0.09))
    soft = (90, 90, 90, 165)
    black = (14, 14, 14, 255)

    draw.ellipse((x - outer, y - outer, x + outer, y + outer), outline=soft, width=outer_width)
    draw.ellipse((x - outer + 18, y - outer + 18, x + outer - 18, y + outer - 18), outline=(150, 150, 150, 108), width=inner_width)
    draw.rounded_rectangle(
        (x - inner, y - inner, x + inner, y + inner),
        radius=int(inner * 0.34),
        outline=black,
        width=frame_width,
    )
    draw_diamond(draw, center, diamond, black, frame_width)
    draw.line((x - outer, y, x + outer, y), fill=black, width=frame_width)
    draw.line((x, y - outer, x, y + outer), fill=black, width=frame_width)

    for dx, dy in ((0, -outer), (outer, 0), (0, outer), (-outer, 0)):
        draw.ellipse((x + dx - node_radius, y + dy - node_radius, x + dx + node_radius, y + dy + node_radius), fill=black)


def generate_hero_card():
    canvas = make_canvas((WIDTH, HERO_HEIGHT))
    add_card(canvas, (28, 24, WIDTH - 28, HERO_HEIGHT - 24), radius=34)
    draw = ImageDraw.Draw(canvas)

    draw_nexus_mark(draw, (252, 230), 108)

    title_font = fit_text(draw, "NEXUS", "Outfit-Bold.ttf", 126, 96, 560)
    lab_font = fit_text(draw, "RESEARCH LAB", "Outfit-Bold.ttf", 86, 68, 740)
    meta_font = font("IBMPlexMono-Regular.ttf", 28)
    kicker_font = font("IBMPlexMono-Regular.ttf", 21)

    draw.line((468, 116, 1302, 116), fill=(10, 10, 10, 38), width=2)
    draw.text((468, 134), "NEXUS", font=title_font, fill=(10, 10, 10, 255))
    draw.text((468, 256), "RESEARCH LAB", font=lab_font, fill=(10, 10, 10, 255))
    draw.text(
        (472, 356),
        "AI-centered hub for end-to-end software creation",
        font=meta_font,
        fill=(66, 66, 66, 255),
    )
    draw.text(
        (470, 80),
        "FULL-CHAIN SYSTEMS / HUMAN <-> AI",
        font=kicker_font,
        fill=(96, 96, 96, 255),
    )

    canvas.save(HERO_OUT)


def bezier_point(p0, p1, p2, p3, t):
    inv = 1 - t
    x = (inv ** 3) * p0[0] + 3 * (inv ** 2) * t * p1[0] + 3 * inv * (t ** 2) * p2[0] + (t ** 3) * p3[0]
    y = (inv ** 3) * p0[1] + 3 * (inv ** 2) * t * p1[1] + 3 * inv * (t ** 2) * p2[1] + (t ** 3) * p3[1]
    return (x, y)


def draw_bezier(draw, p0, p1, p2, p3, fill, width, steps=56):
    points = [bezier_point(p0, p1, p2, p3, idx / steps) for idx in range(steps + 1)]
    for idx in range(len(points) - 1):
        ax, ay = points[idx]
        bx, by = points[idx + 1]
        draw.line((ax, ay, bx, by), fill=fill, width=width)


def draw_chain_node(draw, center, label, pulse=0.0):
    x, y = center
    radius = 13
    if pulse > 0:
        glow = radius + 6
        draw.ellipse(
            (x - glow, y - glow, x + glow, y + glow),
            outline=(24, 24, 24, int(28 + pulse * 56)),
            width=2,
        )
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(245, 245, 243, 255))
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(18, 18, 18, 215), width=3)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(18, 18, 18, 255))
    draw.text((x - 36, y), label, font=font("IBMPlexMono-Regular.ttf", 17), fill=(92, 92, 92, 255), anchor="rm")


def draw_terminal(draw, center, label):
    x, y = center
    draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(245, 245, 243, 255))
    draw.ellipse((x - 16, y - 16, x + 16, y + 16), outline=(18, 18, 18, 220), width=3)
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(18, 18, 18, 168), width=2)
    label_y = y - 34 if label == "HUMAN" else y + 38
    draw.text((x, label_y), label, font=font("IBMPlexMono-Regular.ttf", 18), fill=(92, 92, 92, 255), anchor="mm")


def draw_hub(draw, center, phase):
    x, y = center
    outline = (16, 16, 16, 255)
    soft = (24, 24, 24, 26)
    card_fill = (245, 245, 243, 255)
    orbit = 92
    shell = 64
    inner = 42

    draw.ellipse((x - orbit, y - orbit, x + orbit, y + orbit), outline=soft, width=2)
    draw.ellipse((x - orbit + 12, y - orbit + 12, x + orbit - 12, y + orbit - 12), outline=(24, 24, 24, 18), width=1)
    draw.ellipse((x - shell, y - shell, x + shell, y + shell), outline=outline, width=3)
    draw.rounded_rectangle((x - inner, y - inner, x + inner, y + inner), radius=18, outline=outline, width=3)
    draw_diamond(draw, center, 50, outline, 3)

    for angle_offset in (0.0, 0.33, 0.66):
        angle = (phase + angle_offset) * 2 * pi
        px = x + (orbit - 6) * sin(angle)
        py = y - (orbit - 6) * cos(angle)
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(18, 18, 18, 88))

    draw.ellipse((x - 20, y - 20, x + 20, y + 20), fill=card_fill)
    draw.ellipse((x - 20, y - 20, x + 20, y + 20), outline=(18, 18, 18, 112), width=1)


def draw_pulse(draw, point, radius, alpha):
    x, y = point
    fill = (12, 12, 12, alpha)
    glow = (40, 40, 40, max(0, alpha // 6))
    draw.ellipse((x - radius - 4, y - radius - 4, x + radius + 4, y + radius + 4), fill=glow)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def generate_avatar():
    canvas = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (244, 244, 242, 255))
    draw = ImageDraw.Draw(canvas)
    center = AVATAR_SIZE // 2

    halo = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.ellipse((116, 116, AVATAR_SIZE - 116, AVATAR_SIZE - 116), fill=(0, 0, 0, 10))
    halo = halo.filter(ImageFilter.GaussianBlur(24))
    canvas.alpha_composite(halo)

    draw.ellipse((140, 140, AVATAR_SIZE - 140, AVATAR_SIZE - 140), fill=(239, 239, 237, 255))
    draw.ellipse((140, 140, AVATAR_SIZE - 140, AVATAR_SIZE - 140), outline=(18, 18, 18, 28), width=2)
    draw_nexus_mark(draw, (center, center), 252)

    for output in AVATAR_OUTS:
        canvas.save(output)


def polyline_lengths(points):
    lengths = [0.0]
    total = 0.0
    for idx in range(len(points) - 1):
        ax, ay = points[idx]
        bx, by = points[idx + 1]
        total += ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        lengths.append(total)
    return lengths, total


def point_on_polyline(points, progress):
    lengths, total = polyline_lengths(points)
    target = total * progress
    for idx in range(len(points) - 1):
        start_len = lengths[idx]
        end_len = lengths[idx + 1]
        if target <= end_len:
            span = end_len - start_len or 1
            local = (target - start_len) / span
            ax, ay = points[idx]
            bx, by = points[idx + 1]
            return (ax + (bx - ax) * local, ay + (by - ay) * local)
    return points[-1]


def draw_grid(draw, card_box, theme):
    x0, y0, x1, y1 = card_box
    for x in range(x0 + 30, x1 - 29, 36):
        color = theme["grid_major"] if (x - x0) % 144 == 0 else theme["grid_minor"]
        draw.line((x, y0 + 20, x, y1 - 20), fill=color, width=1)
    for y in range(y0 + 20, y1 - 19, 36):
        color = theme["grid_major"] if (y - y0) % 108 == 0 else theme["grid_minor"]
        draw.line((x0 + 20, y, x1 - 20, y), fill=color, width=1)


def draw_polyline(draw, points, fill, width):
    for idx in range(len(points) - 1):
        ax, ay = points[idx]
        bx, by = points[idx + 1]
        draw.line((ax, ay, bx, by), fill=fill, width=width)


def draw_motion_node(draw, center, theme, label, label_pos, pulse=0.0, terminal=False):
    x, y = center
    radius = 14 if terminal else 13
    if pulse > 0:
        glow = radius + 5
        draw.ellipse(
            (x - glow, y - glow, x + glow, y + glow),
            outline=(theme["primary"][0], theme["primary"][1], theme["primary"][2], int(36 + pulse * 56)),
            width=2,
        )
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=theme["card_bg"])
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=theme["primary"], width=3)
    if terminal:
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), outline=theme["secondary"], width=2)
    else:
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=theme["primary"])
    draw.text(label_pos, label, font=font("IBMPlexMono-Regular.ttf", 18), fill=theme["secondary"], anchor="mm")


def draw_motion_hub(draw, center, theme):
    x, y = center
    primary = theme["primary"]
    secondary = theme["secondary"]
    fill = theme["hub_fill"]
    guide = theme["grid_major"]

    draw.rectangle((x - 152, y - 152, x + 152, y + 152), outline=guide, width=1)
    draw.rectangle((x - 112, y - 112, x + 112, y + 112), outline=theme["grid_minor"], width=1)
    draw.line((x - 152, y, x + 152, y), fill=theme["grid_minor"], width=1)
    draw.line((x, y - 152, x, y + 152), fill=theme["grid_minor"], width=1)

    draw.rounded_rectangle((x - 82, y - 82, x + 82, y + 82), radius=28, fill=fill, outline=primary, width=4)
    draw_diamond(draw, center, 92, primary, 4)
    draw.rounded_rectangle((x - 60, y - 60, x + 60, y + 60), radius=20, outline=secondary, width=2)
    draw.rounded_rectangle((x - 58, y - 28, x + 58, y + 34), radius=14, fill=fill)
    draw.text((x, y - 6), "NEXUS", font=font("Outfit-Bold.ttf", 28), fill=primary, anchor="mm")
    draw.text((x, y + 24), "AI CORE HUB", font=font("IBMPlexMono-Regular.ttf", 16), fill=secondary, anchor="mm")


def generate_motion_frames(theme_name):
    theme = THEMES[theme_name]
    frames = []
    card_box = (28, 20, WIDTH - 28, MOTION_HEIGHT - 20)
    hub = (844, 274)
    bridge = (1010, 274)
    human = (1208, 184)
    ai = (1208, 352)
    stages = [
        ("REQ", (500, 164), (448, 164)),
        ("DESIGN", (596, 214), (520, 214)),
        ("BUILD", (632, 284), (572, 284)),
        ("TEST", (576, 356), (522, 356)),
        ("OPERATE", (476, 420), (410, 420)),
    ]
    stage_entries = [
        (hub[0] - 96, hub[1] - 92),
        (hub[0] - 96, hub[1] - 46),
        (hub[0] - 96, hub[1]),
        (hub[0] - 96, hub[1] + 50),
        (hub[0] - 96, hub[1] + 96),
    ]
    stage_paths = []
    for idx, (_, start, _) in enumerate(stages):
        bend = (682, start[1])
        stage_paths.append([start, bend, stage_entries[idx]])

    human_forward = [(hub[0] + 96, hub[1] - 18), bridge, (1118, 224), human]
    ai_forward = [(hub[0] + 96, hub[1] + 18), bridge, (1118, 312), ai]
    human_return = [human, (1120, 214), (1016, 252), (hub[0] + 96, hub[1] - 2)]
    ai_return = [ai, (1120, 322), (1016, 296), (hub[0] + 96, hub[1] + 2)]

    mono = "IBMPlexMono-Regular.ttf"
    title_font = font("Outfit-Bold.ttf", 52)
    meta_font = font(mono, 22)
    small_font = font(mono, 18)

    for frame_index in range(FRAMES):
        phase = frame_index / FRAMES
        canvas = make_canvas((WIDTH, MOTION_HEIGHT), theme["canvas_bg"])
        add_card(canvas, card_box, radius=34, bg=theme["card_bg"], border=theme["card_border"])
        draw = ImageDraw.Draw(canvas)

        draw_grid(draw, card_box, theme)
        draw.text((88, 66), "SYSTEM MOTION", font=title_font, fill=theme["primary"])
        draw.text((88, 122), "full-chain orchestration routed through the Nexus AI core", font=meta_font, fill=theme["secondary"])
        draw.text((88, 158), "requirements  ->  design  ->  build  ->  test  ->  operate", font=small_font, fill=theme["muted"])
        draw.text((842, 122), "human feedback  <->  ai execution  <->  shared control", font=small_font, fill=theme["secondary"], anchor="mm")

        for path in stage_paths:
            draw_polyline(draw, path, theme["line"], 4)
        draw_polyline(draw, human_forward, theme["line"], 4)
        draw_polyline(draw, ai_forward, theme["line"], 4)
        draw_polyline(draw, human_return, theme["line_soft"], 2)
        draw_polyline(draw, ai_return, theme["line_soft"], 2)

        for idx, (label, center, label_pos) in enumerate(stages):
            pulse_strength = max(0.0, sin((phase * 2 * pi) - idx * 0.72)) * 0.55
            draw_motion_node(draw, center, theme, label, label_pos, pulse_strength)

        draw_motion_node(draw, human, theme, "HUMAN", (human[0], human[1] - 34), terminal=True)
        draw_motion_node(draw, ai, theme, "AI", (ai[0], ai[1] + 42), terminal=True)
        draw_motion_hub(draw, hub, theme)

        for idx, path in enumerate(stage_paths):
            pulse = point_on_polyline(path, (phase + idx * 0.14) % 1.0)
            draw_pulse(draw, pulse, 7, 210 if theme_name == "light" else 230)

        for path, offset, alpha in (
            (human_forward, 0.18, 205),
            (ai_forward, 0.58, 205),
            (human_return, 0.42, 120),
            (ai_return, 0.82, 120),
        ):
            pulse = point_on_polyline(path, (phase + offset) % 1.0)
            draw_pulse(draw, pulse, 6, alpha if theme_name == "light" else min(255, alpha + 28))

        frames.append(canvas)

    return frames


def save_gif(frames, output_path):
    paletted = []
    for frame in frames:
        converted = frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64, dither=Image.Dither.NONE)
        paletted.append(converted)

    paletted[0].save(
        output_path,
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
    generate_avatar()
    light_frames = generate_motion_frames("light")
    dark_frames = generate_motion_frames("dark")
    save_gif(light_frames, MOTION_OUT)
    save_gif(light_frames, MOTION_LIGHT_OUT)
    save_gif(dark_frames, MOTION_DARK_OUT)


if __name__ == "__main__":
    main()
