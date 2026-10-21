---
name: architecture-web
description: How the Web team builds its .NET (C#, ASP.NET Core) web solutions. Use together with code-review when the code belongs to the Web team.
---

# How the Web team codes

This is how the Web team builds its solutions. It is fixed in advance and does not depend on the project or on any requirements.
Compare the code you have read with it, and point out where the code does it differently, with a file:line reference.

## Solution structure
The solution is an ASP.NET Core (MVC) site, split into these parts:
- **Controllers/**: one controller per page or feature. An action reads the request, calls a service and returns a view or partial view with a view model. No business logic here.
- **Views/**: Razor views (`.cshtml`) that only display what the view model gives them. No calls to services or external systems, and no calculations.
- **Core/<Feature>/**: the business layer, one folder per feature, with `Services/` for the logic and `Models/` for the feature's own models.
- **Core/Authentication/Services/**: the session or state service, which knows the logged-in customer and their current choices.
- **Managers/**: managers that talk to external systems and web services. Only services call them.
- **Models/ViewModels/**: the view models the views display.
- **Program.cs** (or a composer/startup class): the composition root. Every service and manager is registered in the DI container here.

So the flow is always: controller → service in `Core/<Feature>/Services` → manager → external system.

## Services
- Each service has an interface named `I<Name>Service`, and the class that implements it. Others depend on the interface, never on the class.
- Dependencies come in through the constructor as interfaces and are stored in `private readonly` fields (`_name`). Nothing creates its own dependencies with `new`, and nothing uses a service locator; the DI container does it.
- The logged-in customer and their current choices (such as the selected contract) are read through the session or state service, never taken from the request. A value from the request (such as a chosen contract or an invoice number) is checked against what the customer has access to, on the server.
- Data from an external system is mapped to the feature's own model in `Core/<Feature>/Models` or a view model before it leaves the service. Controllers and views never see the external system's types.
- I/O (external systems, databases, files) is `async` all the way: methods return `Task`/`Task<T>`, are awaited, and never use `.Result` or `.Wait()`.

## Quality the team expects
- Methods never return `null` for a list; an empty list is returned instead. Nullable reference types are respected, and possible `null` values are checked.
- Data from the outside (external systems, session, request) may be missing. It is checked, and errors are caught and logged with `ILogger<T>` instead of being shown to the user as a technical error. An exception is never swallowed without logging.
- Dates and numbers are parsed with `TryParse` and an explicit `CultureInfo` and format, and shown with an explicit format and culture. Money is a `decimal`, never a `double` or `float`.
- No magic strings: session keys and fixed values are `const` or settings, and fixed choices are an `enum`.
- Types say what they are: a yes/no value becomes a `bool` once, in the mapping, and is never passed around as the string `"true"`.
- Names follow C# conventions (PascalCase for types, methods and properties, `_camelCase` for private fields, `Async` suffix where the team uses it), are correct English, and there is no dead, commented-out or duplicated code.
