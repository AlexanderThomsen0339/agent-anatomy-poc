---
name: architecture-web
description: The Web team's coding and architecture rules for all its .NET web projects. Use together with code-review when the code belongs to the Web team.
---

# The Web team's architecture rules

DRAFT for the demo. The Web team has not approved these rules yet.
The rules apply to every project the Web team builds. They name no product, customer or system.

Check the code you have read against each rule. Only report a rule that is broken, with a file:line reference. Never invent a rule that is not on this list.

## Layers
- **ARK-WEB-01: Controllers stay thin.** A controller reads the request, calls a service and returns a view or result. Business logic, filtering and sorting belong in a service.
- **ARK-WEB-02: External systems sit behind an interface.** Calls to external systems (APIs, web services, databases) go through a service or manager interface, never directly from a controller or view.
- **ARK-WEB-03: Dependencies come through the constructor.** Services are registered in dependency injection and depend on interfaces, not on `new` of concrete classes.

## Robustness
- **ARK-WEB-04: Never return null for a list.** A method that returns a list returns an empty list, so callers don't have to null-check.
- **ARK-WEB-05: Null-check data from outside.** Data from external systems, the session or the request may be missing. Handle it without a NullReferenceException and log it with `ILogger`.
- **ARK-WEB-06: async means await.** An `async` method awaits its I/O. An `async` method with no `await` is a bug or should not be async.
- **ARK-WEB-07: Parse with a culture.** Dates and numbers are parsed with `TryParse` and a `CultureInfo`, never `DateTime.Parse` or `decimal.Parse` alone.

## Readability
- **ARK-WEB-08: No magic strings.** Session keys, configuration keys and status values are constants or enums, defined in one place.
- **ARK-WEB-09: Types say what they are.** A yes/no value is a `bool` and a fixed set of values is an enum, not a string such as `"true"`.
- **ARK-WEB-10: Names are correct English.** Classes, methods and properties are spelled correctly in English. No dead code, such as a variable assigned twice.
