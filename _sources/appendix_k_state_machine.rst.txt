Appendix K: State Machine
=========================

Overview
--------

A state machine models a system with a finite number of modes. Each state has
well-defined behavior and transitions that occur on events or conditions.

Key terms
---------

- State: a named mode of operation.
- Transition: a change from one state to another.
- Guard: a condition that must be true for a transition.
- Action: logic executed on entry, exit, or during a state.

Design guidelines
-----------------

- Keep states orthogonal: one reason to change.
- Prefer explicit transitions over implicit side effects.
- Log transitions for debugging.

Hierarchical state machines
---------------------------

Nested states allow shared behavior at higher levels. This reduces duplication
when multiple states share common logic.

Applied to navigation
---------------------

The navigation pipeline can be modeled as:

- IDLE: waiting for a waypoint.
- NAVIGATING: moving toward a target.
- EDIT: applying a waypoint update.
- PAUSED: holding position.
- RETURNING: going back to a visited waypoint.

This structure simplifies reasoning about behavior and failure handling.
