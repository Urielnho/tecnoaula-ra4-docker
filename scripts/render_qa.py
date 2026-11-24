from pathlib import Path
import base64
from playwright.sync_api import sync_playwright

root = Path.cwd()
deps = root.parent / "Unidad 4 - Práctica 1 Instalación y Primeros Pasos con Docker" / "tmp" / "portada" / "preview" / "node_modules"
docx = root / "output" / "word" / "RA4_TecnoAula_Docker.docx"
qa = root / "tmp" / "qa"
qa.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1000, "height": 1100}, device_scale_factor=1)
    page.set_content('<html><body style="margin:0"><div id="document"></div></body></html>')
    page.add_script_tag(path=str(deps / "jszip" / "dist" / "jszip.min.js"))
    page.add_script_tag(path=str(deps / "docx-preview" / "dist" / "docx-preview.min.js"))
    data = base64.b64encode(docx.read_bytes()).decode()
    page.evaluate("""async data => {
      const bytes = Uint8Array.from(atob(data), c => c.charCodeAt(0));
      await docx.renderAsync(bytes.buffer, document.getElementById('document'), null,
        {ignoreWidth:false, ignoreHeight:false, breakPages:true, ignoreLastRenderedPageBreak:false});
    }""", data)
    pages = page.locator("section.docx")
    for i, element in enumerate(pages.all(), 1):
        element.screenshot(path=str(qa / f"docx-{i}.png"))
    print("DOCX pages", pages.count())
    browser.close()

