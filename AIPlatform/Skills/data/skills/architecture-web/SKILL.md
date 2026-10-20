---
name: architecture-web
description: How the Web team builds its Umbraco/.NET web solutions. Use together with code-review when the code belongs to the Web team.
---

# How the Web team codes

This is how the Web team builds its solutions. It is fixed in advance and does not depend on the project or on any requirements.
Compare the code you have read with it, and point out where the code does it differently, with a file:line reference.

## Solution structure
The solution is an Umbraco site on ASP.NET Core, split into these parts:
- **Controllers/Surface/**: Umbraco Surface controllers, one per page or feature (`<Feature>SurfaceController`). They read the request, call a service and return a view or partial. No business logic here.
- **Views/**: Razor views (`.cshtml`) that only display a view model.
- **wwwroot/scripts/<Area>/**: one JavaScript file per page for behaviour in the browser. No business rules that the server does not also check.
- **Core/<Feature>/**: the business layer, one folder per feature, with `Services/` for the logic and `Models/` for the feature's own models.
- **Models/ViewModels/**: the models the views get.
- **Shared/Managers/**: managers that talk to external systems and web services. Only services call them.

So the flow is always: Surface controller → service in `Core/<Feature>/Services` → manager in `Shared/Managers` → external system.

## Services
- Each service has an interface `I<Name>Service` declared at the top of the same file, followed by the class `<Name>Service : I<Name>Service`.
- The namespace matches the folder (`<Solution>.Core.<Feature>.Services`) and is file-scoped (`namespace ...;`).
- Dependencies come in through the constructor as interfaces and are stored in `private readonly` fields named `_camelCase`.
- The logged-in customer and their current choices (such as the selected contract) are read through the state manager service from `Core/Authentication/Services` and the session, never passed in from the browser.
- Data from an external system is mapped to the feature's own model in `Core/<Feature>/Models` (e.g. with `Select(x => new ...Model { ... })`) before it leaves the service. Views and controllers never see the external system's types.
- Public service methods return `Task<...>`.

## Quality the team expects
- Async all the way: an `async` method awaits its I/O, and nothing blocks on `.Result` or `.Wait()`.
- Lists are never returned as `null`; an empty list is returned instead.
- Data from the outside (external systems, session, state) may be missing. It is checked, and errors are logged with `ILogger` instead of throwing at the user.
- Dates and numbers are parsed with `TryParse` and a `CultureInfo`.
- No magic strings: session keys and fixed values are constants or enums in one place.
- Types say what they are: a yes/no value becomes a `bool` once, in the mapping, and is never passed around as the string `"true"`.
- Names are correct English, and there is no dead or duplicated code.
