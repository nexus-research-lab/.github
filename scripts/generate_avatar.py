from pathlib import Path
from math import cos, sin, pi

from PIL import Image, ImageDraw, ImageFilter


SIZE = 1024
CENTER = SIZE // 2
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "nexus-avatar.png"


def hex_rgba(value: str, alpha: int = 255):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def add_glow(base: Image.Image, xy, radius, color, blur_radius):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(
        (xy[0] - radius, xy[1] - radius, xy[0] + radius, xy[1] + radius),
        fill=color,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(glow)


def draw_ring(draw: ImageDraw.ImageDraw, radius, width, color):
    box = (CENTER - radius, CENTER - radius, CENTER + radius, CENTER + radius)
    draw.ellipse(box, outline=color, width=width)


def draw_line(draw: ImageDraw.ImageDraw, a, b, width, fill):
    draw.line((a[0], a[1], b[0], b[1]), fill=fill, width=width)


def main():
    image = Image.new("RGBA", (SIZE, SIZE), hex_rgba("#0b1018"))
    draw = ImageDraw.Draw(image)

    vignette = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((72, 72, SIZE - 72, SIZE - 72), fill=hex_rgba("#16202f", 255))
    vignette = vignette.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(vignette)

    add_glow(image, (CENTER, CENTER), 210, hex_rgba("#1de1ff", 70), 90)
    add_glow(image, (CENTER, CENTER), 330, hex_rgba("#65a8ff", 24), 120)

    draw_ring(draw, 396, 6, hex_rgba("#273548", 255))
    draw_ring(draw, 308, 4, hex_rgba("#233040", 255))
    draw_ring(draw, 228, 3, hex_rgba("#2f4257", 255))

    hub_top = (CENTER, 280)
    hub_bottom = (CENTER, 744)
    left_mid = (CENTER - 176, CENTER)
    right_mid = (CENTER + 176, CENTER)

    draw_line(draw, hub_top, hub_bottom, 24, hex_rgba("#c7f3ff", 255))
    draw_line(draw, hub_top, left_mid, 18, hex_rgba("#69d8ff", 255))
    draw_line(draw, left_mid, hub_bottom, 18, hex_rgba("#69d8ff", 255))
    draw_line(draw, hub_top, right_mid, 6, hex_rgba("#2b3f53", 255))
    draw_line(draw, right_mid, hub_bottom, 6, hex_rgba("#2b3f53", 255))

    node_positions = [
        hub_top,
        hub_bottom,
        left_mid,
        right_mid,
        (CENTER - 250, 352),
        (CENTER + 252, 672),
        (CENTER + 246, 356),
        (CENTER - 248, 668),
    ]

    for x, y in node_positions:
        add_glow(image, (x, y), 24, hex_rgba("#22ebff", 88), 24)
        draw.ellipse((x - 17, y - 17, x + 17, y + 17), fill=hex_rgba("#d5fbff"))
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=hex_rgba("#22ebff"))

    orbit_points = []
    orbit_radius = 396
    for idx in range(10):
        angle = (-0.18 + idx / 10) * 2 * pi
        x = CENTER + orbit_radius * cos(angle)
        y = CENTER + orbit_radius * sin(angle)
        orbit_points.append((x, y))

    for idx, (x, y) in enumerate(orbit_points):
        r = 10 if idx % 3 else 14
        fill = hex_rgba("#8cb9d6", 230) if idx % 2 else hex_rgba("#f1fbff", 255)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    for a, b in ((0, 3), (2, 6), (5, 8)):
        draw_line(draw, orbit_points[a], orbit_points[b], 3, hex_rgba("#304459", 255))

    draw.rounded_rectangle(
        (CENTER - 108, CENTER - 108, CENTER + 108, CENTER + 108),
        radius=34,
        outline=hex_rgba("#d8fbff"),
        width=7,
    )
    draw.rounded_rectangle(
        (CENTER - 68, CENTER - 68, CENTER + 68, CENTER + 68),
        radius=24,
        fill=hex_rgba("#0f1723", 220),
        outline=hex_rgba("#50e8ff"),
        width=5,
    )

    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((42, 42, SIZE - 42, SIZE - 42), fill=255)

    final = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    final.alpha_composite(image)
    final.putalpha(mask)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    final.save(OUT)


if __name__ == "__main__":
    main()
