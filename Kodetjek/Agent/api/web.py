"""
Kør fra Kodetjek-mappen:
    python -m Agent.api.web
"""
import re
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from Agent.api.build import build_agent
from Agent.domain.models import Decision, Step

PORT = 8000

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Code Check</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2em auto; padding: 0 1em; }
textarea { width: 100%; font: inherit; }
.step { color: #666; margin: .3em 0; }
.error { color: #b00; }
.answer { border: 1px solid #ddd; border-radius: 8px; padding: .5em 1.2em; margin-top: 1.5em; }
.answer li { margin: .3em 0; }
pre { white-space: pre-wrap; background: #f4f4f4; padding: 1em; }
</style></head><body>
<h1>Code Check</h1>
<form method="get" action="/">
<textarea name="q" rows="3" placeholder="Does our code solve US-001?">{question}</textarea>
<p><button>Check the code</button></p>
</form>
"""


# Hvad hvert værktøj hedder for en bruger, der ikke kender værktøjerne.
FRIENDLY = {
    "load_skill": lambda a: f"📘 Loading the {a.get('name', '')} rules",
    "search_requirements": lambda a: f"🔎 Looking up the test cases: {a.get('query', '')}",
    "search_specification": lambda a: f"📋 Looking up the business requirements: {a.get('query', '')}",
    "list_code_files": lambda a: "📂 Listing the project's files",
    "read_code_file": lambda a: f"📄 Reading {a.get('path', '').replace(chr(92), '/').split('/')[-1]}",
}


def render_step(decision: Decision, steps: list[Step]) -> str:
    """Ét skridt som én kort linje pr. handling, i et sprog brugeren forstår."""
    html = ""
    for step in steps:
        a, o = step.action, step.observation
        label = FRIENDLY.get(a.tool, lambda _: f"⚙️ {a.tool}")(a.arguments)
        css = "step error" if o.is_error else "step"
        html += f'<div class="{css}">{escape(label)}{" (failed)" if o.is_error else ""}</div>'
    return html


def render_markdown(text: str) -> str:
    """Den lille smule markdown, svaret bruger: fed, kode og punktlister."""
    def inline(line: str) -> str:
        line = escape(line)
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", line)

    html, in_list = "", False
    for line in text.splitlines():
        item = re.match(r"\s*[-*]\s+(.*)", line)
        if item and not in_list:
            html, in_list = html + "<ul>", True
        if not item and in_list:
            html, in_list = html + "</ul>", False
        if item:
            html += f"<li>{inline(item.group(1))}</li>"
        elif line.strip():
            html += f"<p>{inline(line.lstrip('# '))}</p>"
    return html + ("</ul>" if in_list else "")


def make_handler(agent):

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            # 11: SPØRGSMÅL: Browseren sender spørgsmålet som ?q=... i adressen.
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

            self.write("<h2>What I am doing</h2>")
            try:
                # 12: AGENTEN KØRER: Fortsæt i Agent/application/agent_service.py.
                # 18: VIS SKRIDT: on_step kaldes efter hvert skridt, og render_step() sender det til browseren med det samme.
                run = agent.run(question, on_step=lambda d, s: self.write(render_step(d, s)))

                # 20: OUTPUT: Svaret laves om fra markdown til HTML og sendes. Siden er færdig. SLUT.
                title = "" if run.finished else "<h2>Not finished</h2>"
                self.write(f'{title}<div class="answer">{render_markdown(run.answer)}</div>')
            except Exception as e:
                # Fejlen vises på siden, så demoen ikke bare hænger.
                self.write(f'<h2 class="error">Error</h2><pre>{escape(repr(e))}</pre>')
            self.write("</body></html>")

        def write(self, html: str) -> None:
            self.wfile.write(html.encode("utf-8"))
            self.wfile.flush()

    return Handler


def main():
    # 1: START: Her starter vi, når man kører "python -m Agent.api.web".
    # Agenten bygges én gang, så xlsx-filerne kun indlæses ved start. Fortsæt i Agent/api/build.py.
    agent = build_agent()

    # 10: VENT: Serveren er klar og venter på, at nogen stiller et spørgsmål på siden.
    # Hvert spørgsmål lander i Handler.do_GET() herover.
    server = ThreadingHTTPServer(("localhost", PORT), make_handler(agent))
    print(f"Code Check is running on http://localhost:{PORT} (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()
