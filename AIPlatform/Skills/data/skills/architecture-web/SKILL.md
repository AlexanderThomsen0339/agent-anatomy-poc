---
name: architecture-web
description: How the Web team builds its Python (Flask) web solutions. Use together with code-review when the code belongs to the Web team.
---

# How the Web team codes

This is how the Web team builds its solutions. It is fixed in advance and does not depend on the project or on any requirements.
Compare the code you have read with it, and point out where the code does it differently, with a file:line reference.

## Solution structure
The solution is a Flask site, split into these parts:
- **web/**: Flask routes, one `<feature>_routes.py` per page or feature, made by a `create_<feature>_routes(...)` function that gets its services. A route reads the request, calls a service and renders a template. No business logic here.
- **web/templates/**: Jinja templates that only display what the route gives them.
- **core/<feature>/**: the business layer, one folder per feature, with `services/` for the logic and `models/` for the feature's own models.
- **core/authentication/services/**: the session service, which knows the logged-in customer and their current choices.
- **shared/managers/**: managers that talk to external systems and web services. Only services call them.
- **shared/**: constants and formatting used by several features.
- **app.py**: the composition root. It creates every service and manager and passes them in.

So the flow is always: route → service in `core/<feature>/services` → manager in `shared/managers` → external system.

## Services
- Each service has an interface, a `typing.Protocol` named `<Name>Service`, at the top of the same file, followed by the class that implements it.
- Dependencies come in through the constructor typed as their `Protocol` and are stored in private attributes (`self._name`). Nothing creates its own dependencies, except `app.py`.
- The logged-in customer and their current choices (such as the selected contract) are read through the session service, never taken from the request. A value from the request (such as a chosen contract or an invoice number) is checked against what the customer has access to, on the server.
- Data from an external system is mapped to the feature's own model (a `dataclass`) in `core/<feature>/models` before it leaves the service. Routes and templates never see the external system's records.
- Public service methods have type hints on every argument and return value.

## Quality the team expects
- Lists are never returned as `None`; an empty list is returned instead.
- Data from the outside (external systems, session, request) may be missing. It is checked, and errors are logged with `logging` instead of being shown to the user as a technical error.
- Dates are parsed with `datetime.strptime` and a fixed format, and money is a `Decimal`, never a `float`.
- No magic strings: session keys and fixed values are constants in `shared/constants.py`, and fixed choices are an `Enum`.
- Types say what they are: a yes/no value becomes a `bool` once, in the mapping, and is never passed around as the string `"true"`.
- Names are correct English, and there is no dead or duplicated code.
