Appendix B: MVC Architecture
============================

Overview
--------

Model-View-Controller (MVC) separates data, presentation, and user input into
three roles. This separation improves maintainability by reducing coupling.

Roles
-----

Model
^^^^^

- Owns the application state and business rules.
- Exposes operations that modify data in a controlled way.

View
^^^^

- Renders the model state to the user.
- Should be mostly passive and not contain business logic.

Controller
^^^^^^^^^^

- Interprets user input and updates the model.
- Chooses which view to refresh or navigate to.

Typical flow
------------

1. User interacts with the View.
2. Controller translates the action into model updates.
3. Model updates its state and notifies views.
4. View re-renders using the new model state.

Benefits
--------

- Clear separation of responsibilities.
- Easier testing of logic by isolating the model.
- Views can be swapped without changing the model.

Tradeoffs
---------

- Controllers can grow large if not structured.
- Requires discipline to keep business logic in the model.

Applied to a robotics UI
------------------------

In a waypoint-setting UI:

- Model holds the waypoint list, active target, and plan ID.
- View renders the field, robot position, and waypoint markers.
- Controller translates touch events into model updates and network sends.

Implementation hint
-------------------

Use small controllers to handle independent features (e.g., waypoint editing,
return-to-base). This avoids a single controller that becomes a bottleneck.
