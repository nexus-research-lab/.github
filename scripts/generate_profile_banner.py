from math import pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = Path("/Users/berhand/.agents/skills/canvas-design/canvas-fonts")

HERO_OUT = ASSETS / "nexus-profile-hero-monochrome.png"
MOTION_OUT = ASSETS / "nexus-system-motion-monochrome.gif"

WIDTH = 1440
HERO_HEIGHT = 460
MOTION_HEIGHT = 420
FRAMES = 24


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def fit_text(draw, text, font_name, max_size, min_size, max_width):
    for size in range(max_size, min_size - 1, -2):
        current = font(font_name, size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=current)
        if right - left <= max_width:
            return current
    return font(font_name, min_size)


def make_canvas(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def add_card(canvas, box, radius=34):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(shadow, (x0, y0 + 8))

    card = Image.new("RGBA", (width, height), (245, 245, 243, 255))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        outline=(26, 26, 26, 70),
        width=2,
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
    soft = (90, 90, 90, 180)
    black = (14, 14, 14, 255)

    draw.ellipse((x - outer, y - outer, x + outer, y + outer), outline=soft, width=6)
    draw.ellipse((x - outer + 18, y - outer + 18, x + outer - 18, y + outer - 18), outline=(150, 150, 150, 120), width=3)
    draw.rounded_rectangle(
        (x - inner, y - inner, x + inner, y + inner),
        radius=int(inner * 0.34),
        outline=black,
        width=8,
    )
    draw_diamond(draw, center, diamond, black, 8)
    draw.line((x - outer, y, x + outer, y), fill=black, width=8)
    draw.line((x, y - outer, x, y + outer), fill=black, width=8)

    for dx, dy in ((0, -outer), (outer, 0), (0, outer), (-outer, 0)):
        draw.ellipse((x + dx - 10, y + dy - 10, x + dx + 10, y + dy + 10), fill=black)


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


def draw_stage(draw, x, y, label, label_y, pulse=0.0):
    radius = 13 + int(round(pulse * 2))
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(18, 18, 18, 255))
    inner = max(4, radius - 7)
    draw.ellipse((x - inner, y - inner, x + inner, y + inner), fill=(245, 245, 243, 255))
    draw.text((x, label_y), label, font=font("IBMPlexMono-Regular.ttf", 18), fill=(92, 92, 92, 255), anchor="mm")


def draw_hub(draw, center, phase):
    x, y = center
    outer = 68 + int(round(4 * sin(phase * 2 * pi)))
    mid = 52
    outline = (16, 16, 16, 255)
    soft = (24, 24, 24, 44)

    draw.ellipse((x - outer - 20, y - outer - 20, x + outer + 20, y + outer + 20), outline=soft, width=3)
    draw.ellipse((x - outer, y - outer, x + outer, y + outer), outline=outline, width=6)
    draw.rounded_rectangle((x - mid, y - mid, x + mid, y + mid), radius=20, outline=outline, width=5)
    draw_diamond(draw, center, 58, outline, 5)
    draw.text((x, y - 10), "NEXUS", font=font("Outfit-Bold.ttf", 30), fill=outline, anchor="mm")
    draw.text((x, y + 22), "HUB", font=font("IBMPlexMono-Regular.ttf", 20), fill=(82, 82, 82, 255), anchor="mm")


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


def draw_pulse(draw, point, radius, alpha):
    x, y = point
    fill = (12, 12, 12, alpha)
    glow = (40, 40, 40, max(0, alpha // 4))
    draw.ellipse((x - radius - 6, y - radius - 6, x + radius + 6, y + radius + 6), fill=glow)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def generate_motion_frames():
    frames = []
    card_box = (28, 16, WIDTH - 28, MOTION_HEIGHT - 16)
    stage_y = 212
    label_y = 316
    stage_x = [150, 272, 394, 516, 638]
    hub = (806, 212)
    split = (936, 212)
    human = (1168, 154)
    ai = (1168, 270)

    incoming_points = [(stage_x[0], stage_y), (stage_x[4], stage_y), (hub[0] - 82, stage_y)]
    human_points = [(hub[0] + 82, stage_y), split, human]
    ai_points = [(hub[0] + 82, stage_y), split, ai]

    labels = ["REQ", "DESIGN", "BUILD", "TEST", "OPS"]

    for frame_index in range(FRAMES):
        phase = frame_index / FRAMES
        canvas = make_canvas((WIDTH, MOTION_HEIGHT))
        add_card(canvas, card_box, radius=34)
        draw = ImageDraw.Draw(canvas)

        draw.line((96, stage_y, hub[0] - 82, stage_y), fill=(30, 30, 30, 180), width=4)
        draw.line((hub[0] + 82, stage_y, split[0], split[1]), fill=(30, 30, 30, 180), width=4)
        draw.line((split[0], split[1], human[0], human[1]), fill=(30, 30, 30, 180), width=4)
        draw.line((split[0], split[1], ai[0], ai[1]), fill=(30, 30, 30, 180), width=4)

        draw.line((96, 108, 1344, 108), fill=(10, 10, 10, 24), width=2)
        draw.text((96, 78), "SIGNAL FLOW THROUGH THE NEXUS HUB", font=font("IBMPlexMono-Regular.ttf", 18), fill=(96, 96, 96, 255))

        for idx, x in enumerate(stage_x):
            pulse_strength = max(0.0, sin((phase * 2 * pi) - idx * 0.65)) * 0.55
            draw_stage(draw, x, stage_y, labels[idx], label_y, pulse_strength)

        draw_stage(draw, human[0], human[1], "HUMAN", 120, 0.2)
        draw_stage(draw, ai[0], ai[1], "AI", 318, 0.2)
        draw_hub(draw, hub, phase)

        for offset in (0.00, 0.18, 0.36, 0.54):
            progress = (phase + offset) % 1.0
            pulse = point_on_polyline(incoming_points, progress)
            alpha = int(220 - offset * 160)
            draw_pulse(draw, pulse, 8, alpha)

        for path, offset in ((human_points, 0.08), (ai_points, 0.56)):
            progress = (phase + offset) % 1.0
            pulse = point_on_polyline(path, progress)
            draw_pulse(draw, pulse, 7, 210)

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
    save_gif(generate_motion_frames())


if __name__ == "__main__":
    main()
