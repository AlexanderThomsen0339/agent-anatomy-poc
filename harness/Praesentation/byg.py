"""Bygger praesentation.html ud fra deck.json og slides/.

Hvorfor en byg-fil?
Præsentationen er lavet som én HTML-fil pr. slide (samme format som Slides-artefaktet).
Det gør den nem at rette slide for slide i git. Byg-filen samler dem til én side,
der kan åbnes direkte i en browser, med talenoterne under hvert slide.

Kør fra mappen AIPlatform/Praesentation:
    python byg.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Den viste rækkefølge kommer fra deck.json. Slides med "hidden" er backup og vises sidst med et mærke.
deck = json.loads((ROOT / "deck.json").read_text(encoding="utf-8"))
fonts = "&".join(
    face["href"].split("css2?", 1)[1].replace("&display=swap", "")
    for face in deck["faces"].values() if "href" in face
)

slides = []
for number, slide_id in enumerate(deck["order"], start=1):
    source = (ROOT / "slides" / f"{slide_id}.html").read_text(encoding="utf-8")
    backup = re.search(r"<section[^>]*\shidden[\s>]", source) is not None
    source = re.sub(r"(<section[^>]*?)\shidden(?=[\s>])", r"\1", source, count=1)
    # Talenoterne står i <aside>. De tages ud af sliden og vises under den.
    notes = re.search(r"<aside>(.*?)</aside>", source, re.S)
    source = re.sub(r"<aside>.*?</aside>", "", source, flags=re.S)
    label = f"Slide {number}" + (" · backup" if backup else "")
    notes_html = f'<p class="notes"><b>Talenoter:</b> {notes.group(1).strip()}</p>' if notes else ""
    slides.append(
        f'<div class="slide"><p class="label">{html.escape(label)}</p>'
        f'<div class="frame"><div class="canvas">{source}</div></div>{notes_html}</div>'
    )

page = f"""<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(deck["title"])}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<style>
  body {{ margin: 0; padding: 24px 16px 64px; background: #1E2E30; color: #F5F6F2; font-family: Inter, Arial, sans-serif; }}
  h1.title {{ max-width: 1200px; margin: 0 auto 24px; font-family: Rubik, Arial, sans-serif; }}
  .slide {{ max-width: 1200px; margin: 0 auto 48px; }}
  .label {{ margin: 0 0 8px; font-size: 14px; color: #C9DEDC; }}
  .notes {{ margin: 12px 0 0; font-size: 15px; line-height: 1.5; color: #C9DEDC; }}
  .frame {{ position: relative; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; border-radius: 8px; }}
  .canvas {{ position: absolute; top: 0; left: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
  .canvas section {{ position: relative; box-sizing: border-box; width: 1920px; height: 1080px; overflow: hidden; }}
  .canvas section * {{ box-sizing: border-box; margin: 0; }}
  .canvas ul {{ padding-left: 1.2em; }}
  .canvas table {{ border-collapse: collapse; width: 100%; }}
  .canvas th, .canvas td {{ padding: 0.35em 0.6em; text-align: left; border-bottom: 1px solid #D5E0DE; }}
  .canvas x-shape, .canvas x-icon {{ display: block; flex: none; }}
  .canvas x-shape[kind="ellipse"], .canvas x-icon {{ border-radius: 50%; }}
  .canvas x-icon {{ border: 4px solid currentColor; }}
  .canvas x-shape[kind="arrow-right"] {{ clip-path: polygon(0 30%, 60% 30%, 60% 0, 100% 50%, 60% 100%, 60% 70%, 0 70%); }}
  .canvas x-shape[kind="arrow-down"] {{ clip-path: polygon(30% 0, 70% 0, 70% 60%, 100% 60%, 50% 100%, 0 60%, 30% 60%); }}
</style>
</head>
<body>
<h1 class="title">{html.escape(deck["title"])}</h1>
{"".join(slides)}
<script>
  // Skalerer hvert 1920x1080-slide ned til bredden af siden.
  function fit() {{
    document.querySelectorAll(".frame").forEach(function (frame) {{
      frame.firstElementChild.style.transform = "scale(" + frame.clientWidth / 1920 + ")";
    }});
  }}
  window.addEventListener("resize", fit);
  fit();
</script>
</body>
</html>
"""

(ROOT / "praesentation.html").write_text(page, encoding="utf-8")
print(f"praesentation.html bygget med {len(slides)} slides")
