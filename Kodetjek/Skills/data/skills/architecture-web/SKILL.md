---
name: architecture-web
description: The Web team's coding and architecture rules (Umbraco/.NET, Mit Aalborg Forsyning). Use together with code-review when the code belongs to the Web team.
---

# The Web team's architecture rules

DRAFT for the demo. Claude wrote these rules from one file in the code (BillingService.cs). The Web team has not approved them yet.

Check the code you have read against each rule. Only report a rule that is broken or worth praising, with a file:line reference. Never invent a rule that is not on this list.

## Layers
- **ARK-WEB-01: Controllers stay thin.** A controller reads the request, calls a service and returns a view or result. Business logic, filtering and sorting belong in a service in `Core/`.
- **ARK-WEB-02: Services hide external systems.** Calls to Xellent and other external systems go through a manager or service interface (e.g. `IXellentManager`), never directly from a controller or view.
- **ARK-WEB-03: Dependencies come through the constructor.** Services are registered in DI and depend on interfaces, not on `new` of concrete classes.

## Robustness
- **ARK-WEB-04: Never return null for a list.** A service returns an empty list, so callers don't have to null-check.
- **ARK-WEB-05: Null-check data from external systems and the session.** A missing customer, contract or session value must not throw a NullReferenceException. Handle it and log it with `ILogger`.
- **ARK-WEB-06: async means await.** An `async` method awaits its I/O. An `async` method with no `await` is a bug or should not be async.
- **ARK-WEB-07: Parse with a culture.** Dates and amounts are parsed with `DateTime.TryParse`/`decimal.TryParse` and a `CultureInfo`, never `DateTime.Parse` alone.

## Readability
- **ARK-WEB-08: No magic strings.** Session keys such as `"kontraktnr"` and status values are constants or enums, defined in one place.
- **ARK-WEB-09: Types say what they are.** A yes/no value is a `bool` or an enum in the model, not the string `"true"`.
- **ARK-WEB-10: Names are correct English.** Classes, methods and properties are spelled correctly in English (`GetInvoiceRows`, not `GetIvoiceRows`). No dead code such as a variable assigned twice.
