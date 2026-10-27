# Præsentation af AI Platform POC

Præsentationen til Kommunikation og IT: problemet, hvorfor AI Platform, hvorfor den er bygget sådan (Cognia, Anthropic og IBM), skalering og demo. 21 slides plus 4 skjulte backup-slides.

Åbn [praesentation.html](praesentation.html) i en browser for at se alle slides med talenoter under hvert slide.

## Filer

| Fil | Hvad |
|---|---|
| `deck.json` | Titel, rækkefølge, afsnit og skrifttyper |
| `slides/<id>.html` | Ét slide pr. fil. Talenoterne står i `<aside>`. Backup-slides har `hidden` |
| `billeder/` | Screenshots, slidesene bruger |
| `byg.py` | Samler slidesene til `praesentation.html` |
| `praesentation.html` | Den samlede side. Bygges, rettes ikke i hånden |

Efter en rettelse i `slides/` eller `deck.json`:

```bash
cd AIPlatform/Praesentation
python byg.py
```

Præsentationen vises bedst i Slides-artefaktet, hvor den også kan præsenteres og hentes som PowerPoint eller PDF. Filerne her er en kopi af artefaktet. Ikonerne vises kun som cirkler i `praesentation.html`.
