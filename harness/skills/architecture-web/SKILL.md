---
name: architecture-web
description: Describes how the Web team builds its .NET (C#, ASP.NET Core) web solutions. Use together with code-review when the code belongs to the Web team. Supplies the architecture-deviation half of evaluation's Node 4 quality gate.
---

# How the Web team codes

This is fixed in advance and does not depend on the project or the requirements. It feeds `evaluation`'s Node 4 ("Evaluate Conflicts") gate in `code-review`: a conflict with the rules below is reported as a `RISK` line exactly like a conflict with a user story or test case is reported as `NOT_MET`. Where the code does it differently, that is a `RISK` line.

## Solution structure
The flow is always: controller → service in `Core/<Feature>/Services` → manager → external system.
- **Controllers/**: one per page or feature. An action calls a service and returns a view with a view model. No business logic.
- **Views/** (`.cshtml`): only display the view model. No service calls and no calculations.
- **Core/<Feature>/**: the business layer, with `Services/` for the logic and `Models/` for the feature's own models.
- **Core/Authentication/Services/**: the session service, which knows the logged-in customer and their current choices.
- **Managers/**: talk to external systems. Only services call them.
- **Models/ViewModels/**: the view models.
- **Program.cs** (or a composer): registers every service and manager in the DI container.

## Services
- Each service has an interface `I<Name>Service`, and others depend on the interface, never the class.
- Dependencies come through the constructor as interfaces into `private readonly` fields (`_name`). No `new` of dependencies and no service locator.
- The customer and their choices (such as the selected contract) come from the session service, never from the request. A value from the request (such as an invoice number) is checked on the server against what the customer has access to.
- Data from an external system is mapped to the feature's own model or a view model inside the service. Controllers and views never see the external system's types.
- I/O is `async` all the way, never `.Result` or `.Wait()`.

## Team rules
- A list is never `null`; return an empty list.
- Missing data from outside (external system, session, request) is checked. Errors are logged with `ILogger<T>` and never shown to the user as a technical error, and never swallowed without logging.
- Dates and numbers are parsed with `TryParse` and an explicit `CultureInfo`, and shown with an explicit format and culture. Money is `decimal`.
- No magic strings: session keys and fixed values are `const` or settings, and fixed choices are an `enum`.
- A yes/no value becomes a `bool` once, in the mapping, and is never passed around as the string `"true"`.
