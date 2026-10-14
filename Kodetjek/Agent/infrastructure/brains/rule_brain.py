"""Lærlingen: følger faste regler, uden internet og uden API-nøgle.

Den tænker ikke selv, men den arbejder på det rigtige spørgsmål og de rigtige data:
1. Henter skillen kodevurdering og søger kravene frem.
2. Vælger den user story, der passer bedst, og lister udviklerens filer.
3. Læser de filer, hvis navne ligner user storyens titel.
4. Skriver en rapport, hvor hvert acceptkriterie får de steder i koden, hvor dets ord står.

Værktøjskaldene er ægte. Vurderingen er ren ord-matchning, ikke en AI-vurdering,
og det står i svaret.
"""
import re

from Agent.domain.models import Action, Decision, History, Observation
from MCP.domain.models import ToolSpec

# Hvor mange filer lærlingen højst læser. Resten springes over.
MAX_FILES = 4

# Filer, der ikke er kode, og som derfor ikke læses.
NOT_CODE = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".mp4", ".woff", ".woff2", ".ttf", ".eot", ".pdf")

# Ord, der står i næsten alle krav og derfor ikke siger noget om, hvor i koden kravet er løst.
STOP_WORDS = {
    "kunden", "kunde", "skal", "kunne", "vises", "visning", "følgende", "eller", "samme", "hvis",
    "findes", "ikke", "både", "efter", "under", "mindst", "minimum", "valgte", "løsningen", "systemet",
}

DEMO_QUESTION = "Løser vores kode US-001 Vis regningsoversigt?"


def keywords(text: str) -> list[str]:
    """Ord på mindst 5 bogstaver, uden stopord. Korte ord giver for mange tilfældige træf."""
    words = re.findall(r"[a-zæøå]{5,}", text.lower())
    return list(dict.fromkeys(w for w in words if w not in STOP_WORDS))


class RuleBrain:

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        step = sum(1 for item in history if isinstance(item, Decision))
        seen = self._observations(history)

        if step == 0:
            # "acceptkriterier" i søgningen trækker user stories frem foran enkelte testcases.
            return Decision(
                "Jeg henter skillen til kodevurdering og søger kravene frem.",
                [
                    Action("1", "load_skill", {"name": "kodevurdering"}),
                    Action("2", "search_requirements", {"query": f"{question} acceptkriterier"}),
                ],
            )

        story = self._pick_story(seen.get("2", ""), question)
        if story is None:
            return Decision("Jeg fandt ingen user story, der passer til spørgsmålet. Prøv med id'et, fx US-002.")

        if step == 1:
            return Decision(
                f"Den bedste user story er {story['id']} {story['title']}. Nu ser jeg, hvilke filer der findes.",
                [Action("3", "list_code_files")],
            )

        files = self._pick_files(seen.get("3", ""), story["title"])
        if step == 2 and files:
            return Decision(
                f"Disse filer ligner \"{story['title']}\" på navnet. Jeg læser dem.",
                [Action(f"read-{i}", "read_code_file", {"path": path}) for i, path in enumerate(files)],
            )

        code = {path: seen.get(f"read-{i}", "") for i, path in enumerate(files)}
        return Decision(self._report(story, code))

    @staticmethod
    def _observations(history: History) -> dict[str, str]:
        """Alt, agenten har set indtil nu, slået op på handlingens id."""
        seen = {}
        for item in history:
            if isinstance(item, list):
                for observation in item:
                    if isinstance(observation, Observation):
                        seen[observation.action_id] = observation.content
        return seen

    @staticmethod
    def _pick_story(search_result: str, question: str) -> dict | None:
        stories = []
        for block in search_result.split("\n\n"):
            fields = dict(
                line.split(": ", 1) for line in block.splitlines() if ": " in line
            )
            us_id = next((v for k, v in fields.items() if k.endswith("US-ID")), None)
            if us_id and fields.get("Acceptkriterier"):
                stories.append({
                    "id": us_id,
                    "title": fields.get("Titel", ""),
                    "criteria": fields["Acceptkriterier"],
                    "testcases": fields.get("Testcases", ""),
                })
        if not stories:
            return None

        # Nævner udvikleren id'et, vinder den story. Ellers den, søgningen gav højest score.
        mentioned = [s for s in stories if s["id"].lower() in question.lower()]
        return (mentioned or stories)[0]

    @staticmethod
    def _pick_files(file_list: str, title: str) -> list[str]:
        words = keywords(title)
        matches = []
        for path in file_list.splitlines():
            name = path.rsplit("/", 1)[-1].lower()
            if name.endswith(NOT_CODE):
                continue
            if any(word in name for word in words):
                matches.append(path)
        return matches[:MAX_FILES]

    @staticmethod
    def _criteria(text: str) -> list[str]:
        # Kriterierne står som "1. ... 2. ..." eller "• ... • ..." i én celle.
        parts = re.split(r"\s*(?:•|\b\d{1,2}\.\s)\s*", text)
        return [p.strip() for p in parts if len(p.strip()) > 3]

    def _report(self, story: dict, code: dict[str, str]) -> str:
        lines = [
            f"Regelbaseret vurdering af {story['id']} {story['title']} (ingen AI: kun ord-matchning).",
            "",
        ]
        if not code:
            lines.append("Jeg fandt ingen filer, hvis navne ligner user storyen, så jeg har ikke læst noget kode.")
        else:
            lines.append("Læste filer: " + ", ".join(code))
        lines.append("")

        # Titlens ord står i alle de læste filer (det er derfor, de blev valgt), så de tæller ikke som spor.
        title_words = set(keywords(story["title"]))
        for number, criterion in enumerate(self._criteria(story["criteria"]), start=1):
            hits = self._find(criterion, code, title_words)
            if hits:
                lines.append(f"🔎 {number}. {criterion}")
                lines.append(f"     Spor i koden: {', '.join(hits)}")
            else:
                lines.append(f"❓ {number}. {criterion}")
                lines.append("     Ingen spor i de læste filer.")

        lines += [
            "",
            f"Testcases: {story['testcases']}",
            "",
            "🔎 betyder kun, at kriteriets ord står i koden, ikke at kriteriet er opfyldt. "
            "En rigtig vurdering kræver Claude (kør uden --fake med en API-nøgle).",
        ]
        return "\n".join(lines)

    @staticmethod
    def _find(criterion: str, code: dict[str, str], skip: set[str]) -> list[str]:
        """Finder fil:linje for de første steder, hvor kriteriets ord står i koden."""
        hits = []
        for word in keywords(criterion):
            if word in skip:
                continue
            for path, content in code.items():
                for line in content.splitlines():
                    number, _, text = line.partition(" | ")
                    if word in text.lower():
                        hits.append(f"{path.rsplit('/', 1)[-1]}:{number.strip()} ({word})")
                        break
            if len(hits) >= 3:
                break
        return hits[:3]
