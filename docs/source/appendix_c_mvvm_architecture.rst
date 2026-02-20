Appendix C: MVVM Architecture
=============================

Overview
--------

Model-View-ViewModel (MVVM) emphasizes data binding between view and view-model.
It is common in UI frameworks with declarative views.

Roles
-----

Model
^^^^^

- Domain data and business rules.
- Independent of UI technologies.

View
^^^^

- UI elements and layout.
- Binds directly to view-model properties.

ViewModel
^^^^^^^^^

- Adapts model data into UI-friendly formats.
- Exposes commands or actions that the view can invoke.

Data binding
------------

Bindings update the UI when model data changes, and optionally update the model
when the user edits the UI. This reduces glue code but requires careful state
management.

Benefits
--------

- Strong separation between view and logic.
- Easier to test view-model behavior.
- Reduced UI boilerplate.

Tradeoffs
---------

- Overuse of bindings can make data flow hard to trace.
- View-models can become too large without clear boundaries.

Applied to target setting
-------------------------

A view-model might expose:

- A list of waypoints as UI-friendly points.
- A selected waypoint index.
- Commands for send, edit, and return actions.

This allows the view to remain simple and focused on rendering and input.
