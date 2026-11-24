from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import io
import json
import posixpath

from lxml import etree as E
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn as docx_qn
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


ROOT = Path.cwd()
CAP = ROOT / "capturas"
TMP = ROOT / "tmp"
WORD_OUT = ROOT / "output" / "word" / "RA4_TecnoAula_Docker.docx"
PDF_OUT = ROOT / "output" / "pdf" / "RA4_TecnoAula_Docker.pdf"
COVER = Path(r"C:/Users/uriel/Downloads/portada ejemplo.docx")
REPO = "https://github.com/Urielnho/tecnoaula-ra4-docker"
TMP.mkdir(parents=True, exist_ok=True)
WORD_OUT.parent.mkdir(parents=True, exist_ok=True)
PDF_OUT.parent.mkdir(parents=True, exist_ok=True)

EVIDENCE = [
    ("Registro del usuario", "04_registro.png",
     "Registré una cuenta de prueba desde el formulario real de TecnoAula. El usuario incluye nombre, correo y matrícula."),
    ("Frontend autenticado", "02_frontend.png",
     "Inicié sesión en http://localhost:5173. El panel muestra el correo persistencia.ra4@tecnoaula.local y la matrícula RA4-20261123."),
    ("Documentación de la API", "03_swagger.png",
     "Abrí Swagger en http://localhost:8000/swagger/. Se muestran los endpoints de autenticación, usuarios, productos, categorías e integraciones."),
    ("Usuario después del reinicio", "07_usuario_despues.png",
     "Después de ejecutar docker compose down y docker compose up -d --wait, la misma cuenta continuó disponible con sus datos originales."),
]

STATUS = (
    "tecnoaula-ra4-backend-1    Up (healthy)    127.0.0.1:8000->8000/tcp\n"
    "tecnoaula-ra4-db-1         Up (healthy)    3306/tcp, 33060/tcp\n"
    "tecnoaula-ra4-frontend-1   Up (healthy)    127.0.0.1:5173->5173/tcp"
)
BEFORE = '{"motor": "mysql", "id": 1, "email": "persistencia.ra4@tecnoaula.local", "matricula": "RA4-20261123", "activo": true}'


def set_font(run, bold=False, italic=False, size=14, name="Arial"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(docx_qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(docx_qn("w:hAnsi"), name)


def add_link(paragraph, text, url):
    part = paragraph.part
    rid = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(docx_qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(docx_qn("w:val"), "0563C1")
    underline = OxmlElement("w:u")
    underline.set(docx_qn("w:val"), "single")
    rfonts = OxmlElement("w:rFonts")
    rfonts.set(docx_qn("w:ascii"), "Arial")
    rfonts.set(docx_qn("w:hAnsi"), "Arial")
    size = OxmlElement("w:sz")
    size.set(docx_qn("w:val"), "28")
    rpr.extend([rfonts, color, underline, size])
    run.append(rpr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def build_body():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Inches(0.7)
    for style in doc.styles:
        if style.type in (1, 2):
            style.font.name = "Arial"
            style.font.size = Pt(14)
            style.font.color.rgb = RGBColor(0, 0, 0)
    for name in ["Title", "Heading 1", "Heading 2"]:
        doc.styles[name].font.name = "Arial"
        doc.styles[name].font.size = Pt(14)
        doc.styles[name].font.bold = True
        doc.styles[name].font.color.rgb = RGBColor(0, 0, 0)
    for border in list(doc.styles.element.iter(docx_qn("w:pBdr"))):
        border.getparent().remove(border)
    doc.styles["Normal"].paragraph_format.space_after = Pt(10)

    title = doc.add_paragraph("Resultado de Aprendizaje Unidad 4", "Title")
    title.paragraph_format.page_break_before = True
    doc.add_paragraph(
        "En esta actividad integré React, Django y MySQL en un solo proyecto con Docker Compose. "
        "Los tres servicios funcionan, el frontend consume la API y los datos permanecen en un volumen de MySQL."
    )
    p = doc.add_paragraph()
    set_font(p.add_run("Repositorio: "), bold=True)
    add_link(p, REPO, REPO)
    doc.add_paragraph("Contenedores comprobados con docker compose ps:")
    p = doc.add_paragraph()
    run = p.add_run(STATUS)
    set_font(run, size=11, name="Courier New")
    p.paragraph_format.space_after = Pt(8)

    for heading, filename, caption in EVIDENCE:
        p = doc.add_paragraph(heading, "Heading 1")
        p.paragraph_format.page_break_before = True
        pic = doc.add_paragraph()
        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.keep_with_next = True
        with Image.open(CAP / filename) as im:
            w, h = im.size
        scale = min(510 / w, 465 / h)
        pic.add_run().add_picture(str(CAP / filename), width=Pt(w * scale), height=Pt(h * scale))
        doc.add_paragraph(caption)

    p = doc.add_paragraph("Prueba de persistencia", "Heading 1")
    p.paragraph_format.page_break_before = True
    doc.add_paragraph("Antes de reiniciar los contenedores, la consulta directa al modelo de Django devolvió:")
    p = doc.add_paragraph()
    set_font(p.add_run(BEFORE), size=10, name="Courier New")
    doc.add_paragraph("Ejecuté docker compose down sin la opción -v y después docker compose up -d --wait. La consulta posterior devolvió exactamente el mismo motor, id, correo, matrícula y estado activo.")
    doc.add_paragraph("Esto confirma que el volumen mysql_data conservó la información aunque los contenedores fueron eliminados y creados otra vez.")

    p = doc.add_paragraph("Conclusión", "Heading 1")
    p.paragraph_format.page_break_before = True
    doc.add_paragraph(
        "Docker Compose permite ejecutar el frontend, el backend y la base de datos con una sola configuración. "
        "La red interna permite que Django se conecte a MySQL por el nombre db y el volumen evita perder la información."
    )
    doc.add_paragraph(
        "En comparación con instalar cada servicio por separado, Docker facilita repetir el entorno en otra computadora, "
        "mantener las dependencias aisladas y levantar todo el sistema con un solo comando."
    )
    doc.core_properties.author = "Uriel Ochoa Mora"
    doc.core_properties.title = "Resultado de Aprendizaje Unidad 4 TecnoAula con Docker"
    body_path = TMP / "cuerpo.docx"
    doc.save(body_path)
    return body_path


def merge_cover(body_path):
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    }
    qn = lambda p, n: "{" + ns[p] + "}" + n
    with ZipFile(COVER) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    cover = E.fromstring(parts["word/document.xml"])
    paragraphs = cover.find(qn("w", "body")).findall(qn("w", "p"))
    texts = paragraphs[5].findall(".//" + qn("w", "t"))
    texts[0].text = "Resultado de Aprendizaje Unidad 4: "
    texts[1].text = "Proyecto orquestado"
    texts[2].text = " con Docker Compose"
    for node in cover.findall(".//" + qn("w", "t")):
        if node.text == "29/10/2026":
            node.text = "23/11/2026"
    xml = lambda e: E.tostring(e, encoding="UTF-8", xml_declaration=True, standalone=True)
    with ZipFile(body_path) as z:
        body_parts = {n: z.read(n) for n in z.namelist()}
    body = E.fromstring(body_parts["word/document.xml"]).find(qn("w", "body"))
    cover_body = cover.find(qn("w", "body"))
    cover_section = cover_body.find(qn("w", "sectPr"))
    cover_body.remove(cover_section)
    break_p = E.SubElement(cover_body, qn("w", "p"))
    pp = E.SubElement(break_p, qn("w", "pPr"))
    section = deepcopy(cover_section)
    kind = section.find(qn("w", "type")) or E.SubElement(section, qn("w", "type"))
    kind.set(qn("w", "val"), "nextPage")
    pp.append(section)
    styles = E.fromstring(parts["word/styles.xml"])
    body_styles = E.fromstring(body_parts["word/styles.xml"])
    style_map = {s.get(qn("w", "styleId")): "RA4" + s.get(qn("w", "styleId")) for s in body_styles.findall(qn("w", "style"))}
    for s in body_styles.findall(qn("w", "style")):
        s = deepcopy(s)
        old_id = s.get(qn("w", "styleId"))
        s.set(qn("w", "styleId"), style_map[old_id])
        s.attrib.pop(qn("w", "default"), None)
        for tag in ["basedOn", "next", "link"]:
            for node in s.findall(qn("w", tag)):
                old = node.get(qn("w", "val"))
                if old in style_map:
                    node.set(qn("w", "val"), style_map[old])
        styles.append(s)
    rels = E.fromstring(parts["word/_rels/document.xml.rels"])
    body_rels = E.fromstring(body_parts["word/_rels/document.xml.rels"])
    rel_map = {}
    for rel in body_rels:
        if rel.get("Type").endswith("/image") or rel.get("Type").endswith("/hyperlink"):
            old = rel.get("Id")
            new = "RA4" + old
            rel_map[old] = new
            rel = deepcopy(rel)
            rel.set("Id", new)
            if rel.get("Type").endswith("/image"):
                old_part = posixpath.normpath(posixpath.join("word", rel.get("Target")))
                new_part = "word/media/ra4_" + posixpath.basename(old_part)
                parts[new_part] = body_parts[old_part]
                rel.set("Target", "media/" + posixpath.basename(new_part))
            rels.append(rel)
    max_id = max([int(e.get("id", "0")) for e in cover.findall(".//" + qn("wp", "docPr"))] + [0])
    first = True
    for item in body:
        if item.tag == qn("w", "sectPr"):
            continue
        item = deepcopy(item)
        paragraphs_in_item = ([item] if item.tag == qn("w", "p") else []) + item.findall(".//" + qn("w", "p"))
        for paragraph in paragraphs_in_item:
            ppr = paragraph.find(qn("w", "pPr"))
            if ppr is None:
                ppr = E.Element(qn("w", "pPr"))
                paragraph.insert(0, ppr)
            style = ppr.find(qn("w", "pStyle"))
            if style is None:
                style = E.Element(qn("w", "pStyle"))
                ppr.insert(0, style)
                style.set(qn("w", "val"), "RA4Normal")
            else:
                style.set(qn("w", "val"), style_map.get(style.get(qn("w", "val")), style.get(qn("w", "val"))))
            if first:
                E.SubElement(ppr, qn("w", "pageBreakBefore"))
                first = False
        for node in item.iter():
            for key, value in list(node.attrib.items()):
                if key.startswith("{" + ns["r"] + "}") and value in rel_map:
                    node.set(key, rel_map[value])
            if node.tag == qn("wp", "docPr"):
                max_id += 1
                node.set("id", str(max_id))
        cover_body.append(item)
    cover_body.append(deepcopy(body.find(qn("w", "sectPr"))))
    parts["word/document.xml"] = xml(cover)
    parts["word/styles.xml"] = xml(styles)
    parts["word/_rels/document.xml.rels"] = xml(rels)
    with ZipFile(WORD_OUT, "w", ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    assert hashlib.sha256(COVER.read_bytes()).hexdigest() == "ee517ef6b14adfd8bdfc3f852ddcb670cd61da03d30a823760c55b482224c803"


def build_pdf():
    fonts = Path(r"C:/Windows/Fonts")
    for name, filename in [("Arial", "arial.ttf"), ("ArialBold", "arialbd.ttf"), ("ArialItalic", "ariali.ttf"), ("CourierNew", "cour.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    c = canvas.Canvas(str(PDF_OUT), pagesize=(612, 792))
    c.setTitle("Resultado de Aprendizaje Unidad 4 TecnoAula con Docker")
    c.setAuthor("Uriel Ochoa Mora")
    body = ParagraphStyle("Body", fontName="Arial", fontSize=14, leading=20, spaceAfter=12)
    heading = ParagraphStyle("Heading", parent=body, fontName="ArialBold", spaceAfter=14)
    center = ParagraphStyle("Center", parent=body, alignment=TA_CENTER)
    mono = ParagraphStyle("Mono", fontName="CourierNew", fontSize=9.5, leading=14, spaceAfter=10)

    def para(text, x, y, width, style=body):
        p = Paragraph(text, style)
        _, h = p.wrap(width, 720)
        p.drawOn(c, x, y - h)
        return y - h - 12

    with ZipFile(COVER) as z:
        for filename, x, top, w, h in [("image1.png", 25, 5, 214, 90), ("image2.png", 396, 10, 211, 67), ("image3.png", 427, 85, 156, 93)]:
            c.drawImage(ImageReader(io.BytesIO(z.read("word/media/" + filename))), x, 792 - top - h, w, h, mask="auto")
    y = 605
    y = para("Resultado de Aprendizaje Unidad 4<br/>Proyecto orquestado con Docker Compose", 50, y, 512, ParagraphStyle("Cover", parent=center, fontName="ArialBold", fontSize=16, leading=23))
    y = para("Universidad Tecnológica de San Luis Río Colorado", 50, y - 24, 512, center)
    y = para("Carrera Ingeniería en Desarrollo y Gestión de Software", 50, y - 22, 512, ParagraphStyle("Career", parent=center, fontName="ArialItalic"))
    y = para("IDGS-9-1", 50, y, 512, center)
    y = para("Alumno", 50, y - 4, 512, center)
    para("Uriel Ochoa Mora", 50, y, 512, center)
    c.setFont("Arial", 12)
    c.drawString(50, 76, "San Luis Río Colorado, Sonora")
    c.drawRightString(562, 76, "23/11/2026")
    c.showPage()

    y = para("Resultado de Aprendizaje Unidad 4", 50, 742, 512, heading)
    y = para("Integré React, Django y MySQL en un proyecto con Docker Compose. Los tres servicios funcionan y los datos permanecen en un volumen de MySQL.", 50, y, 512)
    y = para(f'Repositorio: <link href="{REPO}" color="#0563C1">{REPO}</link>', 50, y, 512)
    y = para("Resultado de docker compose ps", 50, y - 4, 512, heading)
    y = para(STATUS.replace("\n", "<br/>"), 50, y, 512, mono)
    para("Los servicios backend, db y frontend quedaron en estado healthy.", 50, y, 512)
    c.showPage()

    for title, filename, caption in EVIDENCE:
        y = para(title, 50, 742, 512, heading)
        path = CAP / filename
        with Image.open(path) as im:
            iw, ih = im.size
        scale = min(512 / iw, 470 / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(str(path), 50 + (512 - w) / 2, y - h, w, h)
        y -= h + 16
        para(caption, 50, y, 512)
        c.showPage()

    y = para("Prueba de persistencia", 50, 742, 512, heading)
    y = para("Antes del reinicio", 50, y, 512, heading)
    y = para(BEFORE, 50, y, 512, mono)
    y = para("Comandos ejecutados", 50, y - 4, 512, heading)
    y = para("docker compose down<br/>docker compose up -d --wait", 50, y, 512, mono)
    y = para("Después del reinicio", 50, y - 4, 512, heading)
    y = para(BEFORE, 50, y, 512, mono)
    para("El mismo id, correo, matrícula y estado activo confirman que mysql_data conservó el registro.", 50, y, 512)
    c.showPage()

    y = para("Conclusión", 50, 742, 512, heading)
    y = para("Docker Compose permite ejecutar el frontend, el backend y la base de datos con una sola configuración. La red interna conecta Django con MySQL y el volumen evita perder la información.", 50, y, 512)
    para("Frente a instalar cada servicio por separado, Docker facilita repetir el entorno, aislar dependencias y levantar todo el sistema con un solo comando.", 50, y, 512)
    c.save()


if __name__ == "__main__":
    body_path = build_body()
    merge_cover(body_path)
    build_pdf()
    print(json.dumps({"word": str(WORD_OUT), "pdf": str(PDF_OUT)}, ensure_ascii=False))
