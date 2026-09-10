"""Generate the email-safe animated version of the Webbitti brand mark."""
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 288
SCALE = 3
FRAMES = 30
OUTPUT = Path(__file__).parents[1] / "img" / "webbitti-mark-email.gif"


def point(cx, cy, radius, angle):
    radians = angle * pi / 180
    return cx + radius * cos(radians), cy + radius * sin(radians)


def dashed_circle(draw, box, start, dash, gap, color, width):
    angle = start
    while angle < start + 360:
        draw.arc(box, angle, min(angle + dash, start + 360), fill=color, width=width)
        angle += dash + gap


frames = []
for index in range(FRAMES):
    image = Image.new("RGB", (SIZE, SIZE), "#0b0d10")
    draw = ImageDraw.Draw(image)
    phase = index * 360 / FRAMES

    for radius, color, width, dash, gap, direction in (
        (111, "#c8ff65", 5, 66, 34, 1),
        (78, "#71e4ff", 4, 21, 16, -1),
    ):
        box = (SIZE // 2 - radius, SIZE // 2 - radius, SIZE // 2 + radius, SIZE // 2 + radius)
        dashed_circle(draw, box, phase * direction, dash, gap, color, width)

    w_points = [(76, 101), (101, 190), (144, 131), (187, 190), (212, 101)]
    draw.line(w_points, fill="#c8ff65", width=15, joint="curve")

    sparkle_angle = phase * 1.4
    sx, sy = point(144, 144, 100, sparkle_angle)
    pulse = 8 + int(3 * (1 + sin(index * 2 * pi / 10)))
    draw.ellipse((sx - pulse, sy - pulse, sx + pulse, sy + pulse), fill="#f4fff0")

    image = image.resize((SIZE // SCALE, SIZE // SCALE), Image.Resampling.LANCZOS)
    frames.append(image.quantize(colors=128, method=Image.Quantize.MEDIANCUT))

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=70,
    loop=0,
    optimize=True,
    disposal=2,
)
print(OUTPUT)
