"""
Start siden:
    python web.py
"""
import hashlib
import json
import re
from html import escape
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import settings
from agent import CHAT, DOCS, Action, AgentRun, Assessment, Step, parse_assessment
from build import build_agents, build_checkout_service, build_router, build_writer
from tools import Checkout

PORT = 8000

HEAD = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Platform POC</title>
<style>
/* Aalborg Forsynings farver (brand colours). Mørk tilstand følger styresystemet. */
:root {
  --primary: #005b63; --primary-dark: #00464d; --primary-light: #e6f1f1;
  --secondary: #72b5a3; --secondary-light: #edf6f3;
  --accent: #e66f45; --accent-dark: #d45c36;
  --bg: #f7f9f8; --surface: #ffffff; --text: #17383b; --muted: #5b6f71; --border: #d8e3e1;
  --hero: #005b63; --hero-text: #ffffff; --heading: #005b63; --user: #e6f1f1;
  --highlight: rgba(0, 91, 99, 0.06); --code-bg: #e6f1f1; --error: #c62828; --edge: #005b63;
  --ok: #1e7d4f; --ok-bg: #e3f4ea; --part: #9a5a00; --part-bg: #fdf0dc; --bad: #b3261e; --bad-bg: #fbe5e3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17383b; --surface: #1d4448; --text: #ffffff; --muted: #b9cbc9; --border: rgba(114, 181, 163, 0.30);
    --hero: #00464d; --heading: #72b5a3; --user: #245358;
    --highlight: rgba(114, 181, 163, 0.10); --code-bg: rgba(114, 181, 163, 0.20); --error: #ff8a80; --edge: #72b5a3;
    --ok: #8fe0b4; --ok-bg: rgba(143, 224, 180, 0.15); --part: #ffcf7d; --part-bg: rgba(255, 207, 125, 0.15);
    --bad: #ffaaa3; --bad-bg: rgba(255, 170, 163, 0.15);
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 16px/1.55 "Segoe UI", system-ui, sans-serif; }
header { background: var(--hero); color: var(--hero-text); padding: 1em 16px; }
.bar { max-width: 860px; margin: 0 auto; display: flex; flex-wrap: wrap; align-items: center; gap: .6em 1.2em; }
.bar .title { flex: 1 1 auto; }
header h1 { margin: 0; font-size: 1.35em; font-weight: 600; }
header p { margin: 0; opacity: .85; font-size: .9em; }
header form { margin: 0; }
header label { font-size: .9em; }
header select { font: inherit; font-size: .9em; color: var(--text); background: var(--surface); border: 0; border-radius: 6px; padding: .35em .5em; margin-left: .3em; }
header a { color: var(--hero-text); font-size: .9em; text-decoration: none; border: 1px solid rgba(255,255,255,.5); border-radius: 6px; padding: .3em .7em; }
header a:hover { background: rgba(255,255,255,.12); }
main { max-width: 860px; margin: 0 auto; padding: 1.2em 16px 3em; }
.welcome { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.1em 1.3em; margin-bottom: 1em; }
.welcome h2 { margin: 0 0 .3em; color: var(--heading); font-size: 1.1em; }
.welcome p { margin: 0 0 .8em; color: var(--muted); }
.chips { display: flex; flex-wrap: wrap; gap: .5em; }
.chip { font: inherit; font-size: .9em; color: var(--heading); background: var(--highlight); border: 1px solid var(--border); border-radius: 999px; padding: .35em .9em; cursor: pointer; }
.chip:hover { border-color: var(--secondary); }
.chips.reply { margin: .5em 0 0; }
.msg { margin: .9em 0; }
.msg .who { font-size: .8em; color: var(--muted); margin: 0 0 .2em; }
.msg.user { display: flex; flex-direction: column; align-items: flex-end; }
.msg.user .bubble { background: var(--user); border-radius: 14px 14px 4px 14px; padding: .55em 1em; max-width: 85%; white-space: pre-wrap; overflow-wrap: anywhere; }
.msg.agent .bubble { background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--edge); border-radius: 4px 14px 14px 14px; padding: .5em 1.2em; overflow-wrap: anywhere; }
.msg.agent.asks .bubble { border-left-color: var(--accent); }
.bubble p { margin: .5em 0; }
.bubble ul { padding-left: 1.2em; margin: .4em 0; }
.bubble li { margin: .35em 0; }
code { background: var(--code-bg); border-radius: 4px; padding: .05em .35em; font-size: .9em; overflow-wrap: anywhere; }
.verdict { display: inline-block; font-weight: 600; border-radius: 999px; padding: .2em .8em; margin: .6em 0 .2em; }
.verdict.ok { color: var(--ok); background: var(--ok-bg); }
.verdict.part { color: var(--part); background: var(--part-bg); }
.verdict.bad { color: var(--bad); background: var(--bad-bg); }
.count { color: var(--muted); margin-left: .4em; }
details { margin: .5em 0; }
summary { cursor: pointer; font-weight: 600; color: var(--heading); font-size: .9em; }
.work { background: var(--highlight); border-radius: 8px; padding: .5em .9em; }
.step { color: var(--muted); margin: .3em 0; font-size: .92em; }
.step ul { margin: .2em 0; padding-left: 1.3em; }
.error { color: var(--error); }
.busy { color: var(--muted); font-size: .92em; }
.busy::before { content: ""; display: inline-block; width: .8em; height: .8em; margin-right: .5em; border: 2px solid var(--secondary); border-top-color: transparent; border-radius: 50%; animation: spin .8s linear infinite; vertical-align: -1px; }
@keyframes spin { to { transform: rotate(360deg); } }
.step a, .sources a { color: var(--heading); }
.sources { color: var(--muted); font-size: .85em; border-top: 1px solid var(--border); padding-top: .4em; }
.sources ul { padding-left: 1.2em; }
.table { overflow-x: auto; }
.sources table { border-collapse: collapse; margin-top: .5em; }
.sources td, .sources th { padding: .35em .5em; vertical-align: top; border-top: 1px solid var(--border); text-align: left; }
.composer { position: sticky; bottom: 0; background: var(--bg); padding: .8em 0 .4em; margin-top: 1em; }
.composer form { display: flex; gap: .5em; align-items: flex-end; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: .5em; }
textarea { flex: 1; font: inherit; color: var(--text); background: transparent; border: 0; padding: .45em .5em; resize: none; min-height: 2.6em; }
textarea:focus { outline: none; }
.composer form:focus-within { border-color: var(--secondary); box-shadow: 0 0 0 2px rgba(114, 181, 163, 0.35); }
.hint { font-size: .78em; color: var(--muted); margin: .3em .2em 0; }
button.send { font: inherit; font-weight: 600; color: #fff; background: var(--accent); border: 0; border-radius: 8px; padding: .55em 1.2em; cursor: pointer; }
button.send:hover { background: var(--accent-dark); }
button.send:disabled { opacity: .6; cursor: progress; }
pre { white-space: pre-wrap; background: var(--code-bg); padding: 1em; border-radius: 6px; }
</style></head><body>
<header><div class="bar">
<div class="title"><h1>AI Platform POC</h1><p>{use_case}</p></div>
<form method="get" action="/"><label>{i_am} <select name="role" onchange="if (this.selectedOptions[0].dataset.use != '{use_case_key}') { this.form.q.value = ''; this.form.c.value = ''; } this.form.submit()">{roles}</select></label>{keep}</form>
<a href="/?role={role}">{new_chat}</a>
</div></header>
<main>
"""


# Lidt JavaScript til sidst på siden. Siden virker også uden.
# Enter sender (Shift+Enter giver en ny linje), knappen låses, så man ikke sender to gange, og et eksempel kan klikkes.
SCRIPT = """<script>
for (const form of document.querySelectorAll(".composer form")) {
  const box = form.querySelector("textarea"), send = form.querySelector("button");
  box.addEventListener("keydown", e => { if (e.key == "Enter" && !e.shiftKey && box.value.trim()) { e.preventDefault(); form.requestSubmit(); } });
  form.addEventListener("submit", e => { if (!box.value.trim()) { e.preventDefault(); return; } send.disabled = true; send.textContent = "{working}"; });
}
for (const chip of document.querySelectorAll(".chip")) {
  chip.addEventListener("click", () => { const box = document.querySelector(".composer textarea"); box.value = chip.textContent; box.form.requestSubmit(); });
}
</script>"""


# Alle tekster på siden, på hvert sprog. Sproget vælges med LANGUAGE i settings.py.
# Hvorfor ét sted? Så kan siden skifte sprog uden at røre resten af koden, og en manglende oversættelse ses let.
TEXTS = {
    "da": {
        "i_am": "Jeg er", "new_chat": "Ny samtale", "working": "Arbejder …", "or": " eller ",
        "skill": "📘 Henter reglerne i {}", "search_requirements": "🔎 Slår testcases op: {}",
        "list_requirements": "📋 Ser listen over alle tests igennem", "search_specification": "📋 Slår forretningens krav op: {}",
        "list_code_files": "📂 Ser projektets filer igennem", "read_code_file": "📄 Læser {}",
        "list_recent_changes": "🕓 Ser de seneste ændringer på branchen",
        "failed": " (fejlede)",
        "checking_pr": "Tjekker pull request", "no_pr": "Ingen åben pull request passer til spørgsmålet, så jeg tjekker",
        "starting_from": "Starter fra de seneste ændringer på",
        "code": "Kode:", "at_commit": "ved commit", "from_pr": "fra", "sources": "Kilder", "test_cases": "Testcases:",
        "requirements": "Forretningens krav:",
        "works": "Virker", "see_it": "Se svaret til IT", "requirement": "Kravet", "why_fails": "Hvorfor det fejler",
        "where": "Hvor", "fix": "Ret", "per_requirement": "Vurdering pr. krav", "ai_asks": "AI spørger",
        "your_question": "Dit spørgsmål", "hint": "Enter sender · Shift+Enter giver en ny linje",
        "welcome": "Hvad vil du vide?", "ask_about": "Spørg {}.", "written_for": "Svaret skrives til {}.", "eg": "Fx: {}",
        "ask": "Spørg", "ask_more": "Spørg videre", "how": "Sådan finder jeg svaret",
        "nothing_in_docs": "Jeg fandt ikke noget i testprotokollerne om det.", "lookup_failed": "Opslaget fejlede: {}",
        "answer_for": "AI · svar til {}", "fetch_failed": "Kunne ikke hente koden, så den sidste kopi bruges: {}",
        "reused": "Koden og kravene er ikke ændret, så det tidligere tjek bruges",
        "checked_before": "Tjekket før på commit {}, så kun det, der er ændret siden, læses ({} {}):", "file": "fil", "files": "filer",
        "not_finished": "<b>Ikke færdig.</b> Agenten nåede ikke frem til en vurdering. Prøv at spørge igen, gerne med user storyens id.",
        "model_text": "Det, modellen skrev",
        "writing": "Skriver svaret", "yes_check": "Ja, tjek det", "reply_here": "Svar her", "reply": "Svar",
        "error": "Fejl.", "try_again": "Prøv igen",
        "teams": {
            settings.TEAM: ("Kodetjek", "om koden løser en user story", ["Løser koden US-004?", "Er kravene til regninger overholdt?"]),
        },
    },
    "en": {
        "i_am": "I am", "new_chat": "New chat", "working": "Working …", "or": " or ",
        "skill": "📘 Loading the rules in {}", "search_requirements": "🔎 Looking up test cases: {}",
        "list_requirements": "📋 Going through the list of all tests", "search_specification": "📋 Looking up the business requirements: {}",
        "list_code_files": "📂 Going through the project's files", "read_code_file": "📄 Reading {}",
        "list_recent_changes": "🕓 Looking at the latest changes on the branch",
        "failed": " (failed)",
        "checking_pr": "Checking pull request", "no_pr": "No open pull request matches the question, so I'm checking",
        "starting_from": "Starting from the latest changes on",
        "code": "Code:", "at_commit": "at commit", "from_pr": "from", "sources": "Sources", "test_cases": "Test cases:",
        "requirements": "Business requirements:",
        "works": "Works", "see_it": "See the answer for IT", "requirement": "Requirement", "why_fails": "Why it fails",
        "where": "Where", "fix": "Fix", "per_requirement": "Assessment per requirement", "ai_asks": "AI asks",
        "your_question": "Your question", "hint": "Enter sends · Shift+Enter adds a new line",
        "welcome": "What do you want to know?", "ask_about": "Ask {}.", "written_for": "The answer is written for {}.", "eg": "E.g. {}",
        "ask": "Ask", "ask_more": "Ask a follow-up", "how": "How I find the answer",
        "nothing_in_docs": "I didn't find anything about that in the test protocols.", "lookup_failed": "The lookup failed: {}",
        "answer_for": "AI · answer for {}", "fetch_failed": "Could not fetch the code, so the last copy is used: {}",
        "reused": "The code and requirements haven't changed, so the earlier check is used",
        "checked_before": "Checked before on commit {}, so only what changed since is read ({} {}):", "file": "file", "files": "files",
        "not_finished": "<b>Not finished.</b> The agent didn't reach an assessment. Try asking again, ideally with the user story's id.",
        "model_text": "What the model wrote",
        "writing": "Writing the answer", "yes_check": "Yes, check it", "reply_here": "Reply here", "reply": "Reply",
        "error": "Error.", "try_again": "Try again",
        "teams": {
            settings.TEAM: ("Code check", "whether the code solves a user story", ["Does the code solve US-004?", "Are the billing requirements met?"]),
        },
    },
}
T = TEXTS[settings.LANGUAGE]
SCRIPT = SCRIPT.replace("{working}", T["working"])

# Hvad hvert værktøj hedder for en bruger, der ikke kender værktøjerne.
FRIENDLY = {
    "load_skill": lambda a: T["skill"].format(a.get('name', '')),
    "search_requirements": lambda a: T["search_requirements"].format(a.get('query', '')),
    "list_requirements": lambda a: T["list_requirements"],
    "search_specification": lambda a: T["search_specification"].format(a.get('query', '')),
    "list_code_files": lambda a: T["list_code_files"],
    "read_code_file": lambda a: T["read_code_file"].format(a.get('path', '').replace(chr(92), '/').split('/')[-1]),
    "list_recent_changes": lambda a: T["list_recent_changes"],
}

# Teksten på siden for hvert hold: overskrift, hvad man kan spørge om, og eksempler, man kan klikke på.
# En rolle, der ser flere hold, får dem alle.
PAGE_TEXT = T["teams"]


def page_text(teams: list[str]) -> tuple[str, str, list[str]]:
    """Overskrift, hvad man kan spørge om, og eksempler til siden for en rolle, der ser de givne hold."""
    heading = " · ".join(PAGE_TEXT[t][0] for t in teams)
    topics = T["or"].join(PAGE_TEXT[t][1] for t in teams)
    examples = [e for t in teams for e in PAGE_TEXT[t][2]]
    return heading, topics, examples


def render_step(steps: list[Step]) -> str:
    """Ét skridt som én kort linje pr. handling, i et sprog brugeren forstår."""
    html = ""
    for step in steps:
        a, o = step.action, step.observation
        label = FRIENDLY.get(a.tool, lambda _: f"⚙️ {a.tool}")(a.arguments)
        css = "step error" if o.is_error else "step"
        html += f'<p class="{css}">{escape(label)}{T["failed"] if o.is_error else ""}</p>'
    return html


def code_repo(folder: Path) -> str:
    """Repoets adresse fra .git/config i kodemappen, hvis der er en."""
    config = folder / ".git" / "config"
    if config.exists():
        match = re.search(r"url\s*=\s*(\S+)", config.read_text(encoding="utf-8", errors="ignore"))
        if match:
            return match.group(1)
    return ""


def render_checkout(checkout: Checkout) -> str:
    """Skridtet, der siger, hvilken branch agenten ser, og hvorfor."""
    html = f'<p class="step error">🔀 {escape(checkout.note)}</p>' if checkout.note else ""
    pr = checkout.pull_request
    if pr:
        return html + (
            f'<p class="step">🔀 {T["checking_pr"]} <a href="{escape(pr.url)}">{pr.id} "{escape(pr.title)}"</a> '
            f'(<code>{escape(pr.branch)}</code> → {escape(settings.CODE_BRANCH)}), commit {escape(checkout.commit)}</p>'
        )
    return html + f'<p class="step">🔀 {T["no_pr"]} <code>{escape(checkout.branch)}</code> (commit {escape(checkout.commit)})</p>'


def render_changes(checkout: Checkout) -> str:
    """Skridtet, der viser de seneste commits, agenten starter fra: kun besked og filer, ikke hele diff'en."""
    commits = re.findall(r"^commit (\S+)\s+(\S+)\s+(.*)\n(.*)$", checkout.changes, re.MULTILINE)
    if not commits:
        return ""
    items = "".join(f"<li><code>{escape(h)}</code> {escape(d)}, {escape(a)}: {escape(s)}</li>" for h, d, a, s in commits)
    return f'<div class="step">🕓 {T["starting_from"]} <code>{escape(checkout.branch)}</code>:<ul>{items}</ul></div>'


def first_steps(words: str, checkout: Checkout | None) -> list[Action]:
    """Det, koden slår op, før modellen tænker: kravene, kravspec'en og de filer, de nyeste commits ændrede.

    Hvorfor ikke lade agenten selv gøre det?
    En lille lokal model springer tit værktøjerne over og skriver ud fra commits alene. Så bygger svaret
    ikke på user storyerne, og siden kan ikke vise, hvad den har kigget i. Agenten kan stadig søge og læse mere selv.
    """
    actions = [
        Action("first-req", "search_requirements", {"query": words}),
        Action("first-spec", "search_specification", {"query": words}),
    ]
    changed = re.findall(r"^diff --git a/(\S+) b/", checkout.changes, re.MULTILINE) if checkout else []
    files = [f for f in dict.fromkeys(changed) if f.endswith(settings.FIRST_FILE_TYPES)][: settings.FIRST_FILES]
    actions += [Action(f"first-file-{i}", "read_code_file", {"path": f}) for i, f in enumerate(files)]
    return actions


def changes_first(question: str, checkout: Checkout) -> str:
    """Spørgsmålet med de seneste commits foran, så agenten altid starter fra det, der er ændret."""
    return (
        f"{question}\n\n"
        f"These are the newest commits on {checkout.branch}, the latest changes, with the changed lines:\n\n{checkout.changes}\n\n"
        "Start from these changes. Find out which page or feature the changed code belongs to (follow who calls it), "
        "look up that feature's user stories and test cases, read the changed files and the code that uses them, "
        "and judge whether the requirements are still met after the changes. "
        "If the question names a user story, check that one, but still take the changes into account. "
        "If it is unclear what the user wants checked, ask with your best guess, as the code-review rules say."
    )


def render_sources(steps: list[Step], checkout: Checkout | None = None) -> str:
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
    code = f"<p>{T['code']} <code>{escape(str(settings.CODE_FOLDER))}</code>"
    code += f" (repo <code>{escape(repo)}</code>)" if repo else ""
    if checkout:
        # Hvilken branch og commit koden kom fra, og PR'en, hvis det var en PR's branch.
        code += f", branch <code>{escape(checkout.branch)}</code> {T['at_commit']} <code>{escape(checkout.commit)}</code>"
        if checkout.pull_request:
            code += f', {T["from_pr"]} <a href="{escape(checkout.pull_request.url)}">pull request {checkout.pull_request.id}</a>'
    code += "</p>"
    return (
        f'<details class="sources"><summary>{T["sources"]}</summary>'
        + rows(T["test_cases"], Path(settings.DATA_FOLDER), test_files)
        + rows(T["requirements"], Path(settings.SPEC_FOLDER), spec_files)
        + code
        + "".join(f"<li><code>{escape(f)}</code></li>" for f in code_files).join(("<ul>", "</ul>"))
        + "</details>"
    )


def render_assessment(assessment: Assessment, role: str) -> str:
    """Vurderingen, som begge roller bygger på, i en lukket boks under kilderne.

    IT ser hvorfor i koden, hvor og hvad der skal rettes. Produkt / kommunikation ser kun hvorfor, uden kode.
    """
    icons = {"MET": "✅", "NOT_MET": "❌", "CANT_TELL": "❓", "RISK": "⚠️"}
    technical = role == "it"

    def why(f) -> str:
        if technical:
            return f.code
        if f.status == "MET":
            return T["works"]
        return f.why or T["see_it"]

    def row(f) -> str:
        cells = f"<td>{icons[f.status]}</td><td>{escape(f.ids)}</td><td>{escape(f.requirement)}</td><td>{escape(why(f))}</td>"
        if technical:
            cells += f"<td><code>{escape(f.where)}</code></td><td>{escape(f.fix)}</td>"
        return f"<tr>{cells}</tr>"

    head = f"<tr><th></th><th>Id</th><th>{T['requirement']}</th><th>{T['why_fails']}</th>"
    head += f"<th>{T['where']}</th><th>{T['fix']}</th></tr>" if technical else "</tr>"
    rows = "".join(row(f) for f in assessment.findings)
    return f'<details class="sources"><summary>{T["per_requirement"]}</summary><div class="table"><table>{head}{rows}</table></div></details>'


def fingerprint(steps: list[Step]) -> str:
    """Et fingeraftryk af den kode og de krav, vurderingen bygger på.

    Hvorfor?
    AI'en kan vurdere den samme kode forskelligt fra gang til gang. Er koden og kravene uændrede,
    genbruges vurderingen, så den samme kode altid får det samme svar. Rettes en fil, tjekkes koden igen.
    """
    files = sorted({Path(settings.CODE_FOLDER) / s.action.arguments.get("path", "") for s in steps if s.action.tool == "read_code_file"})
    return hash_files(files) + requirements_fingerprint()


def requirements_fingerprint() -> str:
    """Fingeraftrykket af kravene alene. Er de ændret, tjekkes al koden igen, ikke kun de seneste ændringer."""
    return hash_files(sorted(Path(settings.SPEC_FOLDER).glob("*.md")) + sorted(Path(settings.DATA_FOLDER).glob("*.xlsx")))


def hash_files(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for file in files:
        digest.update(str(file).encode())
        digest.update(file.read_bytes() if file.is_file() else b"missing")
    return digest.hexdigest()


# Er flere filer ændret end det, er det nærmest et nyt projekt, og al koden tjekkes igen.
MAX_CHANGED_FILES = 20


def changes_question(question: str, earlier: str, commit: str, changed: list[str]) -> str:
    """Spørgsmålet til agenten, når kun de seneste ændringer skal tjekkes."""
    files = "\n".join(f"- {f}" for f in changed)
    return (
        f"{question}\n\n"
        f"You checked this before, on commit {commit}, and wrote this assessment:\n\n{earlier}\n\n"
        f"Since then only these files changed:\n{files}\n\n"
        "Look up the user story, test cases and requirements as usual, but only read the changed files "
        "(and another file only if a change cannot be understood without it). Then write the complete assessment again "
        "in the same format: keep the findings the changes do not touch, and update the ones they do."
    )


# Hvor mange tidligere spørgsmål og svar agenten får med. Flere gør prompten lang uden at hjælpe.
MAX_TURNS = 3

# Sådan starter agenten sit svar, når den ikke ved, hvilken user story der menes (skillen code-review).
CLARIFY = "QUESTION:"

# Det, agenten får at vide, når den allerede har stillet sit ene spørgsmål i samtalen.
ALREADY_ASKED = (
    "\n\nYou already asked the user a clarifying question in this conversation, and the message above is their answer. "
    "Do not ask again: write the assessment now. If they mean more than one user story (e.g. \"alle\"), assess all of them."
)


def read_conversation(raw: str) -> list[tuple[str, str]]:
    """Den tidligere samtale fra det skjulte felt c: en liste af [spørgsmål, svar].

    Hvorfor i siden og ikke på serveren?
    Så husker serveren ingenting mellem to spørgsmål, og en genstart mister ikke en samtale.
    Hver side har samtalen med i formularen og sender den med næste spørgsmål.
    """
    try:
        turns = json.loads(raw) if raw else []
        return [(str(q), str(a)) for q, a in turns][-MAX_TURNS:]
    except (ValueError, TypeError):
        return []


def with_conversation(question: str, conversation: list[tuple[str, str]]) -> str:
    """Spørgsmålet til agenten med den tidligere samtale foran, så "Den om billing" kan forstås."""
    if not conversation:
        return question
    earlier = "\n".join(f"User: {q}\nYou: {a}" for q, a in conversation)
    return f"Earlier in this conversation:\n{earlier}\n\nThe user now says: {question}\nRead it in the light of the earlier conversation."


def render_user(question: str) -> str:
    """Et spørgsmål fra brugeren som en boble til højre."""
    return f'<div class="msg user"><div class="bubble">{escape(question)}</div></div>'


def render_agent(html: str, who: str = "AI", css: str = "") -> str:
    """Et svar fra agenten som en boble til venstre."""
    return f'<div class="msg agent {css}"><div class="who">{escape(who)}</div><div class="bubble">{html}</div></div>'


def render_conversation(conversation: list[tuple[str, str]]) -> str:
    """Den tidligere samtale som bobler, så man kan se, hvad der allerede er sagt."""
    def agent(a: str) -> str:
        # Et opklarende spørgsmål står i samtalen med QUESTION: foran, så agenten kan se, at den allerede har spurgt.
        if a.startswith(CLARIFY):
            return render_agent(render_markdown(a[len(CLARIFY):].strip()), T["ai_asks"], "asks")
        return render_agent(render_markdown(a))
    return "".join(render_user(q) + agent(a) for q, a in conversation)


def render_verdict(assessment: Assessment, answer: str) -> str:
    """Dommen som et farvet mærke over svaret: grøn, når alt er opfyldt, orange for delvist og rød for ingenting."""
    met = assessment.count("MET")
    total = met + assessment.count("NOT_MET") + assessment.count("CANT_TELL")
    css = "ok" if met == total else "bad" if met == 0 else "part"
    word, _, rest = assessment.verdict.partition(". ")
    body = answer[len(assessment.verdict):] if answer.startswith(assessment.verdict) else answer
    return (
        f'<span class="verdict {css}">{escape(word.strip("*"))}</span><span class="count">{escape(rest)}</span>'
        + render_markdown(body)
    )


def render_composer(turns: list[tuple[str, str]], role: str, placeholder: str, button: str) -> str:
    """Feltet nederst på siden. Samtalen indtil nu ligger i det skjulte felt c og sendes med næste spørgsmål."""
    turns = turns[-MAX_TURNS:]
    return (
        '<div class="composer"><form method="get" action="/">'
        f'<input type="hidden" name="role" value="{escape(role)}">'
        f'<input type="hidden" name="c" value="{escape(json.dumps(turns, ensure_ascii=False)) if turns else ""}">'
        f'<textarea name="q" rows="1" placeholder="{escape(placeholder)}" aria-label="{escape(T['your_question'])}" autofocus></textarea>'
        f'<button class="send">{escape(button)}</button></form>'
        f'<p class="hint">{T["hint"]}</p></div>'
    )


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


def make_handler(agents, writer, checkouts, router=None, docs=None):

    # Hvorfor gemme vurderingen?
    # Skifter man rolle eller spørger igen om uændret kode, skal svaret bygge på den samme vurdering.
    # Ellers vurderer AI'en koden forfra og kan komme frem til noget andet.
    # Den ligger kun i hukommelsen, så en genstart af serveren laver en ny.
    checked: dict[str, tuple] = {}

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            # SPØRGSMÅL: Browseren sender spørgsmålet som ?q=... i adressen.
            url = urlparse(self.path)
            if url.path != "/":
                self.send_error(404)
                return
            query = parse_qs(url.query)
            question = query.get("q", [""])[0].strip()
            # Den tidligere samtale, hvis spørgsmålet kommer fra feltet under et svar.
            conversation = read_conversation(query.get("c", [""])[0]) if question else []
            # Det, agenten og skribenten får: spørgsmålet med samtalen foran.
            asked = with_conversation(question, conversation)
            # Rollen kommer fra dropdownen. Den står i adressen, så den er valgt igen ved næste spørgsmål.
            # Skifter man til en rolle, der ser andre hold, starter en ny samtale, fordi spørgsmålet måske ikke giver mening der.
            role = query.get("role", [settings.DEFAULT_ROLE])[0]
            if role not in settings.ROLES:
                role = settings.DEFAULT_ROLE
            teams = settings.ROLE_TEAMS[role]
            # Rollen bestemmer agenten, og dermed hvilke hold AI'en kan se. AI'en vælger det ikke selv.
            agent = agents[role]
            checks_code = settings.TEAM in teams

            # Hvorfor ingen Content-Length?
            # Siden er ikke færdig, når vi begynder at sende den. Browseren læser,
            # indtil serveren lukker forbindelsen, og viser undervejs det, der er kommet.
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            roles = "".join(
                f'<option value="{key}" data-use="{"+".join(settings.ROLE_TEAMS[key])}"'
                f'{" selected" if key == role else ""}>{escape(label)}</option>'
                for key, label in settings.ROLES.items()
            )
            # Skifter man rolle, sendes det samme spørgsmål og den samme samtale igen, så svaret til den anden rolle
            # hentes med det samme, og vurderingen genbruges.
            keep = (
                f'<input type="hidden" name="q" value="{escape(question)}">'
                f'<input type="hidden" name="c" value="{escape(json.dumps(conversation, ensure_ascii=False)) if conversation else ""}">'
            )
            heading, topics, examples = page_text(teams)
            self.write(
                HEAD.replace("{roles}", roles).replace("{keep}", keep).replace("{role}", escape(role))
                .replace("{use_case_key}", "+".join(teams)).replace("{use_case}", heading)
                .replace("{lang}", settings.LANGUAGE).replace("{i_am}", T["i_am"]).replace("{new_chat}", T["new_chat"])
            )

            if not question:
                # Ingen spørgsmål endnu: sig, hvad man kan spørge om, og vis eksempler, man kan klikke på.
                chips = "".join(f'<button type="button" class="chip">{escape(e)}</button>' for e in examples)
                self.write(
                    f'<div class="welcome"><h2>{T["welcome"]}</h2><p>{escape(T["ask_about"].format(topics))} '
                    f'{escape(T["written_for"].format(settings.ROLES[role]))}</p><div class="chips">{chips}</div></div>'
                    + render_composer([], role, T["eg"].format(examples[0]), T["ask"]) + SCRIPT + "</main></body></html>"
                )
                return

            self.write(render_conversation(conversation) + render_user(question))

            # HVAD KRÆVER SPØRGSMÅLET? Ét kald uden værktøjer afgør det (agent.py: Router).
            # Småsnak som "Hej, hvordan går det" svares med det samme. Et spørgsmål som "Hvilke tests er der?"
            # slås op i testprotokollerne og kravene. Ingen af dem henter koden eller læser commits.
            # Har agenten lige stillet et spørgsmål, er beskeden et svar på det og går direkte til kodetjekket.
            asked_before = any(a.startswith(CLARIFY) for _, a in conversation)
            route, answer = router.route(asked, topics) if router and checks_code and not asked_before else ("", "")
            if route == CHAT:
                turns = conversation + [(question, answer)]
                self.write(render_agent(render_markdown(answer), "AI") + render_composer(turns, role, T["ask_more"], T["ask"]))
                self.write(SCRIPT + "</main></body></html>")
                return
            if route == DOCS and docs:
                self.write(f'<details class="work" id="work" open><summary>{T["how"]}</summary><p class="busy" id="busy">{T["working"]}</p>')
                try:
                    run = docs.run(f"{asked}\n\nThe reader is {settings.ROLES[role]}.", on_step=lambda s: self.write(render_step(s)))
                    reply = run.answer.strip() or T["nothing_in_docs"]
                except Exception as e:
                    reply = T["lookup_failed"].format(repr(e))
                    run = None
                self.write('</details><script>work.open = false; busy.remove()</script>')
                self.write(render_agent(render_markdown(reply) + (render_sources(run.steps) if run else ""), T["answer_for"].format(settings.ROLES[role])))
                self.write(render_composer(conversation + [(question, reply)], role, T["ask_more"], T["ask"]) + SCRIPT + "</main></body></html>")
                return
            # Skridtene står i en boks, der er åben, mens agenten arbejder, og foldes sammen, når svaret er klar.
            self.write(f'<details class="work" id="work" open><summary>{T["how"]}</summary>')
            self.write(f'<p class="busy" id="busy">{T["working"]}</p>')
            work_open = True

            def close_work() -> None:
                nonlocal work_open
                if work_open:
                    self.write('</details><script>work.open = false; busy.remove()</script>')
                    work_open = False

            # Et kodetjek holder låsen, til svaret er skrevet, så et andet spørgsmål ikke skifter branch imens.
            holds_code = checks_code and checkouts is not None
            if holds_code:
                checkouts.lock.acquire()
            checkout = None
            turns = conversation
            try:
                if holds_code:
                    # Vælg branch (en PR, der passer til spørgsmålet, ellers dev) og hent det nyeste, så en udvikler kan pushe og straks spørge.
                    # Det sker før fingeraftrykket herunder, så en anden branch eller en ændret fil giver et nyt tjek.
                    try:
                        # Kun brugerens egne ord, så et id, agenten selv nævnte i sit spørgsmål, ikke vælger en PR.
                        checkout = checkouts.checkout(" ".join([q for q, _ in conversation] + [question]))
                        self.write(render_checkout(checkout) + render_changes(checkout))
                    except RuntimeError as e:
                        self.write(f'<p class="step error">🔀 {escape(T["fetch_failed"].format(e))}</p>')

                # Samme spørgsmål med andre store/små bogstaver, mellemrum eller tegnsætning genbruger vurderingen,
                # så længe koden og kravene er uændrede. Er en fil rettet, tjekkes koden igen.
                key = " ".join(re.sub(r"[^\w\s-]", " ", asked.lower()).split())
                # Kun roller, der tjekker kode, kan genbruge en vurdering.
                cached = checked.get(key) if checks_code else None
                # En ny commit giver altid et nyt tjek, også hvis den ændrer en fil, agenten ikke læste sidst.
                same_commit = not checkout or cached and cached[4] == checkout.commit
                if cached and same_commit and cached[2] == fingerprint(cached[0].steps):
                    run, assessment = cached[0], cached[1]
                    self.write(f'<p class="step">♻️ {T["reused"]}</p>')
                else:
                    # Hvorfor kun de seneste ændringer?
                    # Er koden tjekket før på samme branch, og er kravene uændrede, er det kun de nye commits, der kan ændre svaret.
                    # Agenten får den tidligere vurdering og listen over ændrede filer og læser kun dem.
                    changed, earlier = None, None
                    if cached and checkout and cached[3] == checkout.branch and cached[5] == requirements_fingerprint():
                        changed = checkouts.changed_since(cached[4])
                        if changed and len(changed) <= MAX_CHANGED_FILES:
                            earlier = cached[0]
                    task = changes_first(asked, checkout) if checkout and checkout.changes.startswith("commit ") else asked
                    if asked_before:
                        # Hvorfor siger koden det, når skillen allerede gør?
                        # En lille model spørger ellers igen og igen, selvom brugeren har svaret.
                        task += ALREADY_ASKED
                    if earlier:
                        self.write(
                            f'<p class="step">🔁 {escape(T["checked_before"].format(cached[4], len(changed), T["file"] if len(changed) == 1 else T["files"]))} '
                            + ", ".join(f"<code>{escape(f)}</code>" for f in changed) + "</p>"
                        )
                        task = changes_question(asked, earlier.answer, cached[4], changed)
                    # AGENTEN KØRER: Fortsæt i agent.py.
                    # VIS SKRIDT: on_step kaldes efter hvert skridt, og render_step() sender det til browseren med det samme.
                    # Agenten får ikke rollen. Vurderingen skal være den samme, uanset hvem der spørger.
                    words = " ".join([q for q, _ in conversation] + [question])
                    first = first_steps(words, checkout) if settings.FIRST_STEPS else []
                    run = agent.run(task, on_step=lambda s: self.write(render_step(s)), first=first)
                    if earlier:
                        # Kilderne og fingeraftrykket skal dække al den kode, vurderingen bygger på, også den fra det tidligere tjek.
                        run = AgentRun(run.answer, earlier.steps + run.steps, run.finished)
                    assessment = parse_assessment(run.answer, settings.LANGUAGE) if run.finished and checks_code else None
                    if assessment:
                        commit = (checkout.branch, checkout.commit) if checkout else ("", "")
                        checked[key] = (run, assessment, fingerprint(run.steps), *commit, requirements_fingerprint())

                # Det, der står i svaret, og som næste spørgsmål i samtalen får med.
                reply, asks_back = run.answer, False
                who = T["answer_for"].format(settings.ROLES[role])
                if not assessment and run.finished and run.answer.strip().upper().startswith(CLARIFY):
                    # Spørgsmålet var uklart, så agenten spørger med sit bedste gæt i stedet for at vurdere noget forkert.
                    # Svaret sendes med samtalen i feltet herunder.
                    reply, asks_back = run.answer.strip()[len(CLARIFY):].strip(), True
                    close_work()
                    self.write(render_agent(render_markdown(reply), T["ai_asks"], "asks"))
                    reply = f"{CLARIFY} {reply}"
                elif not assessment:
                    # Agenten blev ikke færdig eller skrev ikke en vurdering. Vis det, den skrev.
                    close_work()
                    self.write(render_agent(
                        f'<p class="error">{T["not_finished"]}</p>'
                        # Teksten er ikke en vurdering og ofte lang og på engelsk, så den står i en lukket boks.
                        + f'<details class="sources"><summary>{T["model_text"]}</summary>{render_markdown(run.answer)}</details>'
                        + render_sources(run.steps, checkout), who
                    ))
                else:
                    # OUTPUT: Vurderingen skrives om til et svar til rollen, laves om fra markdown til HTML og sendes. SLUT.
                    # Dommen står som et farvet mærke øverst, og kilderne og vurderingen står i lukkede bokse under svaret.
                    self.write(f'<p class="step">✍️ {T["writing"]}</p>')
                    reply = writer.write(asked, assessment, role)
                    close_work()
                    self.write(render_agent(
                        render_verdict(assessment, reply) + render_sources(run.steps, checkout) + render_assessment(assessment, role), who
                    ))
                turns = conversation + [(question, reply)]
                if asks_back:
                    # Agenten har gættet, hvad der menes. Ét klik siger ja til gættet.
                    self.write(f'<div class="chips reply"><button type="button" class="chip">{T["yes_check"]}</button></div>')
                self.write(render_composer(turns, role, T["reply_here"] if asks_back else T["ask_more"], T["reply"] if asks_back else T["ask"]))
            except Exception as e:
                # Fejlen vises på siden, så demoen ikke bare hænger.
                close_work()
                self.write(render_agent(f'<p class="error"><b>{T["error"]}</b></p><pre>{escape(repr(e))}</pre>', "AI", "asks"))
                self.write(render_composer(turns, role, T["try_again"], T["ask"]))
            finally:
                if holds_code:
                    checkouts.lock.release()
            self.write(SCRIPT + "</main></body></html>")

        def write(self, html: str) -> None:
            self.wfile.write(html.encode("utf-8"))
            self.wfile.flush()

    return Handler


def main():
    # START: agenterne bygges én gang, så xlsx-filerne kun indlæses ved start. Fortsæt i build.py.
    agents, docs = build_agents()
    writer = build_writer()
    router = build_router()
    # Branch-valget og repoet med koden, hvis den hentes fra et repo (CODE_REPO). Fortsæt i build.py.
    checkouts = build_checkout_service()

    # VENT: Serveren er klar og venter på, at nogen stiller et spørgsmål på siden.
    # Hvert spørgsmål lander i Handler.do_GET() herover.
    server = ThreadingHTTPServer(("localhost", PORT), make_handler(agents, writer, checkouts, router, docs))
    print(f"AI Platform POC is running on http://localhost:{PORT} (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()
