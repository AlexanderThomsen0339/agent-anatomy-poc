"""Demo-websiden til Agent-laget: ét tekstfelt, én knap og skridtene live.

Kør fra Kodetjek-mappen:
    python -m Agent.api.web
    python -m Agent.api.web --fake
Åbn derefter http://localhost:8000

Hvorfor ingen JavaScript og ingen web-framework?
Det er en demo. Serveren skriver HTML-siden lidt ad gangen, mens agenten arbejder,
og browseren viser hvert stykke, så snart det kommer. Så ser man skridtene live
med kun Pythons standardbibliotek.
"""
import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from Agent.api.build import build_agent
from Agent.domain.models import Decision, Step

PORT = 8000

HEAD = """<!doctype html>
<html lang="da"><head><meta charset="utf-8"><title>Kodetjek</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2em auto; padding: 0 1em; }
textarea { width: 100%; font: inherit; }
.step { border-left: 3px solid #ccc; padding-left: .8em; margin: .8em 0; color: #555; }
.error { color: #b00; }
pre { white-space: pre-wrap; background: #f4f4f4; padding: 1em; }
</style></head><body>
<h1>Kodetjek</h1>
<form method="get" action="/">
<textarea name="q" rows="3">{question}</textarea>
<p><button>Tjek koden</button></p>
</form>
"""


def render_step(decision: Decision, steps: list[Step]) -> str:
    """Ét skridt som HTML: hvad agenten tænkte, gjorde og så."""
    html = '<div class="step">'
    if decision.text:
        html += f"<p><b>Tænker:</b> {escape(decision.text)}</p>"
    for step in steps:
        a, o = step.action, step.observation
        first_line = o.content.splitlines()[0] if o.content else ""
        css = ' class="error"' if o.is_error else ""
        html += f"<p><b>Gør:</b> {escape(a.tool)}({escape(str(a.arguments))})<br>"
        html += f"<b>Ser:</b> <span{css}>{escape(first_line)}</span></p>"
    return html + "</div>"


def make_handler(agent):

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            url = urlparse(self.path)
            if url.path != "/":
                self.send_error(404)
                return
            question = parse_qs(url.query).get("q", [""])[0].strip()

            # Hvorfor ingen Content-Length?
            # Siden er ikke færdig, når vi begynder at sende den. Browseren læser,
            # indtil serveren lukker forbindelsen, og viser undervejs det, der er kommet.
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.write(HEAD.replace("{question}", escape(question)))

            if not question:
                self.write("</body></html>")
                return

            self.write("<h2>Skridt</h2>")
            try:
                run = agent.run(question, on_step=lambda d, s: self.write(render_step(d, s)))
                title = "Svar" if run.finished else "Ikke færdig"
                self.write(f"<h2>{title}</h2><pre>{escape(run.answer)}</pre>")
                self.write(f"<p>({len(run.steps)} værktøjskald)</p>")
            except Exception as e:
                # Fejlen vises på siden, så demoen ikke bare hænger.
                self.write(f'<h2 class="error">Fejl</h2><pre>{escape(repr(e))}</pre>')
            self.write("</body></html>")

        def write(self, html: str) -> None:
            self.wfile.write(html.encode("utf-8"))
            self.wfile.flush()

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake", action="store_true", help="Brug den regelbaserede lærling, ingen API-nøgle")
    args = parser.parse_args()

    # Agenten bygges én gang, så xlsx-filerne kun indlæses ved start.
    agent = build_agent(args.fake)
    server = ThreadingHTTPServer(("localhost", PORT), make_handler(agent))
    print(f"Kodetjek kører på http://localhost:{PORT} (Ctrl+C stopper)")
    server.serve_forever()


if __name__ == "__main__":
    main()
