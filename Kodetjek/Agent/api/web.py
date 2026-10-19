"""
Kør fra Kodetjek-mappen:
    python -m Agent.api.web
"""
import re
from html import escape
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import settings
from Agent.api.build import build_agent, build_writer
from Agent.application.answer_writer import parse_assessment
from Agent.domain.models import Assessment, Decision, Step

PORT = 8000

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Code Check</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2em auto; padding: 0 1em; }
textarea { width: 100%; font: inherit; }
select { font: inherit; }
.step { color: #666; margin: .3em 0; }
.error { color: #b00; }
.answer { border: 1px solid #ddd; border-radius: 8px; padding: .5em 1.2em; margin-top: 1.5em; }
.answer li { margin: .3em 0; }
.sources { color: #888; font-size: .8em; margin-top: 1.5em; }
.sources summary { cursor: pointer; }
.sources code { word-break: break-all; }
.sources td { padding: .2em .5em; vertical-align: top; }
pre { white-space: pre-wrap; background: #f4f4f4; padding: 1em; }
</style></head><body>
<h1>Code Check</h1>
<form method="get" action="/">
<p><label>I am: <select name="role">{roles}</select></label></p>
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


def code_repo(folder: Path) -> str:
    """Repoets adresse fra .git/config i kodemappen, hvis der er en."""
    config = folder / ".git" / "config"
    if config.exists():
        match = re.search(r"url\s*=\s*(\S+)", config.read_text(encoding="utf-8", errors="ignore"))
        if match:
            return match.group(1)
    return ""


def render_sources(steps: list[Step]) -> str:
    """En lille, lukket boks med de dokumenter og den kode, agenten faktisk har brugt."""
    # Hvorfor ud fra skridtene og ikke fra svaret?
    # Skridtene er det, værktøjerne faktisk returnerede. Svaret er skrevet af AI'en og kan tage fejl.
    test_files, spec_files, code_files = set(), set(), []
    for step in steps:
        a, o = step.action, step.observation
        if o.is_error:
            continue
        # Hvert søgeresultat starter med [fil › ark] eller [fil].
        sources = {s.split(" › ")[0] for s in re.findall(r"^\[(.+?)\]", o.content, re.MULTILINE)}
        if a.tool == "search_requirements":
            test_files |= sources
        elif a.tool == "search_specification":
            spec_files |= sources
        elif a.tool == "read_code_file" and a.arguments.get("path") not in code_files:
            code_files.append(a.arguments.get("path", ""))

    def rows(label: str, folder: Path, files) -> str:
        items = "".join(f"<li><code>{escape(str(folder / f))}</code></li>" for f in sorted(files))
        return f"<p>{label}</p><ul>{items}</ul>" if items else ""

    repo = code_repo(Path(settings.CODE_FOLDER))
    code = f"<p>Code: <code>{escape(str(settings.CODE_FOLDER))}</code>"
    code += f" (repo <code>{escape(repo)}</code>)</p>" if repo else "</p>"
    return (
        '<details class="sources"><summary>Sources</summary>'
        + rows("Test cases:", Path(settings.DATA_FOLDER), test_files)
        + rows("Business requirements:", Path(settings.SPEC_FOLDER), spec_files)
        + code
        + "".join(f"<li><code>{escape(f)}</code></li>" for f in code_files).join(("<ul>", "</ul>"))
        + "</details>"
    )


def render_assessment(assessment: Assessment) -> str:
    """Vurderingen, som begge roller bygger på, i en lukket boks under kilderne."""
    icons = {"MET": "✅", "NOT_MET": "❌", "CANT_TELL": "❓", "RISK": "⚠️"}
    rows = "".join(
        f"<tr><td>{icons[f.status]}</td><td>{escape(f.ids)}</td><td>{escape(f.requirement)}</td>"
        f"<td>{escape(f.code)}</td><td><code>{escape(f.where)}</code></td></tr>"
        for f in assessment.findings
    )
    return f'<details class="sources"><summary>Assessment</summary><table>{rows}</table></details>'


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


def make_handler(agent, writer):

    # Hvorfor gemme vurderingen?
    # Skifter man rolle på samme spørgsmål, skal svaret bygge på den samme vurdering.
    # Ellers vurderer AI'en koden forfra og kan komme frem til noget andet.
    # Den ligger kun i hukommelsen, så en genstart af serveren laver en ny.
    checked: dict[str, tuple] = {}

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            # 11: SPØRGSMÅL: Browseren sender spørgsmålet som ?q=... i adressen.
            url = urlparse(self.path)
            if url.path != "/":
                self.send_error(404)
                return
            query = parse_qs(url.query)
            question = query.get("q", [""])[0].strip()
            # Rollen kommer fra dropdownen. Den står i adressen, så den er valgt igen ved næste spørgsmål.
            role = query.get("role", [settings.DEFAULT_ROLE])[0]
            if role not in settings.ROLES:
                role = settings.DEFAULT_ROLE

            # Hvorfor ingen Content-Length?
            # Siden er ikke færdig, når vi begynder at sende den. Browseren læser,
            # indtil serveren lukker forbindelsen, og viser undervejs det, der er kommet.
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            roles = "".join(
                f'<option value="{key}"{" selected" if key == role else ""}>{escape(label)}</option>'
                for key, label in settings.ROLES.items()
            )
            self.write(HEAD.replace("{roles}", roles).replace("{question}", escape(question)))

            if not question:
                self.write("</body></html>")
                return

            try:
                if question in checked:
                    run, assessment = checked[question]
                    self.write('<p class="step">♻️ Using the check already made for this question</p>')
                else:
                    self.write("<h2>What I am doing</h2>")
                    # 12: AGENTEN KØRER: Fortsæt i Agent/application/agent_service.py.
                    # 18: VIS SKRIDT: on_step kaldes efter hvert skridt, og render_step() sender det til browseren med det samme.
                    # Agenten får ikke rollen. Vurderingen skal være den samme, uanset hvem der spørger.
                    run = agent.run(question, on_step=lambda d, s: self.write(render_step(d, s)))
                    assessment = parse_assessment(run.answer) if run.finished else None
                    if assessment:
                        checked[question] = (run, assessment)

                if not assessment:
                    # Agenten blev ikke færdig eller skrev ikke en vurdering. Vis det, den skrev.
                    self.write(f'<h2>Not finished</h2>{render_sources(run.steps)}<div class="answer">{render_markdown(run.answer)}</div>')
                else:
                    # 20: OUTPUT: Vurderingen skrives om til et svar til rollen, laves om fra markdown til HTML og sendes. SLUT.
                    # Kilderne og vurderingen står øverst i lukkede bokse, så de ikke fylder, men kan foldes ud.
                    self.write('<p class="step">✍️ Writing the answer</p>')
                    answer = writer.write(question, assessment, role)
                    others = " · ".join(
                        f'<a href="/?{escape(urlencode({"q": question, "role": key}))}">{escape(label)}</a>'
                        for key, label in settings.ROLES.items() if key != role
                    )
                    self.write(
                        render_sources(run.steps) + render_assessment(assessment)
                        + f'<div class="answer">{render_markdown(answer)}</div>'
                        + f'<p class="step">Show the answer for: {others}</p>'
                    )
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
    writer = build_writer()

    # 10: VENT: Serveren er klar og venter på, at nogen stiller et spørgsmål på siden.
    # Hvert spørgsmål lander i Handler.do_GET() herover.
    server = ThreadingHTTPServer(("localhost", PORT), make_handler(agent, writer))
    print(f"Code Check is running on http://localhost:{PORT} (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()
