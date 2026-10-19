---
name: architecture-web
description: How the Web team builds its .NET web solutions. Use together with code-review when the code belongs to the Web team.
---

# How the Web team codes

This is how the Web team builds every solution. It is fixed in advance and does not depend on the project or on any requirements.
Compare the code you have read with it, and point out where the code does it differently, with a file:line reference.

## Three-layer architecture
The code is split into three layers, and each layer only talks to the layer below it:
- **Presentation**: controllers, views and front-end scripts. A controller reads the request, calls a service and returns a view or result. No business logic here.
- **Business**: services with the business logic, such as filtering, sorting and calculations.
- **Data**: repositories and integrations that read from databases and external systems. Nothing above this layer talks to a database or an external system directly.

## Interfaces and dependency injection
- Every service, repository and integration has an interface, and the other layers depend on the interface, not on the class.
- Dependencies come in through the constructor and are registered in dependency injection. No `new` of services inside other classes.

## Robust code
- Async all the way: an `async` method awaits its I/O, and nothing blocks on `.Result` or `.Wait()`.
- Lists are never returned as `null`; an empty list is returned instead.
- Data from the outside (external systems, session, request) may be missing. It is checked, and errors are logged with `ILogger` instead of throwing at the user.
- Dates and numbers are parsed with `TryParse` and a `CultureInfo`.

## Clean code
- No magic strings: keys and fixed values are constants or enums in one place.
- Types say what they are: a yes/no value is a `bool`, not a string.
- Names are correct English, and there is no dead or duplicated code.
