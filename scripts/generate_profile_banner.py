from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")

HERO_OUT = ASSETS / "nexus-profile-hero-monochrome.png"
MOTION_OUT = ASSETS / "nexus-system-motion-monochrome.gif"
AVATAR_OUTS = [ASSETS / "nexus-avatar-final.png", ASSETS / "nexus-avatar.png"]

WIDTH = 1440
HERO_HEIGHT = 460
MOTION_HEIGHT = 420
FRAMES = 24
AVATAR_SIZE = 1024


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


def add_card(canvas, box, radius=34):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=(0, 0, 0, 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow, (x0, y0 + 8))

    card = Image.new("RGBA", (width, height), (245, 245, 243, 255))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        outline=(26, 26, 26, 44),
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


def generate_motion_frames():
    frames = []
    card_box = (28, 16, WIDTH - 28, MOTION_HEIGHT - 16)
    hub = (770, 210)
    human = (1168, 152)
    ai = (1168, 268)
    labels = ["REQUIRE", "DESIGN", "BUILD", "TEST", "OPERATE"]
    stage_nodes = [
        (206, 118),
        (226, 164),
        (238, 210),
        (226, 256),
        (206, 302),
    ]
    hub_entries = [
        (hub[0] - 84, hub[1] - 54),
        (hub[0] - 84, hub[1] - 26),
        (hub[0] - 84, hub[1]),
        (hub[0] - 84, hub[1] + 26),
        (hub[0] - 84, hub[1] + 54),
    ]
    stage_paths = []
    for start, end in zip(stage_nodes, hub_entries):
        control_1 = (start[0] + 156, start[1])
        control_2 = (hub[0] - 210, (start[1] + end[1]) / 2)
        stage_paths.append((start, control_1, control_2, end))

    human_forward = ((hub[0] + 72, hub[1] - 18), (908, 164), (1036, 134), (human[0] - 18, human[1]))
    human_return = ((human[0] - 18, human[1] + 12), (1044, 176), (914, 198), (hub[0] + 62, hub[1] - 4))
    ai_forward = ((hub[0] + 72, hub[1] + 18), (908, 256), (1036, 286), (ai[0] - 18, ai[1]))
    ai_return = ((ai[0] - 18, ai[1] - 12), (1044, 244), (914, 222), (hub[0] + 62, hub[1] + 4))

    for frame_index in range(FRAMES):
        phase = frame_index / FRAMES
        canvas = make_canvas((WIDTH, MOTION_HEIGHT), (246, 248, 250, 255))
        add_card(canvas, card_box, radius=34)
        draw = ImageDraw.Draw(canvas)

        draw.text(
            (96, 72),
            "FULL-CHAIN CONVERGENCE / HUMAN <-> AI CO-CREATION",
            font=font("IBMPlexMono-Regular.ttf", 18),
            fill=(96, 96, 96, 255),
        )
        draw.line((96, 98, 1344, 98), fill=(10, 10, 10, 16), width=1)

        for path in stage_paths:
            draw_bezier(draw, *path, fill=(24, 24, 24, 132), width=2)

        draw_bezier(draw, *human_forward, fill=(24, 24, 24, 144), width=2)
        draw_bezier(draw, *ai_forward, fill=(24, 24, 24, 144), width=2)
        draw_bezier(draw, *human_return, fill=(24, 24, 24, 68), width=1)
        draw_bezier(draw, *ai_return, fill=(24, 24, 24, 68), width=1)

        for idx, center in enumerate(stage_nodes):
            pulse_strength = max(0.0, sin((phase * 2 * pi) - idx * 0.62)) * 0.48
            draw_chain_node(draw, center, labels[idx], pulse_strength)

        draw_terminal(draw, human, "HUMAN")
        draw_terminal(draw, ai, "AI")
        draw_hub(draw, hub, phase)

        for idx, path in enumerate(stage_paths):
            progress = (phase + idx * 0.16) % 1.0
            pulse = bezier_point(*path, progress)
            draw_pulse(draw, pulse, 5, 196)

        for path, offset, alpha in (
            (human_forward, 0.12, 188),
            (ai_forward, 0.54, 188),
            (human_return, 0.46, 110),
            (ai_return, 0.86, 110),
        ):
            pulse = bezier_point(*path, (phase + offset) % 1.0)
            draw_pulse(draw, pulse, 5, alpha)

        frames.append(canvas)

    return frames


def save_gif(frames):
    paletted = []
    for frame in frames:
        converted = frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64, dither=Image.Dither.NONE)
        paletted.append(converted)

    paletted[0].save(
        MOTION_OUT,
        save_all=True,
        append_images=paletted[1:],
        optimize=True,
        duration=90,
        loop=0,
        disposal=2,
    )


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_hero_card()
    generate_avatar()
    save_gif(generate_motion_frames())


if __name__ == "__main__":
    main()
