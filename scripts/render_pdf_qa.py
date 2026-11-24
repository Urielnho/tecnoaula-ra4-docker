from pathlib import Path
import pymupdf

root = Path.cwd()
qa = root / "tmp" / "qa"
qa.mkdir(parents=True, exist_ok=True)
pdf = pymupdf.open(root / "output" / "pdf" / "RA4_TecnoAula_Docker.pdf")
for i, page in enumerate(pdf, 1):
    page.get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2)).save(qa / f"pdf-{i}.png")
print("PDF pages", len(pdf))
