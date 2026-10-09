"""Porte for Agent-laget.

Hvorfor kun én port?
Agenten har brug for to ting udefra: en hjerne og værktøjer.
Værktøjerne har vi allerede en kontrakt for i lag 3 (ToolService),
så det eneste nye, laget skal bruge, er hjernen.
"""

# Hvorfor Protocol?
# Samme grund som i de andre lag: en adapter skal bare have de rigtige metoder.
from typing import Protocol

from MCP.domain.models import ToolSpec

from .models import Decision, History


# Hvorfor ikke bare bruge LLMProvider fra lag 1?
# LLMProvider kan kun tekst ind og tekst ud. En agent skal også kunne:
#   - fortælle modellen, hvilke værktøjer der findes
#   - få at vide, at modellen vil bruge et værktøj
#   - sende resultatet tilbage
# I stedet for at gøre lag 1 mere kompliceret for alle, får agenten sin
# egen lille port, der siger præcis det, den har brug for.
class AgentBrain(Protocol):

    # Hvorfor får hjernen hele historikken hver gang?
    # Modellen husker intet mellem kald. Skal den vide, hvad den allerede
    # har gjort og set, skal det hele sendes med.
    #
    # Hvorfor får den værktøjernes mærkater (ToolSpec)?
    # Det er dem, den vælger imellem. Mærkaterne kommer direkte fra lag 3.
    def decide(
        self,
        system: str,
        question: str,
        history: History,
        tools: list[ToolSpec],
    ) -> Decision:
        """Beslutter næste skridt: et endeligt svar eller en eller flere handlinger."""
        ...
