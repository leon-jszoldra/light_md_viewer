"""
Generates md-viewer.ico — a clean Material Design icon for MD Viewer.
Run once: python generate_icon.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, "md-viewer.ico")


def draw_icon(size):
    """Draw a single icon at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Proportional sizing
    margin = max(1, size // 16)
    radius = max(2, size // 8)

    # Background: rounded rectangle in Material blue
    draw.rounded_rectangle(
        [margin, margin, size - margin - 1, size - margin - 1],
        radius=radius,
        fill=(25, 118, 210, 255),  # #1976d2
    )

    # Draw "MD" text in white, centered
    # Try to find a good bold font, fall back to default
    font = None
    font_size = int(size * 0.38)
    for font_name in [
        "arialbd.ttf",   # Windows
        "Arial Bold.ttf",
        "DejaVuSans-Bold.ttf",  # Linux
        "arial.ttf",
        "DejaVuSans.ttf",
    ]:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except (OSError, IOError):
            continue

    if font is None:
        font = ImageFont.load_default()

    text = "MD"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # Subtle down-arrow in bottom-right to hint at "document"
    if size >= 32:
        ax = int(size * 0.78)
        ay = int(size * 0.72)
        arrow_size = max(3, size // 10)
        draw.polygon(
            [
                (ax, ay),
                (ax + arrow_size, ay),
                (ax + arrow_size // 2, ay + arrow_size),
            ],
            fill=(255, 255, 255, 180),
        )

    return img


def main():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [draw_icon(s) for s in sizes]

    # Save as .ico with multiple sizes
    # Pillow's ICO save needs the largest image first with append_images for the rest
    images[-1].save(
        OUT,
        format="ICO",
        append_images=images[:-1],
    )
    print(f"Icon saved to: {OUT}")


if __name__ == "__main__":
    main()
