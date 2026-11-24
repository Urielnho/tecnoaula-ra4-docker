from pathlib import Path
from PIL import Image, ImageDraw

root = Path.cwd() / "tmp" / "qa"
for prefix in ["docx", "pdf"]:
    files = [p for p in root.glob(f"{prefix}-*.png") if p.stem.split("-")[-1].isdigit()]
    files = sorted(files, key=lambda p: int(p.stem.split("-")[-1]))
    thumbs = []
    for file in files:
        image = Image.open(file).convert("RGB")
        image.thumbnail((300, 390))
        canvas = Image.new("RGB", (320, 430), "white")
        canvas.paste(image, ((320 - image.width) // 2, 25))
        ImageDraw.Draw(canvas).text((12, 7), file.stem, fill="black")
        thumbs.append(canvas)
    sheet = Image.new("RGB", (640, 430 * ((len(thumbs) + 1) // 2)), "#dddddd")
    for i, image in enumerate(thumbs):
        sheet.paste(image, ((i % 2) * 320, (i // 2) * 430))
    sheet.save(root / f"{prefix}-contact.png")
