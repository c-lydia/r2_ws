Appendix A: Object-Oriented Programming
=======================================

Overview
--------

Object-oriented programming (OOP) models software as interacting objects that
encapsulate state and behavior. The goal is to make programs easier to reason
about by grouping related data and functions and enforcing clear boundaries.

Core concepts
-------------

Classes and objects
^^^^^^^^^^^^^^^^^^^

- A class defines a blueprint for data (fields) and behavior (methods).
- An object is an instance of a class created at runtime.

Encapsulation
^^^^^^^^^^^^^

- Hide internal details and expose a minimal public interface.
- Prevents accidental misuse and reduces coupling.

Abstraction
^^^^^^^^^^^

- Present only essential features and ignore implementation details.
- Encourages focusing on what an object does, not how it does it.

Inheritance
^^^^^^^^^^^

- A subclass derives from a base class and can extend or override behavior.
- Supports reuse but can introduce tight coupling if overused.

Polymorphism
^^^^^^^^^^^^

- Code can work with objects through a shared interface.
- Allows different implementations to be swapped with minimal changes.

Composition over inheritance
----------------------------

Composition builds complex behavior by combining smaller objects, which helps
avoid fragile inheritance hierarchies. When possible, prefer composition and
interfaces to keep dependencies explicit.

SOLID principles
----------------

- Single Responsibility: one reason to change.
- Open/Closed: open for extension, closed for modification.
- Liskov Substitution: subclasses must be usable where base classes are expected.
- Interface Segregation: small, focused interfaces.
- Dependency Inversion: depend on abstractions, not concrete types.

Design patterns
---------------

Common patterns that align with OOP:

- Strategy: swap algorithms without changing the caller.
- Observer: notify subscribers on state changes.
- Command: encapsulate an action as an object.
- Factory: centralize object creation.

Typical pitfalls
----------------

- Deep inheritance hierarchies that obscure behavior.
- God objects that violate single responsibility.
- Exposing internal state directly, making invariants hard to enforce.

Applied to robotics software
----------------------------

In robotics systems, OOP helps isolate concerns like communication, control,
and sensing. For example:

- A network manager can encapsulate UDP send/receive behavior.
- A controller class can wrap control logic and state updates.
- A UI layer can treat the model as a stable interface and remain decoupled
  from data sources.

Example: interface-driven control
---------------------------------

.. code-block:: python

   class VelocityController:
       def compute(self, target, state):
           raise NotImplementedError

   class PDController(VelocityController):
       def compute(self, target, state):
           # PD math here
           return vx, vy, wz

   def step(controller, target, state):
       return controller.compute(target, state)

This keeps the control pipeline stable while allowing multiple controllers to
be used during testing or future upgrades.
