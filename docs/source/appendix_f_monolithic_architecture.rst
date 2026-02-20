Appendix F: Monolithic Architecture
===================================

Overview
--------

A monolithic architecture bundles application components into a single deployable
unit. This contrasts with microservices or distributed components.

Benefits
--------

- Simple deployment and debugging.
- No network overhead between internal modules.
- Easier to maintain transaction boundaries.

Drawbacks
---------

- Tightly coupled components reduce flexibility.
- Scaling requires duplicating the entire system.
- Large codebases can slow development without strong modularity.

Modular monolith
----------------

A modular monolith preserves a single deployment but enforces internal module
boundaries. This approach often provides the best of both worlds when the
system does not require independent scaling.

Applied to robotics tooling
---------------------------

A standalone UI app can be treated as a monolith with clear internal modules
for networking, input handling, rendering, and data persistence. This keeps
deployment simple while still enabling maintainability.
