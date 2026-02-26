Appendix B: MVC Architecture
============================

Introduction
------------

Conceptual foundation of MVC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Model-View-Controller (MVC) is an architectural pattern developed to address a fundamental structural problem in software engineering: the uncontrolled mixing of data management, presentation logic, and control flow. At its most basic level, MVC divides an application into three interacting components — the Model, the View, and the Controller — but the importance of this division lies not in taxonomy, but in responsibility control.

In many early-stage implementations, developers tend to write code in a way that mirrors immediate functionality. A button click might validate data, update system state, call a hardware function, and update the display — all within the same method. While this appears efficient in small systems, such entanglement scales poorly. The resulting architecture exhibits high coupling and low cohesion, making modification increasingly risky as the system grows.

MVC addresses this by enforcing a deliberate separation:

- The **Model** owns system state and business logic
- The **View** is responsible for presenting information
- The **Controller** mediates interaction between the two

This structural separation became widely adopted in large-scale frameworks such as Django and ASP.NET MVC precisely because long-term maintainability demands architectural discipline. MVC is therefore not merely a coding style; it is a strategy for managing complexity over time.

Why Separation is architecturally necessary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To understand the necessity of MVC, consider a simplified Android example in which a movement button directly manipulates robot state:

.. code-block:: java

    moveButton.setOnClickListener(v -> {
        if (batteryLevel > 10) {
            robot.moveForward();
            batteryLevel -= 5;
            batteryText.setText("Battery: " + batteryLevel);
        }
    });

At first glance, this implementation appears straightforward. However, several structural problems emerge:

- Battery validation logic is embedded in the UI layer
- Domain state is directly modified by presentation code
- Hardware commands are triggered from within a UI callback
- Display updates are interwoven with business logic

This design increases coupling across unrelated concerns. If battery rules change, the UI must be modified. If hardware behavior changes, UI code must be updated. If the interface is redesigned, domain logic risks accidental modification. The architecture lacks clear boundaries.

MVC restructures this situation by isolating responsibilities. Instead of allowing the View to manipulate state directly, it forwards input to a Controller, which delegates domain logic to the Model. This indirection may appear unnecessary in small examples, but in larger systems — especially distributed or safety-sensitive systems — it significantly reduces systemic fragility.

Core concepts
-------------

The Model: authority, integrity, and cohesion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Model is not simply a data container; it is the authoritative representation of domain knowledge. Its purpose is to maintain state consistently and enforce invariants. In a robotic system, invariants might include battery limits, safety constraints, or operational states such as emergency stop.

Consider the following example:

.. code-block:: java

    public class RobotState {
        private int batteryLevel = 100;

        public boolean canMove() {
            return batteryLevel > 10;
        }

        public void consumeBattery(int amount) {
            if (batteryLevel - amount < 0) {
                throw new IllegalStateException("Battery depleted");
            }

            batteryLevel -= amount;
        }

        public int getBatteryLevel() {
            return batteryLevel;
        }
    }

In this implementation, all battery-related logic resides within the Model. This centralization has several architectural implications.

First, it increases cohesion. All behavior related to battery management is encapsulated in one module. Second, it reduces duplication; validation logic is written once rather than scattered across multiple UI handlers. Third, it enhances testability. The Model can be tested independently of Android or ROS2 frameworks.

Invariant centralization improves correctness guarantees. When validation is distributed, inconsistencies are likely. When centralized, the Model becomes the single source of truth. In robotics, where state integrity affects safety, this centralization is not merely beneficial — it is essential.

The View: representation without decision authority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The View is responsible for rendering information and capturing user input, but it intentionally lacks decision-making authority regarding domain rules. This restriction may appear limiting, yet it is critical for architectural stability.

For example:

.. code-block:: java

    batteryText.setText("Battery: " + robotState.getBatteryLevel());

    moveButton.setOnClickListener(v -> {
        controller.onMoveRequested();
    });

Here, the View displays state retrieved from the Model and forwards input to the Controller. It does not decide whether the robot can move; it merely delegates that responsibility.

The argument for limiting View authority lies in change volatility. User interfaces change frequently due to usability improvements, layout redesigns, or platform evolution. If domain logic is embedded in the View, every UI modification risks altering system behavior. By isolating presentation from logic, MVC reduces change propagation and increases maintainability.

This separation aligns with principles of low coupling and high cohesion, ensuring that aesthetic or usability changes do not destabilize system rules.

The Controller: coordination without ownership
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Controller functions as a mediator. It receives user input from the View, invokes operations on the Model, and updates the View accordingly.

.. code-block:: java

    public void onMoveRequested() {
        if (robotState.canMove()) {
            robotState.consumeBattery(5);
            robot.moveForward();
            View.updateBattery(robotState.getBatteryLevel());
        }
    }

The Controller does not enforce battery rules independently; it delegates that responsibility to the Model. Its role is coordination, not ownership.

However, Controllers are often the most vulnerable component in MVC. Developers may gradually accumulate logic within them, leading to "fat Controllers." When Controllers begin implementing validation, managing persistent state, or performing domain computations, the separation collapses.

Thus, MVC requires disciplining. The Controller must remain a mediator, not an alternative domain layer.

Interaction flow and dependency direction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MVC establishes a clear flow of interaction:

- The View captures user input
- The Controller interprets the request
- The Model performs state updates
- The Controller updates the View

Critically, the Model does not depend on the View. This unidirectional dependency structure prevents circular references and preserves independence from presentation frameworks.

In distributed Android-ROS2 systems, this separation has practical implications. The Model can represent robot state independent of Android lifecycle events. Network disruptions affect coordination logic but not domain integrity. UI crashes do not compromise robotic safety rules.

Architecturally, this improves fault isolation and resilience.

Analysis
--------

While MVC improves structural clarity, it is not without cost.

First, it introduces additional abstraction layers. Small projects may perceive this as unnecessary overhead. The architectural benefit emerges primarily in systems of moderate or large complexity. Thus, MVC represents a trade-off between immediate simplicity and long-term maintainability.

Second, the reliance on Controllers as coordination hubs introduces a risk of logic centralization. Without careful boundary enforcement, Controllers may grow excessively complex. This risk must be mitigated through disciplined design practices.

Third, unlike reactive frameworks such as React, traditional MVC requires explicit updates to the View. This increases verbosity but provides transparency. The trade-off is between automated reactivity and explicit control.

Finally, additional abstraction layers may introduce minor performance overhead. In robotics systems where latency matters, this must be considered. However, coupling UI directly to hardware for micro-optimizations would undermine safety and maintainability. In safety-critical environments, architectural integrity outweighs marginal performance gains.
