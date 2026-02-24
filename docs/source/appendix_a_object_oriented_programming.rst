Appendix A: Object-Oriented Programming
=======================================

Introduction
------------

Object-oriented programming (OOP) addresses limitations of procedural paradigms when managing complexity in larger systems. While procedural programming organizes code around functions, OOP organizes code around objects, which encapsulate data (attributes) and behavior (methods). This approach promotes:

- **Modular design:** objects serve as self-contained modules
- **Code reuse:** inheritance and composition enable reuse of behavior
- **Data safety:** encapsulation helps protect internal state
- **Scalability:** modular components can be extended or replaced without affecting the whole system
- **Natural modeling:** objects map naturally to real-world entities, making designs easier to reason about


Historical influences
^^^^^^^^^^^^^^^^^^^^^

OOP has evolved through decades of research and language design:

- **Simula (1960s):** introduced classes and objects
- **Smalltalk (1970s):** popularized OOP concepts, including message passing and dynamic typing
- **C++ (1980s):** extended C with classes, inheritance, and polymorphism
- **Java (1990s):** designed as an OOP language emphasizing portability and safety
- **Python (1990s):** supports multiple paradigms, including OOP, with a dynamic type system
- **C# (2000s):** modern OOP language integrated with the ``.NET`` framework

Core OOP principles
^^^^^^^^^^^^^^^^^^^

- **Encapsulation:** bundle data and the methods that operate on it in a single unit (class), and restrict access to internal components when appropriate.
- **Inheritance:** create new classes based on existing ones to enable reuse and extension.
- **Polymorphism:** treat different classes uniformly through a common interface (method overriding, interfaces, or duck typing).
- **Abstraction:** expose only the necessary features of an object while hiding implementation details.

OOP aligns with design principles such as SOLID and common design patterns (singleton, factory, observer), which formalize reusable solutions to recurrent design problems.

Type systems and object models
-------------------------------

OOP languages differ by type system and object model:

- **Class-based vs. Prototype-based:** class-based languages use classes as blueprints; prototype-based languages (e.g., JavaScript) create objects from other objects.
- **Static vs. Dynamic typing:** static typing requires compile-time type information; dynamic typing resolves types at runtime.
- **Single vs. Multiple inheritance:** some languages (Java, C#) restrict class inheritance to a single parent but allow interfaces; others (C++, Python) support multiple inheritance.
- **Interface-based vs. Class-based polymorphism:** languages use interfaces, virtual methods, or duck typing to achieve polymorphism.
- **Memory management:** some languages (C++) require explicit memory management; others (Java, Python, JavaScript) use automatic garbage collection.

Language-specific notes
^^^^^^^^^^^^^^^^^^^^^^^

- **Java:** strong encapsulation, robust type system, single class inheritance with interfaces, automatic garbage collection.
- **C++:** manual and RAII-style resource management options, multiple inheritance, fine-grained control over performance.
- **Python:** dynamic typing, multiple inheritance, flexible object model, garbage-collected.
- **JavaScript:** prototype-based, dynamic typing, flexible object creation and modification.
- **C#:** modern language features, strong typing, single inheritance with interfaces, integrated with ``.NET``.

Object model differences
^^^^^^^^^^^^^^^^^^^^^^^^

The object model affects how objects are created and interact. For example:
- Java: class-based instantiation, garbage collection, single inheritance with interfaces for polymorphism.
- C++: class-based, manual or RAII-managed resources, multiple inheritance.
- Python: class-based, dynamic typing, multiple inheritance, runtime flexibility.
- JavaScript: prototype-based, dynamic object composition and modification.

Scope of this appendix
----------------------

This appendix focuses on practical OOP guidance relevant to this project:

- ROS2 nodes implemented in Python (Jetson)
- Android app components implemented in Java

We emphasize:

- structuring classes for modular, reusable components
- designing maintainable and extensible class hierarchies
- applying OOP principles to manage robot subsystems

C++ and JavaScript OOP concepts are not covered in detail here.

Foundational OOP concepts
-------------------------

Class
^^^^^

A class is a template for objects. It defines attributes (state) and methods (behavior). Classes enable modular design and reuse.

.. code-block:: python

    class MotorController:
        def __init__(self, motor_id):
            self.motor_id = motor_id
            self.speed = 0

        def set_speed(self, speed):
            self.speed = speed

.. code-block:: java

    public class MotorController {
        private int motorId;
        private int speed;

        public MotorController(int motorId) {
            this.motorId = motorId;
            this.speed = 0;
        }

        public void setSpeed(int speed) {
            this.speed = speed;
        }
    }

Object
^^^^^^

An object is an instance of a class with its own state and behavior.

.. code-block:: python

    motor1 = MotorController(1)
    motor2 = MotorController(2)

    motor1.set_speed(100)
    motor2.set_speed(150)

.. code-block:: java

    MotorController motor1 = new MotorController(1);
    MotorController motor2 = new MotorController(2);

    motor1.setSpeed(100);
    motor2.setSpeed(150);

Attributes
^^^^^^^^^^

Attributes define an object's state.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id
            self.value = 0

.. code-block:: java

    public class Sensor {
        private int sensorId;
        private int value;

        public Sensor(int sensorId) {
            this.sensorId = sensorId;
            this.value = 0;
        }
    }

- Prefer restricting direct access to attributes (private/protected) when appropriate to enforce invariants and reduce coupling.
- Use getters/setters or properties to control and validate updates to internal state.

Methods
^^^^^^^

Methods define behavior and operate on an object's state.

.. code-block:: python

    class WaypointNavigator:
        def __init__(self):
            self.waypoints = []

        def add_waypoint(self, x, y):
            self.waypoints.append((x, y))

.. code-block:: java

    public class WaypointNavigator {
        private List<Point> waypoints;
        public WaypointNavigator() {
            this.waypoints = new ArrayList<>();
        }
    }

Methods encapsulate operations on internal state and support interaction between objects.

Instance and class members
^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Instance members** belong to individual objects.
- **Class members** (static/class variables) are shared across all instances.

.. code-block:: python

    class Robot:
        total_robots = 0  # class variable

        def __init__(self, name):
            self.name = name  # instance variable
            Robot.total_robots += 1

        @classmethod
        def get_total_robots(cls):
            return cls.total_robots

.. code-block:: java

    public class Robot {
        private static int totalRobots = 0; // class variable
        private String name; // instance variable

        public Robot(String name) {
            this.name = name;
            totalRobots++;
        }

        public static int getTotalRobots() {
            return totalRobots;
        }
    }

Object state and behavior
^^^^^^^^^^^^^^^^^^^^^^^^^

- State is defined by attributes; behavior is defined by methods that operate on that state.

.. code-block:: python

    motor1 = MotorController(1)
    motor1.set_speed(100)  # Changes motor1's state

.. code-block:: java

    MotorController motor1 = new MotorController(1);
    motor1.setSpeed(100); // Changes motor1's state

Message passing
^^^^^^^^^^^^^^^

Objects interact by calling methods on one another. This keeps components decoupled and promotes clear interfaces.

.. code-block:: python

    class SensorManager:
        def __init__(self):
            self.sensors = []

        def add_sensor(self, sensor):
            self.sensors.append(sensor)

        def read_all_sensors(self):
            return [sensor.value for sensor in self.sensors]

.. code-block:: java

    public class SensorManager {
        private List<Sensor> sensors;
        public SensorManager() {
            this.sensors = new ArrayList<>();
        }
        public void addSensor(Sensor sensor) {
            this.sensors.add(sensor);
        }
        public List<Integer> readAllSensors() {
            List<Integer> values = new ArrayList<>();
            for (Sensor sensor : sensors) {
                values.add(sensor.getValue());
            }
            return values;
        }
    }

Core concepts
-------------

This section covers encapsulation, inheritance, polymorphism, and abstraction with practical guidance for ROS2 (Python) and Android (Java) components.

Encapsulation
^^^^^^^^^^^^^

Encapsulation protects an object's internal state and exposes a minimal, well-documented interface. Use access modifiers (Java) or naming conventions/properties (Python) to enforce invariants and validate inputs in setter methods or properties.

.. code-block:: python

    class MotorController:
        def __init__(self, motor_id):
            self._motor_id = motor_id
            self._speed = 0

        def set_speed(self, speed):
            if speed < 0:
                raise ValueError("speed must be non-negative")
            self._speed = speed

        def get_speed(self):
            return self._speed

.. code-block:: java

    public class MotorController {
        private final int motorId;
        private int speed;

        public MotorController(int motorId) {
            this.motorId = motorId;
            this.speed = 0;
        }

        public void setSpeed(int speed) {
            if (speed < 0) throw new IllegalArgumentException("speed must be non-negative");
            this.speed = speed;
        }

        public int getSpeed() {
            return this.speed;
        }
    }

Benefits
~~~~~~~~

- prevents invalid state transitions
- reduces coupling between components
- simplifies testing and reasoning about behavior

Abstraction
^^^^^^^^^^^

Abstraction exposes only the information needed by clients. Keep complex algorithms behind a simple method or interface and document expected behavior, side effects, and performance characteristics.

.. code-block:: python

    class Robot:
        def move_to(self, x, y):
            """High-level API: performs path planning and motor control internally."""
            # Implementation details hidden
            pass

.. code-block:: java

    public class Robot {
        public void moveTo(int x, int y) {
            // High-level API; internal planning and actuation hidden
        }
    }

Inheritance
^^^^^^^^^^^

Use inheritance to express an "is-a" relationship. Prefer composition over inheritance when behavior can be composed from smaller components. Avoid deep inheritance chains; prefer small, well-defined base classes or interfaces.

.. code-block:: python

    class Vehicle:
        def move(self):
            raise NotImplementedError

    class Robot(Vehicle):
        def move(self):
            # robot-specific movement
            pass

.. code-block:: java

    public class Vehicle {
        public void move() {
            // default or abstract behavior
        }
    }

Polymorphism
^^^^^^^^^^^^^

Polymorphism lets different implementations be treated through a common interface. Use interfaces (Java) or duck typing/abstract base classes (Python) to decouple consumers from concrete implementations.

.. code-block:: python

    class Sensor:
        def read_value(self):
            raise NotImplementedError

    class Temperature(Sensor):
        def read_value(self):
            return 25  # example value

    class Pressure(Sensor):
        def read_value(self):
            return 1013

.. code-block:: java

    public interface Sensor {
        int readValue();
    }

    public class Temperature implements Sensor {
        @Override
        public int readValue() {
            return 25; // example
        }
    }

    public class Pressure implements Sensor {
        @Override
        public int readValue() {
            return 1013;
        }
    }

Object lifecycle and structure
------------------------------

Construction and destruction of objects, as well as the structure of classes and their relationships, are fundamental aspects of OOP. We will discuss how to properly initialize objects using constructors, manage resources with destructors (where applicable), and design class hierarchies that promote maintainability and extensibility. We will also cover advanced OOP concepts such as method overloading, method overriding, dynamic binding, and design patterns that can be applied to our project to create a robust and scalable software architecture.

Constructor
^^^^^^^^^^^

A constructor is a special method used to initialize objects when they are created. It typically sets up the initial state of the object by assigning values to its attributes.

.. code-block:: python

    class Robot:
        def __init__(self, name):
            self.name = name  # Initialize the robot's name
            self.position = (0, 0)  # Initialize the robot's position

.. code-block:: java

    public class Robot {
        private String name; // Robot's name
        private Point position; // Robot's position

        public Robot(String name) {
            this.name = name; // Initialize the robot's name
            this.position = new Point(0, 0); // Initialize the robot's position
        }
    }

.. tip:: 

    - Keep constructors lightweight; avoid long-running operations
    - Initialize all critical attributes to a known state
    - In ROS2, avoid ROS communications in constructors; use a separate ``initialize()`` method if needed

Destructor
^^^^^^^^^^

A destructor is a special method that is called when an object is destroyed or goes out of scope. It is used to perform cleanup operations, such as releasing resources or closing connections.

.. code-block:: python

    class Robot:
        def __del__(self):
            # Perform cleanup operations, such as closing connections
            pass

Python uses garbage collection to manage memory, so destructors are not commonly used. However, you can define a ``__del__`` method to perform cleanup if necessary.

Java has a garbage collector that automatically manages memory, so it does not have a destructor like C++. Instead, you can use the ``finalize`` method or implement the ``AutoCloseable`` interface for resource management. However, relying on ``finalize`` is generally discouraged in Java due to unpredictability, and using ``AutoCloseable`` with try-with-resources is the recommended approach for managing resources.

Constructor overloading
^^^^^^^^^^^^^^^^^^^^^^^

Constructor overloading allows a class to have multiple constructors with different parameter lists. This provides flexibility in object instantiation, allowing objects to be created with different initial states.

.. code-block:: python

    class Robot:
        def __init__(self, name, position=(0, 0)):
            self.name = name
            self.position = position

.. code-block:: java

    public class Robot {
        private String name;
        private Point position; 

        public Robot(String name) {
            this.name = name;
            this.position = new Point(0, 0);
        }

        public Robot(String name, Point position) {
            this.name = name;
            this.position = position;
        }
    }   

Copy constructor
^^^^^^^^^^^^^^^^

Copy constructors allow for the creation of a new object as a copy of an existing object. This is particularly useful when you want to create a new instance with the same state as an existing instance.

.. code-block:: python

    import copy

    motor2 = copy.deepcopy(motor1)  # Create a deep copy of motor1

.. code-block:: java

    public MotorController(MotorController original) {
        this.motorId = original.motorId;
        this.speed = original.speed;
    }

.. attention:: 

    - In Python, use the ``copy`` module for shallow and deep copying of objects.
    - In Java, implement a copy constructor or use the ``Cloneable`` interface for object copying. Be cautious with mutable objects to avoid unintended side effects.

Initialization block
^^^^^^^^^^^^^^^^^^^^

Java supports initialization blocks, which are used to initialize instance variables. They are executed when an instance of the class is created, before the constructor is called. This can be useful for common initialization code that is shared across multiple constructors.

.. code-block:: java

    public class Robot {
        private String name;
        private Point position;

        // Initialization block
        {
            this.position = new Point(0, 0); // Default position for all robots
        }

        public Robot(String name) {
            this.name = name; // Initialize the robot's name
        }

        public Robot(String name, Point position) {
            this.name = name; // Initialize the robot's name
            this.position = position; // Override default position if provided
        }
    }

Object instantiation
^^^^^^^^^^^^^^^^^^^^

Object instantiation is the process of creating an instance of a class. In Python, this is done by calling the class as if it were a function, which invokes the constructor to initialize the object. In Java, you use the ``new`` keyword followed by the class name and parentheses to create a new instance.

.. code-block:: python

    robot1 = Robot("Robo1")  # Create a new Robot instance with name "Robo1"
    robot2 = Robot("Robo2", (10, 10))  # Create a new Robot instance with name "Robo2" and position (10, 10)

.. code-block:: java

    Robot robot1 = new Robot("Robo1"); // Create a new Robot instance with name "Robo1"
    Robot robot2 = new Robot("Robo2", new Point(10, 10)); // Create a new Robot instance with name "Robo2" and position (10, 10)

Memory allocation
^^^^^^^^^^^^^^^^^

In Python, memory allocation for objects is handled automatically by the Python memory manager and garbage collector. When an object is created, memory is allocated for it on the heap, and when it is no longer needed, the garbage collector will free that memory.

Keywork and modifiers
---------------------

``this`` or ``self`` keyword
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``this`` in Java and ``self`` in Python refer to the current instance of the class. They are used to access instance variables and methods from within the class.

``super`` keyword
^^^^^^^^^^^^^^^^^

The ``super`` keyword is used in subclasses to refer to the superclass. It allows you to call methods and access attributes of the superclass, which is particularly useful when overriding methods.

.. code-block:: python

    class AdvancedRobot(Robot):
        def __init__(self, name, position=(0, 0), sensors=[]):
            super().__init__(name, position)  # Call the superclass constructor
            self.sensors = sensors  # Additional attribute for AdvancedRobot

.. code-block:: java

    public class AdvancedRobot extends Robot {
        private List<Sensor> sensors;
        public AdvancedRobot(String name, Point position, List<Sensor> sensors) {
            super(name, position); // Call the superclass constructor
            this.sensors = sensors; // Additional attribute for AdvancedRobot
        }
    }

Access modifiers
^^^^^^^^^^^^^^^^

- **Public:** accessible from anywhere
- **Private:** accessible only within the class
- **Protected:** accessible within the class and its subclasses

In Python, there are no strict access modifiers, but by convention, a single underscore prefix (e.g., ``_attribute``) indicates that an attribute is intended for internal use (``protected``), while a double underscore prefix (e.g., ``__attribute``) triggers name mangling to make it harder to access from outside the class (``private``).

In Java, you can use the   ``public``, ``private``, and ``protected`` keywords to control access to class members. Additionally, Java has a default (package-private) access level when no modifier is specified, which allows access within the same package.

``final`` or ``const`` keyword
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``final`` keyword in Java and the ``const`` keyword in C++ are used to indicate that a variable's value cannot be changed once it has been assigned. In Java, you can declare a variable as ``final`` to make it a constant, and in C++, you can use ``const`` to achieve the same effect. This is useful for defining constants or ensuring that certain values remain unchanged throughout the program.

In Python, there is no built-in keyword for constants, but by convention, variables that are meant to be constants are typically defined in uppercase letters (e.g., ``PI = 3.14``) to indicate that they should not be modified.

``abstract`` keyword
^^^^^^^^^^^^^^^^^^^^

The ``abstract`` keyword is used in Java to declare a class as abstract, which means that it cannot be instantiated on its own and must be subclassed. An abstract class can contain abstract methods, which are declared without an implementation and must be implemented by subclasses. This allows for defining a common interface for a group of related classes while allowing each subclass to provide its own specific implementation.

.. code-block:: java

    public abstract class Shape {
        public abstract double area(); // Abstract method to be implemented by subclasses
    }

    public class Circle extends Shape {
        private double radius;
        public Circle(double radius) {
            this.radius = radius;
        }
        @Override
        public double area() {
            return Math.PI * radius * radius; // Implementation of the abstract method
        }
    }

In Python, you can achieve similar functionality using the ``abc`` module to create abstract base classes and abstract methods.

.. code-block:: python

    from abc import ABC, abstractmethod

    class Shape(ABC):
        @abstractmethod
        def area(self):
            pass  # Abstract method to be implemented by subclasses

    class Circle(Shape):
        def __init__(self, radius):
            self.radius = radius

        def area(self):
            return 3.14 * self.radius * self.radius  # Implementation of the abstract method

``virtual`` keyword
^^^^^^^^^^^^^^^^^^^

The ``virtual`` keyword is used in C++ to indicate that a method can be overridden in a derived class. This allows for dynamic dispatch, where the method that gets called is determined at runtime based on the actual type of the object, rather than the type of the reference. This is a key feature of polymorphism in C++.

In Python and Java, all methods are virtual by default, meaning they can be overridden in subclasses without needing a specific keyword. However, in Java, you can use the ``final`` keyword to prevent a method from being overridden.

Relationships between classes
-----------------------------

A class can have a relationship with another class, such as association, aggregation, composition, dependency, realization, and generalization. These relationships define how classes interact with each other and how they are structured in a class hierarchy. We will discuss these relationships in detail and provide examples of how they are used in our project to create a well-designed and maintainable codebase.

Association
^^^^^^^^^^^

Association is a relationship between two classes where one class uses or interacts with another class. It represents a "has-a" relationship, where one class contains a reference to another class.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id

    class Robot:
        def __init__(self, name):
            self.name = name
            self.sensor = Sensor(1)  # Robot has a Sensor (association)

.. code-block:: java

    public class Sensor {
        private int sensorId;
        public Sensor(int sensorId) {
            this.sensorId = sensorId;
        }
    }

    public class Robot {
        private String name;
        private Sensor sensor; // Robot has a Sensor (association)

        public Robot(String name) {
            this.name = name;
            this.sensor = new Sensor(1); // Initialize the sensor
        }
    }

Aggregation
^^^^^^^^^^^

Aggregation is a special form of association that represents a "whole-part" relationship, where one class (the whole) contains another class (the part), but the part can exist independently of the whole.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id

    class Robot:
        def __init__(self, name, sensor):
            self.name = name
            self.sensor = sensor  # Robot has a Sensor (aggregation)

.. code-block:: java

    public class Sensor {
        private int sensorId;
        public Sensor(int sensorId) {
            this.sensorId = sensorId;
        }
    }  

    public class Robot {
        private String name;
        private Sensor sensor; // Robot has a Sensor (aggregation)

        public Robot(String name, Sensor sensor) {
            this.name = name;
            this.sensor = sensor; // Initialize the sensor
        }
    }

Composition
^^^^^^^^^^^

Composition is a stronger form of aggregation that represents a "whole-part" relationship, where one class (the whole) contains another class (the part), and the part cannot exist independently of the whole.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id

    class Robot:
        def __init__(self, name):
            self.name = name
            self.sensor = Sensor(1)  # Robot has a Sensor (composition)

.. code-block:: java

    public class Sensor {
        private int sensorId;
        public Sensor(int sensorId) {
            this.sensorId = sensorId;
        }
    }

    public class Robot {
        private String name;
        private Sensor sensor; // Robot has a Sensor (composition)

        public Robot(String name) {
            this.name = name;
            this.sensor = new Sensor(1); // Initialize the sensor
        }
    }

Dependency
^^^^^^^^^^

Dependency is a relationship where one class depends on another class to function. It represents a "uses-a" relationship, where one class uses another class as part of its functionality.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id

    class Robot:
        def __init__(self, name):
            self.name = name

        def read_sensor(self, sensor):
            return sensor.sensor_id  # Robot uses Sensor (dependency)

.. code-block:: java

    public class Sensor {
        private int sensorId;
        public Sensor(int sensorId) {  
            this.sensorId = sensorId;
        }

    public class Robot {
        private String name;
        public Robot(String name) {
            this.name = name;
        }  

        public int readSensor(Sensor sensor) {
            return sensor.getSensorId(); // Robot uses Sensor (dependency)
        }
    }

Realization
^^^^^^^^^^^

Realization is a relationship where one class implements an interface defined by another class. It represents a "implements" relationship, where a class provides the implementation for the methods defined in an interface.

.. code-block:: java

    public interface Sensor {
        int readValue(); // Interface method
    }

    public class TemperatureSensor implements Sensor {
        @Override
        public int readValue() {
            // Return temperature reading
        }
    }

    public class PressureSensor implements Sensor {
        @Override
        public int readValue() {
            // Return pressure reading
        }
    }

In Python, you can achieve a similar effect using abstract base classes and the ``abc`` module to define interfaces and their implementations.

.. code-block:: python

    from abc import ABC, abstractmethod

    class Sensor(ABC):
        @abstractmethod
        def read_value(self):
            pass  # Interface method

    class TemperatureSensor(Sensor):
        def read_value(self):
            # Return temperature reading
            pass

Generalization
^^^^^^^^^^^^^^

Generalization is a relationship where one class is a more general version of another class. It represents an "is-a" relationship, where a subclass is a specialized version of a superclass.

.. code-block:: python

    class Vehicle:
        def move(self):
            pass

    class Robot(Vehicle):
        def move(self):
            # Implement robot-specific movement logic
            pass

.. code-block:: java

    public class Vehicle {
        public void move() {
            // General movement logic
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            // Implement robot-specific movement logic
        }
    }

Advanced concepts
-----------------

Method overloading
^^^^^^^^^^^^^^^^^^

Method overloading allows a class to have multiple methods with the same name but different parameter lists. This provides flexibility in how methods can be called and allows for different behaviors based on the input parameters.

.. code-block:: java

    public class Robot {
        public void move() {
            // Move with default behavior
        }

        public void move(int speed) {
            // Move with specified speed
        }

        public void move(int speed, int direction) {
            // Move with specified speed and direction
        }
    }

.. attention:: 

    - Python does not support method overloading in the same way as Java, but you can achieve similar functionality using default parameters or variable-length argument lists.
    - In Java, method overloading is determined at compile time based on the method signature, while in Python, you can use ``args`` and ``kwargs`` to create flexible methods that can handle different types and numbers of arguments.

Method overriding
^^^^^^^^^^^^^^^^^

Method overriding allows a subclass to provide a specific implementation of a method that is already defined in its superclass. This is a key feature of polymorphism, enabling subclasses to modify or extend the behavior of methods inherited from the superclass.

.. code-block:: python

    class Vehicle:
        def move(self):
            print("Vehicle is moving")

    class Robot(Vehicle):
        def move(self):
            print("Robot is moving")  # Override the move method

.. code-block:: java

    public class Vehicle {
        public void move() {
            System.out.println("Vehicle is moving");
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            System.out.println("Robot is moving"); // Override the move method
        }
    }

Dynamic binding
^^^^^^^^^^^^^^^

Dynamic binding, also known as late binding, is a mechanism where the method that gets called is determined at runtime based on the actual type of the object, rather than the type of the reference. This allows for more flexible and dynamic behavior in object-oriented programming.

.. code-block:: python

    class Vehicle:
        def move(self):
            print("Vehicle is moving")

    class Robot(Vehicle):
        def move(self):
            print("Robot is moving")

    def make_vehicle_move(vehicle):
        vehicle.move()  # Dynamic binding occurs here

    my_robot = Robot()
    make_vehicle_move(my_robot)  # Output: "Robot is moving"

.. code-block:: java

    public class Vehicle {
        public void move() {
            System.out.println("Vehicle is moving");
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            System.out.println("Robot is moving");
        }
    }

Late binding
^^^^^^^^^^^^

Late binding is a related concept to dynamic binding, where the method to be called is determined at runtime. In Java, this is achieved through the use of virtual methods, which are methods that can be overridden in subclasses. In Python, all methods are virtual by default, allowing for late binding without any special syntax.

.. code-block:: java

    public class Vehicle {
        public void move() {
            System.out.println("Vehicle is moving");
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            System.out.println("Robot is moving");
        }
    }

    public class Main {
        public static void main(String[] args) {
            Vehicle myVehicle = new Robot(); // Upcasting to Vehicle
            myVehicle.move(); // Late binding occurs, output: "Robot is moving"
        }
    }

.. attention:: 

    - In Python, late binding is inherent to the language, so you can simply call methods on objects without worrying about the binding mechanism.
    - In Java, ensure that methods you want to be overridden are not declared as ``final``, and use the ``@Override`` annotation to indicate that a method is intended to override a superclass method for better readability and error checking.

Early binding
^^^^^^^^^^^^^

Early binding, also known as static binding, is a mechanism where the method that gets called is determined at compile time based on the type of the reference. This is typically used for static methods, private methods, and final methods in Java, which cannot be overridden.

.. code-block:: java

    public class Vehicle {
        public static void staticMove() {
            System.out.println("Vehicle is moving");
        }

        private void privateMove() {
            System.out.println("Vehicle is moving privately");
        }

        public final void finalMove() {
            System.out.println("Vehicle is moving finally");
        }
    }

    public class Robot extends Vehicle {
        // Cannot override staticMove, privateMove, or finalMove
    }

.. attention:: 

    - In Python, early binding is not a common concept due to the dynamic nature of the language, but you can achieve similar behavior by using static methods or by defining methods that are not intended to be overridden.
    - In Java, use static methods for behavior that should not be overridden, and use private methods for internal behavior that should not be accessible outside the class. Use final methods to prevent overriding while still allowing access to the method from subclasses.

Operator overloading
^^^^^^^^^^^^^^^^^^^^

Operator overloading allows you to define custom behavior for standard operators (e.g., ``+``, ``-``, ``*``, ``/``) when they are used with instances of your classes. This can make your classes more intuitive and easier to use.

.. code-block:: python

    class Vector:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __add__(self, other):
            return Vector(self.x + other.x, self.y + other.y)

.. code-block:: java

    public class Vector {
        private int x;
        private int y; 

        public Vector(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public Vector add(Vector other) {
            return new Vector(this.x + other.x, this.y + other.y);
        }
    }

Multiple inheritance
^^^^^^^^^^^^^^^^^^^^

Multiple inheritance allows a class to inherit from more than one superclass. This can lead to ambiguity and complexity, especially when the same method or attribute is defined in multiple superclasses, which is known as the "diamond problem". To avoid this issue, some languages like Java do not support multiple inheritance of classes but allow it through interfaces.

In Python, multiple inheritance is supported, but you should be cautious when using it to avoid the diamond problem. Python uses the C3 linearization algorithm to determine the method resolution order (MRO) when multiple inheritance is involved.

.. code-block:: python

    class A:
        def method(self):
            print("Method in A")

    class B(A):
        def method(self):
            print("Method in B")

    class C(A):
        def method(self):
            print("Method in C")

    class D(B, C):
        pass

    d = D()
    d.method()  # Output will depend on the MRO, typically "Method in B"

.. attention::

    - In Java, use interfaces to achieve multiple inheritance of behavior without the complications of multiple inheritance of state.
    - In Python, be mindful of the method resolution order (MRO) when using multiple inheritance, and consider using composition or mixins as alternatives if it leads to complex hierarchies.

Diamond problem
^^^^^^^^^^^^^^^

The diamond problem occurs in multiple inheritance when a class inherits from two classes that both inherit from a common superclass. This can lead to ambiguity when the subclass tries to access a method or attribute that is defined in the common superclass, as it may not be clear which version of the method or attribute should be used.

.. code-block:: python

    class A:
        def method(self):
            print("Method in A")

    class B(A):
        def method(self):
            print("Method in B")

    class C(A):
        def method(self):
            print("Method in C")

    class D(B, C):
        pass

    d = D()
    d.method()  # Output will depend on the MRO, typically "Method in B"

.. attention::

    - In Java, the diamond problem is avoided by not allowing multiple inheritance of classes. Instead, you can use interfaces to achieve similar functionality without the ambiguity.
    - In Python, be aware of the method resolution order (MRO) when using multiple inheritance, and consider using composition or mixins as alternatives if it leads to complex hierarchies that may cause the diamond problem.

Delegation
^^^^^^^^^^

Delegation is a design pattern where an object handles a request by delegating it to another object. This allows for flexible code reuse and can help to avoid issues with multiple inheritance.

.. code-block:: python

    class Engine:
        def start(self):
            print("Engine started")

    class Car:
        def __init__(self):
            self.engine = Engine()  # Car has an Engine (delegation)

        def start(self):
            self.engine.start()  # Delegate the start action to the Engine

.. code-block:: java

    public class Engine {
        public void start() {
            System.out.println("Engine started");
        }
    }   

    public class Car {
        private Engine engine; // Car has an Engine (delegation)

        public Car() {
            this.engine = new Engine(); // Initialize the engine
        }

        public void start() {
            this.engine.start(); // Delegate the start action to the Engine
        }
    }

Inner or netsted classes
^^^^^^^^^^^^^^^^^^^^^^^^

Inner or nested classes are classes defined within another class. They can be used to logically group classes that are only used in one place, to increase encapsulation, and to improve readability.

.. code-block:: java

    public class OuterClass {
        private String outerField;

        public OuterClass(String outerField) {
            this.outerField = outerField;
        }

        // Inner class
        public class InnerClass {
            public void display() {
                System.out.println("Outer field: " + outerField); // Accessing outer class field
            }
        }
    }

In Python, you can also define nested classes, but they are not commonly used and do not have the same level of access to the outer class's attributes as Java's inner classes.

.. code-block:: python

    class OuterClass:
        def __init__(self, outer_field):
            self.outer_field = outer_field

        class InnerClass:
            def display(self, outer_instance):
                print(f"Outer field: {outer_instance.outer_field}")  # Accessing outer class field

Abstraction mechanisms
----------------------

Abstract classes
^^^^^^^^^^^^^^^^

Abstract classes are classes that cannot be instantiated on their own and are meant to be subclassed. They can contain abstract methods, which are declared without an implementation and must be implemented by subclasses. This allows for defining a common interface for a group of related classes while allowing each subclass to provide its own specific implementation.

.. code-block:: java

    public abstract class Shape {
        public abstract double area(); // Abstract method to be implemented by subclasses
    }

    public class Circle extends Shape {
        private double radius;
        public Circle(double radius) {
            this.radius = radius;
        }
        @Override
        public double area() {
            return Math.PI * radius * radius; // Implementation of the abstract method
        }
    }

    public class Rectangle extends Shape {
        private double width;
        private double height;
        public Rectangle(double width, double height) {
            this.width = width;
            this.height = height;
        }
        @Override
        public double area() {
            return width * height; // Implementation of the abstract method
        }
    }

In Python, you can achieve similar functionality using the ``abc`` module to create abstract base classes and abstract methods.

.. code-block:: python

    from abc import ABC, abstractmethod

    class Shape(ABC):
        @abstractmethod
        def area(self):
            pass  # Abstract method to be implemented by subclasses

    class Circle(Shape):
        def __init__(self, radius):
            self.radius = radius

        def area(self):
            return 3.14 * self.radius * self.radius  # Implementation of the abstract method

    class Rectangle(Shape):
        def __init__(self, width, height):
            self.width = width
            self.height = height

        def area(self):
            return self.width * self.height  # Implementation of the abstract method

Interfaces
^^^^^^^^^^

An interface is a contract that defines a set of methods that a class must implement. It allows for defining a common interface for a group of related classes while allowing each class to provide its own specific implementation. In Java, interfaces are defined using the ``interface`` keyword, and classes implement interfaces using the ``implements`` keyword.

.. code-block:: java

    public interface Drawable {
        void draw(); // Interface method
    }

    public class Circle implements Drawable {
        @Override
        public void draw() {
            System.out.println("Drawing a circle"); // Implementation of the interface method
        }
    }

    public class Rectangle implements Drawable {
        @Override
        public void draw() {
            System.out.println("Drawing a rectangle"); // Implementation of the interface method
        }
    }

In Python, you can achieve a similar effect using abstract base classes and the ``abc`` module to define interfaces and their implementations.

.. code-block:: python

    from abc import ABC, abstractmethod

    class Drawable(ABC):
        @abstractmethod
        def draw(self):
            pass  # Interface method

    class Circle(Drawable):
        def draw(self):
            print("Drawing a circle")  # Implementation of the interface method

    class Rectangle(Drawable):
        def draw(self):
            print("Drawing a rectangle")  # Implementation of the interface method

Marker interface
^^^^^^^^^^^^^^^^

A marker interface is an interface that does not contain any methods or fields and is used to indicate that a class has a certain property or should be treated in a specific way. In Java, marker interfaces are often used to indicate that a class can be serialized, cloned, or is thread-safe.

.. code-block:: java

    public interface Serializable {
        // No methods, just a marker interface
    }

    public class MyClass implements Serializable {
        // This class can be serialized because it implements the Serializable marker interface
    }

In Python, there is no direct equivalent to marker interfaces, but you can achieve similar functionality using class decorators or by defining a base class that serves as a marker.

.. code-block:: python

    class Serializable:
        pass  # Marker class

    @Serializable
    class MyClass:
        # This class can be treated as serializable because it is decorated with the Serializable marker
        pass

Functional interface
^^^^^^^^^^^^^^^^^^^^

A functional interface is an interface that contains exactly one abstract method. It is used to represent a single function or behavior that can be passed around as an object. In Java, functional interfaces are often used in conjunction with lambda expressions to provide a concise way to implement the interface.

.. code-block:: java

    @FunctionalInterface
    public interface Runnable {
        void run(); // Single abstract method
    }

    public class MyRunnable implements Runnable {
        @Override
        public void run() {
            System.out.println("Running a task"); // Implementation of the functional interface method
        }
    }

In Python, you can achieve a similar effect using callable classes or by using the ``functools`` module to create function objects.

.. code-block:: python

    class Runnable:
        def __call__(self):
            print("Running a task")  # Implementation of the functional interface method

    my_runnable = Runnable()
    my_runnable()  # Output: "Running a task"

Object-oriented design concepts
-------------------------------

SOLID principles
^^^^^^^^^^^^^^^^

SOLID is an acronym for five design principles that help to create maintainable and scalable software. These principles are:

- **Single Responsibility Principle:** A class should have only one reason to change, meaning it should have only one responsibility or job.
- **Open-Closed Principle:** Software entities (classes, modules, functions, etc.) should be open for extension but closed for modification, meaning you should be able to add new functionality without changing existing code.
- **Liskov Substitution Principle:** Objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program, meaning that subclasses should be able to stand in for their superclasses without causing errors or unexpected behavior.
- **Interface Segregation Principle:** Clients should not be forced to depend on interfaces they do not use, meaning that interfaces should be specific to the needs of the clients that use them, rather than being general-purpose interfaces that may contain methods that are not relevant to all clients.
- **Dependency Inversion Principle:** High-level modules should not depend on low-level modules; both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions. This means that you should depend on interfaces or abstract classes rather than concrete implementations, which allows for more flexible and decoupled code.

Single responsibility principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Single responsibility principle states that a class should have only one reason to change, meaning it should have only one responsibility or job. This principle helps to create classes that are focused and easier to maintain, as changes to one responsibility will not affect other responsibilities. By adhering to this principle, you can create a more modular and cohesive codebase, where each class has a clear purpose and is easier to understand and modify when necessary. 

.. code-block:: python

    class Robot:
        def __init__(self, name):
            self.name = name

        def move(self):
            # Code for moving the robot
            pass

        def communicate(self):
            # Code for communicating with other robots
            pass

.. code-block:: java

    public class Robot {
        private String name;

        public Robot(String name) {
            this.name = name;
        }

        public void move() {
            // Code for moving the robot
        }

        public void communicate() {
            // Code for communicating with other robots
        }
    }

Open-closed principle
~~~~~~~~~~~~~~~~~~~~~

Open-closed principle states that software entities (classes, modules, functions, etc.) should be open for extension but closed for modification. This means that you should be able to add new functionality to a class without changing its existing code. By adhering to this principle, you can create a more flexible and maintainable codebase, as new features can be added without risking the introduction of bugs or breaking existing functionality. This can be achieved through the use of inheritance, interfaces, and composition, allowing you to extend the behavior of existing classes without modifying their code.

.. code-block:: python

    class Robot:
        def __init__(self, name):
            self.name = name

        def move(self):
            # Code for moving the robot
            pass

    class AdvancedRobot(Robot):
        def communicate(self):
            # Code for communicating with other robots
            pass

.. code-block:: java

    public class Robot {
        private String name;

        public Robot(String name) {
            this.name = name;
        }

        public void move() {
            // Code for moving the robot
        }
    }

    public class AdvancedRobot extends Robot {
        public AdvancedRobot(String name) {
            super(name);
        }

        public void communicate() {
            // Code for communicating with other robots
        }
    }

Liskov substitution principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Liskov substitution principle states that objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program. This means that subclasses should be able to stand in for their superclasses without causing errors or unexpected behavior. By adhering to this principle, you can create a more robust and flexible codebase, as subclasses can be used interchangeably with their superclasses, allowing for greater code reuse and easier maintenance. This can be achieved by ensuring that subclasses do not violate the expectations set by the superclass, such as maintaining the same method signatures, adhering to the same contracts, and not introducing side effects that would break the functionality of the superclass.

.. code-block:: python

    class Vehicle:
        def move(self):
            pass

    class Robot(Vehicle):
        def move(self):
            # Implement robot-specific movement logic
            pass

    def make_vehicle_move(vehicle):
        vehicle.move()  # This should work for both Vehicle and Robot instances

.. code-block:: java

    public class Vehicle {
        public void move() {
            // General movement logic
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            // Implement robot-specific movement logic
        }
    }

Interface segregation principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interface segregation principle states that clients should not be forced to depend on interfaces they do not use. This means that interfaces should be specific to the needs of the clients that use them, rather than being general-purpose interfaces that may contain methods that are not relevant to all clients. By adhering to this principle, you can create a more modular and maintainable codebase, as clients will only depend on the functionality they actually need, reducing coupling and increasing cohesion. This can be achieved by breaking down large interfaces into smaller, more specific interfaces that cater to the needs of different clients.

.. code-block:: java

    public interface Movable {
        void move(); // Interface for movement
    }

    public interface Communicable {
        void communicate(); // Interface for communication
    }

    public class Robot implements Movable, Communicable {
        @Override
        public void move() {
            // Implement movement logic
        }

        @Override
        public void communicate() {
            // Implement communication logic
        }
    }

In Python, you can achieve a similar effect using abstract base classes and the ``abc`` module to define specific interfaces for different functionalities. 

.. code-block:: python

    from abc import ABC, abstractmethod

    class Movable(ABC):
        @abstractmethod
        def move(self):
            pass  # Interface for movement

    class Communicable(ABC):
        @abstractmethod
        def communicate(self):
            pass  # Interface for communication

    class Robot(Movable, Communicable):
        def move(self):
            # Implement movement logic
            pass

        def communicate(self):
            # Implement communication logic
            pass

GRASP principles
^^^^^^^^^^^^^^^^

GRASP (General Responsibility Assignment Software Patterns) is a set of principles for assigning responsibilities to classes and objects in object-oriented design. These principles help to create a well-structured and maintainable codebase by guiding the design of classes and their interactions. The GRASP principles include:

- **Information Expert:** Assign responsibility to the class that has the necessary information to fulfill it.
- **Creator:** Assign responsibility to the class that creates instances of other classes.
- **Controller:** Assign responsibility to a class that represents the overall system or a use case scenario
- **Low Coupling:** Assign responsibilities in a way that minimizes the dependencies between classes.
- **High Cohesion:** Assign responsibilities in a way that keeps related behavior together and promotes a clear and focused design.
- **Polymorphism:** Use polymorphic behavior to handle variations in behavior based on the type of object.
- **Pure Fabrication:** Assign responsibilities to a class that does not represent a concept in the problem domain to achieve low coupling and high cohesion.
- **Indirection:** Assign responsibility to an intermediate class to mediate between other classes or to decouple them.
- **Protected Variations:** Assign responsibilities in a way that protects elements from variations in other elements, such as using interfaces or abstract classes to shield clients from changes in the implementation.

Information expert
~~~~~~~~~~~~~~~~~~

Information expert is a principle that suggests assigning responsibility to the class that has the necessary information to fulfill it. This means that the class that has the most relevant data or knowledge about a particular responsibility should be responsible for handling that responsibility. By following this principle, you can create a more cohesive and maintainable codebase, as responsibilities are assigned to classes that are best suited to handle them, reducing the need for unnecessary dependencies and improving the overall design of the system.

.. code-block:: python

    class Robot:
        def __init__(self, name, speed):
            self.name = name
            self.speed = speed  # Robot has the necessary information about its speed

        def move(self):
            # Use the speed information to move the robot
            pass

.. code-block:: java

    public class Robot {
        private String name;
        private int speed; // Robot has the necessary information about its speed

        public Robot(String name, int speed) {
            this.name = name;
            this.speed = speed;
        }

        public void move() {
            // Use the speed information to move the robot
        }
    }

Creator
~~~~~~~

Creator is a principle that suggests assigning responsibility to the class that creates instances of other classes. This means that if a class is responsible for creating an instance of another class, it should also be responsible for managing the lifecycle of that instance. By following this principle, you can create a more cohesive and maintainable codebase, as the responsibility for creating and managing objects is centralized in one place, reducing the need for unnecessary dependencies and improving the overall design of the system.

.. code-block:: python

    class Sensor:
        def __init__(self, sensor_id):
            self.sensor_id = sensor_id

    class Robot:
        def __init__(self, name):
            self.name = name
            self.sensor = Sensor(1)  # Robot creates and manages the Sensor instance

.. code-block:: java

    public class Sensor {
        private int sensorId;
        public Sensor(int sensorId) {
            this.sensorId = sensorId;
        }
    }

    public class Robot {
        private String name;
        private Sensor sensor; // Robot creates and manages the Sensor instance

        public Robot(String name) {
            this.name = name;
            this.sensor = new Sensor(1); // Initialize the sensor
        }
    }

Controller
~~~~~~~~~~

Controller is a principle that suggests assigning responsibility to a class that represents the overall system or a use case scenario. This means that a controller class should be responsible for handling the flow of control and coordinating the interactions between other classes in the system. By following this principle, you can create a more cohesive and maintainable codebase, as the controller class can serve as a central point of control for the system, reducing the need for unnecessary dependencies and improving the overall design of the system.

.. code-block:: python

    class RobotController:
        def __init__(self, robot):
            self.robot = robot

        def execute_move(self):
            # Coordinate the movement of the robot
            self.robot.move()

.. code-block:: java

    public class RobotController {
        private Robot robot;

        public RobotController(Robot robot) {
            this.robot = robot;
        }

        public void executeMove() {
            // Coordinate the movement of the robot
            this.robot.move();
        }
    }

Low coupling
~~~~~~~~~~~~

Low coupling is a principle that suggests assigning responsibilities in a way that minimizes the dependencies between classes. This means that classes should be designed to be as independent as possible, with minimal knowledge of each other's internal workings. By following this principle, you can create a more modular and maintainable codebase, as changes to one class will have minimal impact on other classes, reducing the risk of introducing bugs and making it easier to modify and extend the system in the future.

.. code-block:: python

    class Sensor:
        def read_value(self):
            pass

    class Robot:
        def __init__(self, sensor):
            self.sensor = sensor  # Robot depends on Sensor, but Sensor does not depend on Robot    

        def move(self):
            value = self.sensor.read_value()  # Robot uses Sensor, but Sensor is not tightly coupled to Robot

.. code-block:: java

    public class Sensor {
        public int readValue() {
            // Read sensor value
            return 0;
        }
    }

    public class Robot {
        private Sensor sensor; // Robot depends on Sensor, but Sensor does not depend on Robot

        public Robot(Sensor sensor) {
            this.sensor = sensor; // Initialize the sensor
        }

        public void move() {
            int value = this.sensor.readValue(); // Robot uses Sensor, but Sensor is not tightly coupled to Robot
        }
    }

High cohesion
~~~~~~~~~~~~~

High cohesion is a principle that suggests assigning responsibilities in a way that keeps related behavior together and promotes a clear and focused design. This means that classes should be designed to have a single, well-defined purpose, with all of their methods and attributes related to that purpose. By following this principle, you can create a more maintainable and understandable codebase, as classes with high cohesion are easier to understand, modify, and extend without affecting unrelated functionality. This can be achieved by grouping related methods and attributes together in the same class, and by avoiding the inclusion of unrelated functionality in a single class.

.. code-block:: python

    class Robot:
        def __init__(self, name):
            self.name = name

        def move(self):
            # Code for moving the robot
            pass

        def communicate(self):
            # Code for communicating with other robots
            pass

.. code-block:: java

    public class Robot {
        private String name;

        public Robot(String name) {
            this.name = name;
        }

        public void move() {
            // Code for moving the robot
        }

        public void communicate() {
            // Code for communicating with other robots
        }
    }

Polymorphism
~~~~~~~~~~~~

Polymorphism is a principle that allows objects of different classes to be treated as objects of a common superclass. This means that you can write code that works with objects of different types as long as they share a common interface or superclass. By following this principle, you can create a more flexible and maintainable codebase, as you can write code that is not dependent on specific implementations, allowing for greater code reuse and easier maintenance. This can be achieved through the use of inheritance, interfaces, and abstract classes, allowing you to define common behavior in a superclass or interface and have different subclasses provide their own specific implementations.

.. code-block:: python

    class Vehicle:
        def move(self):
            pass

    class Robot(Vehicle):
        def move(self):
            # Implement robot-specific movement logic
            pass

    def make_vehicle_move(vehicle):
        vehicle.move()  # This can work with any subclass of Vehicle, demonstrating polymorphism

.. code-block:: java

    public class Vehicle {
        public void move() {
            // General movement logic
        }
    }

    public class Robot extends Vehicle {
        @Override
        public void move() {
            // Implement robot-specific movement logic
        }
    }

    public class Main {
        public static void main(String[] args) {
            Vehicle myVehicle = new Robot(); // Upcasting to Vehicle
            myVehicle.move(); // This can work with any subclass of Vehicle, demonstrating polymorphism
        }
    }

Pure fabrication
~~~~~~~~~~~~~~~~

Pure fabrication is a principle that suggests assigning responsibilities to a class that does not represent a concept in the problem domain to achieve low coupling and high cohesion. This means that you can create a class that serves as a helper or utility class to handle responsibilities that do not fit well within the existing domain classes, allowing you to keep your domain classes focused and cohesive while still providing the necessary functionality. By following this principle, you can create a more maintainable and flexible codebase, as the pure fabrication class can be modified or extended without affecting the core domain classes, reducing the risk of introducing bugs and making it easier to adapt to changing requirements.

.. code-block:: python

    class SensorDataProcessor:
        @staticmethod
        def process_data(data):
            # Code for processing sensor data that does not fit well within the Robot class
            pass

    class Robot:
        def __init__(self, name):
            self.name = name

        def move(self):
            # Code for moving the robot
            pass

        def communicate(self):
            # Code for communicating with other robots
            pass

.. code-block:: java

    public class SensorDataProcessor {
        public static void processData(String data) {
            // Code for processing sensor data that does not fit well within the Robot class
        }
    }

    public class Robot {
        private String name;

        public Robot(String name) {
            this.name = name;
        }

        public void move() {
            // Code for moving the robot
        }

        public void communicate() {
            // Code for communicating with other robots
        }
    }

Indirection
~~~~~~~~~~~

Indirection is a principle that suggests assigning responsibility to an intermediate class to mediate between other classes or to decouple them. This means that you can create a class that serves as an intermediary between two or more classes, allowing them to interact without being directly dependent on each other. By following this principle, you can create a more flexible and maintainable codebase, as the indirection class can be modified or extended without affecting the classes it mediates between, reducing the risk of introducing bugs and making it easier to adapt to changing requirements. This can be achieved through the use of design patterns such as the mediator pattern, which provides a central point of control for interactions between classes, or the adapter pattern, which allows classes with incompatible interfaces to work together.

.. code-block:: python

    class Mediator:
        def __init__(self):
            self.robot = None
            self.sensor = None

        def set_robot(self, robot):
            self.robot = robot

        def set_sensor(self, sensor):
            self.sensor = sensor

        def coordinate(self):
            # Code to coordinate interactions between the robot and sensor
            pass

    class Robot:
        def move(self):
            pass

    class Sensor:
        def read_value(self):
            pass

.. code-block:: java

    public class Mediator {
        private Robot robot;
        private Sensor sensor;

        public void setRobot(Robot robot) {
            this.robot = robot;
        }

        public void setSensor(Sensor sensor) {
            this.sensor = sensor;
        }

        public void coordinate() {
            // Code to coordinate interactions between the robot and sensor
        }
    }

    public class Robot {
        public void move() {
            // Code for moving the robot
        }
    }

    public class Sensor {
        public int readValue() {
            // Code for reading sensor value
            return 0;
        }
    }

Protected variations
~~~~~~~~~~~~~~~~~~~~

Protected variations is a principle that suggests assigning responsibilities in a way that protects elements from variations in other elements, such as using interfaces or abstract classes to shield clients from changes in the implementation. This means that you can design your classes and their interactions in a way that allows for changes in one part of the system without affecting other parts, reducing the risk of introducing bugs and making it easier to adapt to changing requirements. By following this principle, you can create a more flexible and maintainable codebase, as clients will be insulated from changes in the implementation, allowing for greater code reuse and easier maintenance. This can be achieved through the use of design patterns such as the adapter pattern, which allows classes with incompatible interfaces to work together, or the facade pattern, which provides a simplified interface to a complex subsystem.

.. code-block:: python

    class SensorInterface:
        def read_value(self):
            pass  # Interface to shield clients from changes in the sensor implementation

    class Sensor(SensorInterface):
        def read_value(self):
            # Code for reading sensor value
            return 0

    class Robot:
        def __init__(self, sensor: SensorInterface):
            self.sensor = sensor  # Robot depends on the SensorInterface, not the concrete Sensor implementation

        def move(self):
            value = self.sensor.read_value()  # Robot can work with any implementation of SensorInterface

.. code-block:: java

    public interface SensorInterface {
        int readValue(); // Interface to shield clients from changes in the sensor implementation
    }

    public class Sensor implements SensorInterface {
        @Override
        public int readValue() {
            // Code for reading sensor value
            return 0;
        }
    }

    public class Robot {
        private SensorInterface sensor; // Robot depends on the SensorInterface, not the concrete Sensor implementation

        public Robot(SensorInterface sensor) {
            this.sensor = sensor; // Initialize the sensor
        }

        public void move() {
            int value = this.sensor.readValue(); // Robot can work with any implementation of SensorInterface
        }
    }

Separation of concerns
^^^^^^^^^^^^^^^^^^^^^^

Separation of concerns is a principle that suggests dividing a software system into distinct sections, each of which addresses a separate concern or aspect of the system. This means that different parts of the system should be responsible for different functionalities, allowing for greater modularity and maintainability. By following this principle, you can create a more organized and understandable codebase, as each section of the code will have a clear purpose and will be easier to modify and extend without affecting other parts of the system. This can be achieved through the use of design patterns such as the model-view-controller (MVC) pattern, which separates the data model, user interface, and control logic into distinct components.

.. code-block:: python

    class Model:
        def __init__(self):
            self.data = "Model data"

    class View:
        def display(self, data):
            print(f"Displaying: {data}")

    class Controller:
        def __init__(self, model, view):
            self.model = model
            self.view = view

        def update_view(self):
            self.view.display(self.model.data)

    # Example usage
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.update_view()  # Output: "Displaying: Model data"

.. code-block:: java

    public class Model {
        private String data = "Model data";

        public String getData() {
            return data;
        }
    }

    public class View {
        public void display(String data) {
            System.out.println("Displaying: " + data);
        }
    }

    public class Controller {
        private Model model;
        private View view;

        public Controller(Model model, View view) {
            this.model = model;
            this.view = view;
        }

        public void updateView() {
            view.display(model.getData());
        }
    }

    // Example usage
    public class Main {
        public static void main(String[] args) {
            Model model = new Model();
            View view = new View();
            Controller controller = new Controller(model, view);
            controller.updateView(); // Output: "Displaying: Model data"
        }
    }

Coupling and cohesion
^^^^^^^^^^^^^^^^^^^^^

Coupling refers to the degree of interdependence between software modules, while cohesion refers to the degree to which the elements within a module belong together. High coupling means that modules are highly dependent on each other, while low coupling means that modules are independent and can be modified without affecting other modules. High cohesion means that the elements within a module are closely related and work together to achieve a specific purpose, while low cohesion means that the elements within a module are unrelated and do not work together effectively. By striving for low coupling and high cohesion in your software design, you can create a more maintainable and flexible codebase, as changes to one module will have minimal impact on other modules, and each module will have a clear and focused purpose.

.. code-block:: python

    class Sensor:
        def read_value(self):
            pass  # Low coupling, as Sensor does not depend on other modules

    class Robot:
        def __init__(self, sensor):
            self.sensor = sensor  # Low coupling, as Robot depends on Sensor but Sensor does not depend on Robot

        def move(self):
            value = self.sensor.read_value()  # High cohesion, as move method is focused on robot movement logic

.. code-block:: java

    public class Sensor {
        public int readValue() {
            // Low coupling, as Sensor does not depend on other modules
            return 0;
        }
    }

    public class Robot {
        private Sensor sensor; // Low coupling, as Robot depends on Sensor but Sensor does not depend on Robot

        public Robot(Sensor sensor) {
            this.sensor = sensor; // Initialize the sensor
        }

        public void move() {
            int value = this.sensor.readValue(); // High cohesion, as move method is focused on robot movement logic
        }
    }

Law of Demeter
^^^^^^^^^^^^^^

Demeter is a principle that suggests that a module should not know about the internal details of other modules, and should only interact with its immediate collaborators. This means that a module should only call methods on objects that it directly owns or has a direct relationship with, rather than reaching through multiple layers of objects to access functionality. By following this principle, you can create a more maintainable and flexible codebase, as modules will be less dependent on the internal structure of other modules, reducing the risk of introducing bugs and making it easier to modify and extend the system in the future. This can be achieved by designing your classes and their interactions in a way that minimizes the need for modules to access the internal details of other modules, such as by using interfaces or abstract classes to define clear boundaries between modules.

Law of demeter states that a module should not know about the internal details of other modules, and should only interact with its immediate collaborators. This means that a module should only call methods on objects that it directly owns or has a direct relationship with, rather than reaching through multiple layers of objects to access functionality. By following this principle, you can create a more maintainable and flexible codebase, as modules will be less dependent on the internal structure of other modules, reducing the risk of introducing bugs and making it easier to modify and extend the system in the future. This can be achieved by designing your classes and their interactions in a way that minimizes the need for modules to access the internal details of other modules, such as by using interfaces or abstract classes to define clear boundaries between modules.

.. code-block:: python

    class Sensor:
        def read_value(self):
            pass

    class Robot:
        def __init__(self, sensor):
            self.sensor = sensor  # Robot has a direct relationship with Sensor

        def move(self):
            value = self.sensor.read_value()  # Robot interacts with its immediate collaborator, Sensor

.. code-block:: java

    public class Sensor {
        public int readValue() {
            // Code for reading sensor value
            return 0;
        }
    }

    public class Robot {
        private Sensor sensor; // Robot has a direct relationship with Sensor

        public Robot(Sensor sensor) {
            this.sensor = sensor; // Initialize the sensor
        }

        public void move() {
            int value = this.sensor.readValue(); // Robot interacts with its immediate collaborator, Sensor
        }
    }

Design patterns
---------------

Design patterns are reusable solutions to common software design problems that have been proven effective over time. They provide a way to structure your code in a way that is maintainable, flexible, and scalable. Design patterns can be categorized into three main types: creational patterns, structural patterns, and behavioral patterns. 

- **Creational patterns:** focus on object creation mechanisms, structural patterns focus on the composition of classes and objects.
- **Behavioral patterns:** focus on communication between objects. By using design patterns in your software design, you can create a more robust and maintainable codebase, as they provide a common language and structure for solving common design problems, making it easier to understand and modify the code in the future.
- **Structural patterns:** focus on the composition of classes and objects, while behavioral patterns focus on communication between objects. By using design patterns in your software design, you can create a more robust and maintainable codebase, as they provide a common language and structure for solving common design problems, making it easier to understand and modify the code in the future.

Creational patterns
^^^^^^^^^^^^^^^^^^^

Creational pattern is a design pattern that focuses on object creation mechanisms, trying to create objects in a manner suitable to the situation. The basic form of object creation could lead to design problems or added complexity in the design. Creational design patterns solve this problem by somehow controlling this object creation. Some common creational patterns include:

- **Singleton:** Ensures that a class has only one instance and provides a global point of access to it.
- **Factory method:** Defines an interface for creating an object, but lets subclasses alter the type of objects that will be created.
- **Abstract factory:** Provides an interface for creating families of related or dependent objects without specifying their concrete classes.
- **Builder:** Separates the construction of a complex object from its representation, allowing the same construction process to create different representations.
- **Prototype:** Specifies the kinds of objects to create using a prototypical instance, and creates new objects by copying this prototype.

Singleton
~~~~~~~~~

Singleton is a design pattern that ensures a class has only one instance and provides a global point of access to it. This is useful when you want to control access to a shared resource, such as a database connection or a configuration manager, and ensure that there is only one instance of that resource throughout the application. The singleton pattern can be implemented in various programming languages, and it typically involves making the constructor private and providing a static method to get the instance of the class.

.. code-block:: python

    class Singleton:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__new__(cls)
            return cls._instance

.. code-block:: java

    public class Singleton {
        private static Singleton instance;

        private Singleton() {
            // Private constructor to prevent instantiation
        }

        public static Singleton getInstance() {
            if (instance == null) {
                instance = new Singleton();
            }
            return instance;
        }
    }

Factory method
~~~~~~~~~~~~~~

Factory method is a design pattern that defines an interface for creating an object, but lets subclasses alter the type of objects that will be created. This pattern allows a class to defer instantiation to subclasses, providing a way to create objects without specifying the exact class of object that will be created. By using the factory method pattern, you can create a more flexible and maintainable codebase, as it allows you to add new types of objects without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a factory method in a base class or interface, and then implementing that method in subclasses to create specific types of objects. 

.. code-block:: python

    class VehicleFactory:
        def create_vehicle(self):
            pass  # Factory method to be implemented by subclasses

    class CarFactory(VehicleFactory):
        def create_vehicle(self):
            return Car()  # Create a Car object

    class BikeFactory(VehicleFactory):
        def create_vehicle(self):
            return Bike()  # Create a Bike object

.. code-block:: java

    public abstract class VehicleFactory {
        public abstract Vehicle createVehicle(); // Factory method to be implemented by subclasses
    }

    public class CarFactory extends VehicleFactory {
        @Override
        public Vehicle createVehicle() {
            return new Car(); // Create a Car object
        }
    }

    public class BikeFactory extends VehicleFactory {
        @Override
        public Vehicle createVehicle() {
            return new Bike(); // Create a Bike object
        }
    }

Abstract factory
~~~~~~~~~~~~~~~~

Abstract factory is a design pattern that provides an interface for creating families of related or dependent objects without specifying their concrete classes. This pattern allows you to create a suite of related products without being tied to specific implementations, making it easier to maintain and extend your codebase. By using the abstract factory pattern, you can create a more flexible and maintainable codebase, as it allows you to add new families of products without modifying existing code, adhering to the open-closed principle. This can be achieved by defining an abstract factory interface that declares methods for creating each type of product, and then implementing that interface in concrete factory classes that create specific families of products. 

.. code-block:: python

    class AbstractFactory:
        def create_product_a(self):
            pass  # Method to create product A

        def create_product_b(self):
            pass  # Method to create product B

    class ConcreteFactory1(AbstractFactory):
        def create_product_a(self):
            return ProductA1()  # Create product A1

        def create_product_b(self):
            return ProductB1()  # Create product B1

    class ConcreteFactory2(AbstractFactory):
        def create_product_a(self):
            return ProductA2()  # Create product A2

        def create_product_b(self):
            return ProductB2()  # Create product B2

.. code-block:: java   

    public abstract class AbstractFactory {
        public abstract ProductA createProductA(); // Method to create product A
        public abstract ProductB createProductB(); // Method to create product B
    }

    public class ConcreteFactory1 extends AbstractFactory {
        @Override
        public ProductA createProductA() {
            return new ProductA1(); // Create product A1
        }

        @Override
        public ProductB createProductB() {
            return new ProductB1(); // Create product B1
        }
    }

    public class ConcreteFactory2 extends AbstractFactory {
        @Override
        public ProductA createProductA() {
            return new ProductA2(); // Create product A2
        }

        @Override
        public ProductB createProductB() {
            return new ProductB2(); // Create product B2
        }
    }

Builder
~~~~~~~

Builder is a design pattern that separates the construction of a complex object from its representation, allowing the same construction process to create different representations. This pattern is useful when you want to create an object that requires multiple steps to construct, and you want to be able to create different variations of that object without changing the construction process. By using the builder pattern, you can create a more flexible and maintainable codebase, as it allows you to add new variations of the object without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a builder interface that declares methods for constructing each part of the object, and then implementing that interface in concrete builder classes that create specific variations of the object.

.. code-block:: python

    class Builder:
        def build_part_a(self):
            pass  # Method to build part A

        def build_part_b(self):
            pass  # Method to build part B

        def get_result(self):
            pass  # Method to return the final product

    class ConcreteBuilder1(Builder):
        def build_part_a(self):
            # Build part A for product 1
            pass

        def build_part_b(self):
            # Build part B for product 1
            pass

        def get_result(self):
            return Product1()  # Return the final product 1

    class ConcreteBuilder2(Builder):
        def build_part_a(self):
            # Build part A for product 2
            pass

        def build_part_b(self):
            # Build part B for product 2
            pass

        def get_result(self):
            return Product2()  # Return the final product 2

.. code-block:: java

    public abstract class Builder {
        public abstract void buildPartA(); // Method to build part A
        public abstract void buildPartB(); // Method to build part B
        public abstract Product getResult(); // Method to return the final product
    }

    public class ConcreteBuilder1 extends Builder {
        @Override
        public void buildPartA() {
            // Build part A for product 1
        }

        @Override
        public void buildPartB() {
            // Build part B for product 1
        }

        @Override
        public Product getResult() {
            return new Product1(); // Return the final product 1
        }
    }

    public class ConcreteBuilder2 extends Builder {
        @Override
        public void buildPartA() {
            // Build part A for product 2
        }

        @Override
        public void buildPartB() {
            // Build part B for product 2
        }

        @Override
        public Product getResult() {
            return new Product2(); // Return the final product 2
        }
    }

Prototype
~~~~~~~~~

Prototype is a design pattern that specifies the kinds of objects to create using a prototypical instance, and creates new objects by copying this prototype. This pattern is useful when you want to create new objects that are similar to existing objects, and you want to avoid the overhead of creating new instances from scratch. By using the prototype pattern, you can create a more flexible and maintainable codebase, as it allows you to create new variations of an object without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a prototype interface that declares a method for cloning the object, and then implementing that interface in concrete prototype classes that create specific variations of the object.

.. code-block:: python

    class Prototype:
        def clone(self):
            pass  # Method to clone the object

    class ConcretePrototype(Prototype):
        def clone(self):
            # Code to create a copy of the object
            return ConcretePrototype()  # Return the cloned object

.. code-block:: java

    public abstract class Prototype {
        public abstract Prototype clone(); // Method to clone the object
    }

    public class ConcretePrototype extends Prototype {
        @Override
        public Prototype clone() {
            // Code to create a copy of the object
            return new ConcretePrototype(); // Return the cloned object
        }
    }

Structural patterns
^^^^^^^^^^^^^^^^^^^

Structural patterns are design patterns that focus on the composition of classes and objects, providing ways to create relationships between them to form larger structures. These patterns help to ensure that if one part of a system changes, the entire system doesn't need to change as well. By using structural patterns in your software design, you can create a more flexible and maintainable codebase, as they provide a common language and structure for organizing classes and objects, making it easier to understand and modify the code in the future. Some common structural patterns include:

- **Adapter:** Allows classes with incompatible interfaces to work together by converting the interface of one class into an interface expected by the clients.
- **Decorator:** Allows behavior to be added to individual objects, either statically or dynamically, without affecting the behavior of other objects from the same class.
- **Facade:** Provides a simplified interface to a complex subsystem, making it easier to use and understand.
- **Proxy:** Provides a surrogate or placeholder for another object to control access to it.
- **Composite:** Composes objects into tree structures to represent part-whole hierarchies, allowing clients to treat individual objects and compositions of objects uniformly.

Adapter
~~~~~~~

Adapter is a design pattern that allows classes with incompatible interfaces to work together by converting the interface of one class into an interface expected by the clients. This pattern is useful when you want to use an existing class that does not have the desired interface, and you want to avoid modifying the existing class or creating a new class that inherits from it. By using the adapter pattern, you can create a more flexible and maintainable codebase, as it allows you to integrate existing classes into your system without modifying them, adhering to the open-closed principle. This can be achieved by defining an adapter class that implements the desired interface and holds a reference to an instance of the existing class, forwarding calls to the existing class as needed.

.. code-block:: python

    class TargetInterface:
        def request(self):
            pass  # Desired interface for clients

    class Adaptee:
        def specific_request(self):
            pass  # Existing class with an incompatible interface

    class Adapter(TargetInterface):
        def __init__(self, adaptee):
            self.adaptee = adaptee  # Hold a reference to the existing class

        def request(self):
            return self.adaptee.specific_request()  # Forward calls to the existing class

.. code-block:: java

    public interface TargetInterface {
        void request(); // Desired interface for clients
    }

    public class Adaptee {
        public void specificRequest() {
            // Existing class with an incompatible interface
        }
    }

    public class Adapter implements TargetInterface {
        private Adaptee adaptee; // Hold a reference to the existing class

        public Adapter(Adaptee adaptee) {
            this.adaptee = adaptee;
        }

        @Override
        public void request() {
            adaptee.specificRequest(); // Forward calls to the existing class
        }
    }

Decorator
~~~~~~~~~

Decorator is a design pattern that allows behavior to be added to individual objects, either statically or dynamically, without affecting the behavior of other objects from the same class. This pattern is useful when you want to add responsibilities to objects without modifying their class, and you want to be able to add or remove responsibilities at runtime. By using the decorator pattern, you can create a more flexible and maintainable codebase, as it allows you to extend the functionality of objects without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a decorator class that implements the same interface as the objects it decorates and holds a reference to an instance of the object being decorated, forwarding calls to the decorated object and adding additional behavior as needed. 

.. code-block:: python

    class Component:
        def operation(self):
            pass  # Interface for objects that can have responsibilities added to them

    class ConcreteComponent(Component):
        def operation(self):
            # Code for the core functionality of the component
            pass

    class Decorator(Component):
        def __init__(self, component):
            self.component = component  # Hold a reference to the object being decorated

        def operation(self):
            self.component.operation()  # Forward calls to the decorated object
            # Add additional behavior here

.. code-block:: java

    public interface Component {
        void operation(); // Interface for objects that can have responsibilities added to them
    }

    public class ConcreteComponent implements Component {
        @Override
        public void operation() {
            // Code for the core functionality of the component
        }
    }

    public class Decorator implements Component {
        private Component component; // Hold a reference to the object being decorated

        public Decorator(Component component) {
            this.component = component;
        }

        @Override
        public void operation() {
            component.operation(); // Forward calls to the decorated object
            // Add additional behavior here
        }
    }

Facade
~~~~~~

Facade is a design pattern that provides a simplified interface to a complex subsystem, making it easier to use and understand. This pattern is useful when you want to hide the complexities of a subsystem from clients and provide a simple interface for them to interact with. By using the facade pattern, you can create a more maintainable and flexible codebase, as it allows you to change the underlying implementation of the subsystem without affecting clients, adhering to the open-closed principle. This can be achieved by defining a facade class that provides methods for clients to interact with the subsystem, and internally uses instances of the subsystem classes to perform the necessary operations.

.. code-block:: python

    class SubsystemA:
        def operation_a(self):
            pass  # Code for subsystem A

    class SubsystemB:
        def operation_b(self):
            pass  # Code for subsystem B

    class Facade:
        def __init__(self):
            self.subsystem_a = SubsystemA()
            self.subsystem_b = SubsystemB()

        def simplified_operation(self):
            self.subsystem_a.operation_a()  # Use subsystem A
            self.subsystem_b.operation_b()  # Use subsystem B
            # Provide a simplified interface for clients

.. code-block:: java

    public class SubsystemA {
        public void operationA() {
            // Code for subsystem A
        }
    }

    public class SubsystemB {
        public void operationB() {
            // Code for subsystem B
        }
    }

    public class Facade {
        private SubsystemA subsystemA;
        private SubsystemB subsystemB;

        public Facade() {
            this.subsystemA = new SubsystemA();
            this.subsystemB = new SubsystemB();
        }

        public void simplifiedOperation() {
            subsystemA.operationA(); // Use subsystem A
            subsystemB.operationB(); // Use subsystem B
            // Provide a simplified interface for clients
        }
    }

Proxy
~~~~~

Proxy is a design pattern that provides a surrogate or placeholder for another object to control access to it. This pattern is useful when you want to control access to an object, such as by adding security, logging, or lazy initialization, without modifying the original object's code. By using the proxy pattern, you can create a more flexible and maintainable codebase, as it allows you to add additional behavior to an object without modifying its class, adhering to the open-closed principle. This can be achieved by defining a proxy class that implements the same interface as the original object and holds a reference to an instance of the original object, controlling access to it and adding additional behavior as needed.

.. code-block:: python

    class Subject:
        def request(self):
            pass  # Interface for the original object

    class RealSubject(Subject):
        def request(self):
            # Code for the original object's functionality
            pass

    class Proxy(Subject):
        def __init__(self, real_subject):
            self.real_subject = real_subject  # Hold a reference to the original object

        def request(self):
            # Add additional behavior here (e.g., logging, security checks)
            return self.real_subject.request()  # Control access to the original object

.. code-block:: java

    public interface Subject {
        void request(); // Interface for the original object
    }

    public class RealSubject implements Subject {
        @Override
        public void request() {
            // Code for the original object's functionality
        }
    }

    public class Proxy implements Subject {
        private RealSubject realSubject; // Hold a reference to the original object

        public Proxy(RealSubject realSubject) {
            this.realSubject = realSubject;
        }

        @Override
        public void request() {
            // Add additional behavior here (e.g., logging, security checks)
            realSubject.request(); // Control access to the original object
        }
    }

Composite
~~~~~~~~~

Composite is a design pattern that composes objects into tree structures to represent part-whole hierarchies, allowing clients to treat individual objects and compositions of objects uniformly. This pattern is useful when you want to represent a hierarchy of objects, such as a file system or a graphical user interface, and you want to be able to treat individual objects and groups of objects in the same way. By using the composite pattern, you can create a more flexible and maintainable codebase, as it allows you to add new types of components without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a component interface that declares methods for both individual objects and compositions, and then implementing that interface in both leaf classes (representing individual objects) and composite classes (representing groups of objects).

.. code-block:: python

    class Component:
        def operation(self):
            pass  # Interface for both individual objects and compositions

    class Leaf(Component):
        def operation(self):
            # Code for the individual object's functionality
            pass

    class Composite(Component):
        def __init__(self):
            self.children = []  # List to hold child components

        def add(self, component):
            self.children.append(component)  # Add a child component

        def remove(self, component):
            self.children.remove(component)  # Remove a child component

        def operation(self):
            for child in self.children:
                child.operation()  # Forward the operation to child components

.. code-block:: java

    public interface Component {
        void operation(); // Interface for both individual objects and compositions
    }

    public class Leaf implements Component {
        @Override
        public void operation() {
            // Code for the individual object's functionality
        }
    }

    public class Composite implements Component {
        private List<Component> children = new ArrayList<>(); // List to hold child components

        public void add(Component component) {
            children.add(component); // Add a child component
        }

        public void remove(Component component) {
            children.remove(component); // Remove a child component
        }

        @Override
        public void operation() {
            for (Component child : children) {
                child.operation(); // Forward the operation to child components
            }
        }
    }

Behavioral patterns
^^^^^^^^^^^^^^^^^^^

Behavioral patterns are design patterns that focus on communication between objects, providing ways to define how objects interact and distribute responsibility. These patterns help to ensure that the interactions between objects are well-defined and organized, making it easier to understand and modify the behavior of a system. By using behavioral patterns in your software design, you can create a more flexible and maintainable codebase, as they provide a common language and structure for defining object interactions, making it easier to understand and modify the code in the future. Some common behavioral patterns include:

- **Observer:** Defines a one-to-many dependency between objects, so that when one object changes state, all its dependents are notified and updated automatically.
- **Strategy:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable, allowing the algorithm to vary independently from clients that use it.
- **Command:** Encapsulates a request as an object, thereby allowing for parameterization of clients with queues, requests, and operations.
- **State:** Allows an object to alter its behavior when its internal state changes, appearing as if the object changed its class.
- **Template method:** Defines the skeleton of an algorithm in an operation, deferring some steps to subclasses, allowing them to redefine certain steps of the algorithm without changing its structure.
- **Iterator:** Provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation.
- **Mediator:** Defines an object that encapsulates how a set of objects interact, promoting loose coupling by keeping objects from referring to each other explicitly, and allowing their interaction to be varied independently.

Observer
~~~~~~~~

Observer is a design pattern that defines a one-to-many dependency between objects, so that when one object changes state, all its dependents are notified and updated automatically. This pattern is useful when you want to create a system where multiple objects need to be informed of changes to a particular object, such as in a publish-subscribe model or an event-driven architecture. By using the observer pattern, you can create a more flexible and maintainable codebase, as it allows you to add new observers without modifying existing code, adhering to the open-closed principle. This can be achieved by defining an observer interface that declares a method for receiving updates, and then implementing that interface in concrete observer classes that register themselves with the subject they want to observe.

.. code-block:: python

    class Subject:
        def __init__(self):
            self.observers = []  # List to hold registered observers

        def register_observer(self, observer):
            self.observers.append(observer)  # Register an observer

        def notify_observers(self):
            for observer in self.observers:
                observer.update()  # Notify all registered observers of a change

    class Observer:
        def update(self):
            pass  # Method to receive updates from the subject

    class ConcreteObserver(Observer):
        def update(self):
            # Code to handle the update from the subject
            pass    

.. code-block:: java

    public class Subject {
        private List<Observer> observers = new ArrayList<>(); // List to hold registered observers

        public void registerObserver(Observer observer) {
            observers.add(observer); // Register an observer
        }

        public void notifyObservers() {
            for (Observer observer : observers) {
                observer.update(); // Notify all registered observers of a change
            }
        }
    }

    public interface Observer {
        void update(); // Method to receive updates from the subject
    }

    public class ConcreteObserver implements Observer {
        @Override
        public void update() {
            // Code to handle the update from the subject
        }
    }

Strategy
~~~~~~~~

Strategy is a design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable, allowing the algorithm to vary independently from clients that use it. This pattern is useful when you want to create a system where multiple algorithms can be used interchangeably, such as in a sorting or compression context. By using the strategy pattern, you can create a more flexible and maintainable codebase, as it allows you to add new algorithms without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a strategy interface that declares a method for executing the algorithm, and then implementing that interface in concrete strategy classes that provide specific implementations of the algorithm.

.. code-block:: python

    class Strategy:
        def execute(self):
            pass  # Method to execute the algorithm

    class ConcreteStrategyA(Strategy):
        def execute(self):
            # Code for algorithm A
            pass

    class ConcreteStrategyB(Strategy):
        def execute(self):
            # Code for algorithm B
            pass

.. code-block:: java

    public interface Strategy {
        void execute(); // Method to execute the algorithm
    }

    public class ConcreteStrategyA implements Strategy {
        @Override
        public void execute() {
            // Code for algorithm A
        }
    }

    public class ConcreteStrategyB implements Strategy {
        @Override
        public void execute() {
            // Code for algorithm B
        }
    }

Command
~~~~~~~

Command is a design pattern that encapsulates a request as an object, thereby allowing for parameterization of clients with queues, requests, and operations. This pattern is useful when you want to create a system where requests can be treated as first-class objects, allowing for features such as undo/redo functionality, queuing of requests, or logging of operations. By using the command pattern, you can create a more flexible and maintainable codebase, as it allows you to add new commands without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a command interface that declares a method for executing the command, and then implementing that interface in concrete command classes that encapsulate specific requests.

.. code-block:: python

    class Command:
        def execute(self):
            pass  # Method to execute the command

    class ConcreteCommandA(Command):
        def __init__(self, receiver):
            self.receiver = receiver  # Receiver of the command

        def execute(self):
            self.receiver.action_a()  # Execute the command by calling a method on the receiver

    class ConcreteCommandB(Command):
        def __init__(self, receiver):
            self.receiver = receiver  # Receiver of the command

        def execute(self):
            self.receiver.action_b()  # Execute the command by calling a method on the receiver

.. code-block:: java

    public interface Command {
        void execute(); // Method to execute the command
    }

    public class ConcreteCommandA implements Command {
        private Receiver receiver; // Receiver of the command

        public ConcreteCommandA(Receiver receiver) {
            this.receiver = receiver;
        }

        @Override
        public void execute() {
            receiver.actionA(); // Execute the command by calling a method on the receiver
        }
    }

    public class ConcreteCommandB implements Command {
        private Receiver receiver; // Receiver of the command

        public ConcreteCommandB(Receiver receiver) {
            this.receiver = receiver;
        }

        @Override
        public void execute() {
            receiver.actionB(); // Execute the command by calling a method on the receiver
        }
    }

State
~~~~~

State is a design pattern that allows an object to alter its behavior when its internal state changes, appearing as if the object changed its class. This pattern is useful when you want to create a system where an object's behavior can change based on its state, such as in a finite state machine or a user interface context. By using the state pattern, you can create a more flexible and maintainable codebase, as it allows you to add new states without modifying existing code, adhering to the open-closed principle. This can be achieved by defining a state interface that declares methods for handling requests, and then implementing that interface in concrete state classes that represent specific states of the object.

.. code-block:: python

    class State:
        def handle(self):
            pass  # Method to handle requests based on the state

    class ConcreteStateA(State):
        def handle(self):
            # Code for handling requests in state A
            pass

    class ConcreteStateB(State):
        def handle(self):
            # Code for handling requests in state B
            pass

.. code-block:: java

    public interface State {
        void handle(); // Method to handle requests based on the state
    }

    public class ConcreteStateA implements State {
        @Override
        public void handle() {
            // Code for handling requests in state A
        }
    }

    public class ConcreteStateB implements State {
        @Override
        public void handle() {
            // Code for handling requests in state B
        }
    }

Template method
~~~~~~~~~~~~~~~

Template method is a design pattern that defines the skeleton of an algorithm in an operation, deferring some steps to subclasses, allowing them to redefine certain steps of the algorithm without changing its structure. This pattern is useful when you want to create a system where multiple algorithms share a common structure, but differ in specific steps, such as in a data processing pipeline or a game loop. By using the template method pattern, you can create a more flexible and maintainable codebase, as it allows you to add new algorithms without modifying existing code, adhering to the open-closed principle. This can be achieved by defining an abstract class that implements the template method, which calls abstract methods for the steps that can be overridden by subclasses.

.. code-block:: python

    class AbstractClass:
        def template_method(self):
            self.step_one()  # Common step
            self.step_two()  # Common step
            self.step_three()  # Common step

        def step_one(self):
            pass  # Step one implementation

        def step_two(self):
            pass  # Step two implementation

        def step_three(self):
            pass  # Step three implementation

    class ConcreteClassA(AbstractClass):
        def step_one(self):
            # Code for step one in algorithm A
            pass

        def step_two(self):
            # Code for step two in algorithm A
            pass

        def step_three(self):
            # Code for step three in algorithm A
            pass

    class ConcreteClassB(AbstractClass):
        def step_one(self):
            # Code for step one in algorithm B
            pass

        def step_two(self):
            # Code for step two in algorithm B
            pass

        def step_three(self):
            # Code for step three in algorithm B
            pass

.. code-block:: java

    public abstract class AbstractClass {
        public final void templateMethod() {
            stepOne(); // Common step
            stepTwo(); // Common step
            stepThree(); // Common step
        }

        protected abstract void stepOne(); // Step one implementation
        protected abstract void stepTwo(); // Step two implementation
        protected abstract void stepThree(); // Step three implementation
    }

    public class ConcreteClassA extends AbstractClass {
        @Override
        protected void stepOne() {
            // Code for step one in algorithm A
        }

        @Override
        protected void stepTwo() {
            // Code for step two in algorithm A
        }

        @Override
        protected void stepThree() {
            // Code for step three in algorithm A
        }
    }

    public class ConcreteClassB extends AbstractClass {
        @Override
        protected void stepOne() {
            // Code for step one in algorithm B
        }

        @Override
        protected void stepTwo() {
            // Code for step two in algorithm B
        }

        @Override
        protected void stepThree() {
            // Code for step three in algorithm B
        }
    }

Iterator
~~~~~~~~

Iterator is a design pattern that provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation. This pattern is useful when you want to create a system where you need to traverse a collection of objects, such as in a list or a tree structure, and you want to be able to do so without exposing the internal structure of the collection. By using the iterator pattern, you can create a more flexible and maintainable codebase, as it allows you to add new types of collections without modifying existing code, adhering to the open-closed principle. This can be achieved by defining an iterator interface that declares methods for traversing the collection, and then implementing that interface in concrete iterator classes that provide specific implementations for different types of collections.

.. code-block:: python

    class Iterator:
        def has_next(self):
            pass  # Method to check if there are more elements to iterate over

        def next(self):
            pass  # Method to return the next element in the collection

    class ConcreteIterator(Iterator):
        def __init__(self, collection):
            self.collection = collection  # Reference to the collection being iterated
            self.index = 0  # Current index in the iteration

        def has_next(self):
            return self.index < len(self.collection)  # Check if there are more elements

        def next(self):
            if self.has_next():
                element = self.collection[self.index]  # Get the next element
                self.index += 1  # Move to the next index
                return element
            else:
                raise StopIteration()  # No more elements to iterate over

.. code-block:: java

    public interface Iterator {
        boolean hasNext(); // Method to check if there are more elements to iterate over
        Object next(); // Method to return the next element in the collection
    }

    public class ConcreteIterator implements Iterator {
        private List<Object> collection; // Reference to the collection being iterated
        private int index = 0; // Current index in the iteration

        public ConcreteIterator(List<Object> collection) {
            this.collection = collection;
        }

        @Override
        public boolean hasNext() {
            return index < collection.size(); // Check if there are more elements
        }

        @Override
        public Object next() {
            if (hasNext()) {
                Object element = collection.get(index); // Get the next element
                index++; // Move to the next index
                return element;
            } else {
                throw new NoSuchElementException(); // No more elements to iterate over
            }
        }
    }

Mediator
~~~~~~~~

Mediator is a design pattern that defines an object that encapsulates how a set of objects interact, promoting loose coupling by keeping objects from referring to each other explicitly, and allowing their interaction to be varied independently. This pattern is useful when you want to create a system where multiple objects need to communicate with each other, but you want to avoid tight coupling between them, such as in a chat application or a user interface context. By using the mediator pattern, you can create a more flexible and maintainable codebase, as it allows you to change the interactions between objects without modifying their classes, adhering to the open-closed principle. This can be achieved by defining a mediator interface that declares methods for communication between objects, and then implementing that interface in a concrete mediator class that coordinates the interactions between the objects.

.. code-block:: python

    class Mediator:
        def notify(self, sender, event):
            pass  # Method to handle communication between objects

    class ConcreteMediator(Mediator):
        def __init__(self, component1, component2):
            self.component1 = component1  # Reference to component 1
            self.component2 = component2  # Reference to component 2
            self.component1.set_mediator(self)  # Set the mediator for component 1
            self.component2.set_mediator(self)  # Set the mediator for component 2

        def notify(self, sender, event):
            if sender == self.component1 and event == "EventA":
                # Handle event A from component 1 and coordinate with component 2
                pass
            elif sender == self.component2 and event == "EventB":
                # Handle event B from component 2 and coordinate with component 1
                pass

.. code-block:: java

    public interface Mediator {
        void notify(Object sender, String event); // Method to handle communication between objects
    }

    public class ConcreteMediator implements Mediator {
        private Component1 component1; // Reference to component 1
        private Component2 component2; // Reference to component 2

        public ConcreteMediator(Component1 component1, Component2 component2) {
            this.component1 = component1;
            this.component2 = component2;
            this.component1.setMediator(this); // Set the mediator for component 1
            this.component2.setMediator(this); // Set the mediator for component 2
        }

        @Override
        public void notify(Object sender, String event) {
            if (sender == component1 && event.equals("EventA")) {
                // Handle event A from component 1 and coordinate with component 2
            } else if (sender == component2 && event.equals("EventB")) {
                // Handle event B from component 2 and coordinate with component 1
            }
        }
    }

OOP memory or architecture concepts
-----------------------------------

Memory management is an important aspect of object-oriented programming, as it involves the allocation and deallocation of memory for objects and data structures. In OOP, memory management can be handled manually by the programmer or automatically through garbage collection, depending on the programming language being used. Manual memory management requires the programmer to explicitly allocate and deallocate memory for objects, which can lead to issues such as memory leaks and dangling pointers if not done correctly. On the other hand, automatic memory management through garbage collection allows the programming language to automatically manage memory, freeing up resources when they are no longer needed, which can help to prevent memory-related bugs and improve the overall stability of the application. Understanding memory management concepts is crucial for writing efficient and reliable object-oriented code.

Garbage collection
^^^^^^^^^^^^^^^^^^

Garbage collection is a form of automatic memory management that is used in many object-oriented programming languages, such as Java and Python. It works by automatically identifying and freeing up memory that is no longer being used by the program, which helps to prevent memory leaks and improve the overall stability of the application. Garbage collection typically involves a process of marking objects that are still in use and then sweeping through memory to reclaim the space occupied by objects that are no longer needed. This allows developers to focus on writing code without having to worry about manual memory management, while still ensuring that resources are efficiently utilized.

.. code-block:: python

    # Example of garbage collection in Python
    class MyClass:
        def __init__(self, value):
            self.value = value

    obj1 = MyClass(10)  # obj1 is created and occupies memory
    obj2 = MyClass(20)  # obj2 is created and occupies memory

    del obj1  # obj1 is deleted, but memory is not immediately freed
    # Garbage collector will eventually free the memory occupied by obj1

In Java, garbage collection is handled by the Java Virtual Machine (JVM), which automatically manages memory for Java applications. The JVM uses a generational garbage collection approach, where objects are categorized into different generations based on their age. The garbage collector periodically runs to identify and reclaim memory from objects that are no longer in use, allowing developers to focus on writing code without having to worry about manual memory management.

.. code-block:: java

    // Example of garbage collection in Java
    public class MyClass {
        private int value;

        public MyClass(int value) {
            this.value = value;
        }
    }

    public class Main {
        public static void main(String[] args) {
            MyClass obj1 = new MyClass(10); // obj1 is created and occupies memory
            MyClass obj2 = new MyClass(20); // obj2 is created and occupies memory

            obj1 = null; // obj1 is dereferenced, but memory is not immediately freed
            // Garbage collector will eventually free the memory occupied by obj1
        }
    }

Manual memory management
^^^^^^^^^^^^^^^^^^^^^^^^

Manual memory management is a technique used in some programming languages, such as C and C++, where the programmer is responsible for explicitly allocating and deallocating memory for objects and data structures. This approach gives developers more control over memory usage, but it also introduces the risk of memory-related bugs, such as memory leaks (where allocated memory is not properly freed) and dangling pointers (where a pointer references memory that has already been deallocated). To avoid these issues, programmers must carefully manage memory by ensuring that every allocation has a corresponding deallocation, and by using tools such as smart pointers or memory management libraries to help automate this process. Manual memory management can be more efficient in terms of performance, but it requires a higher level of attention to detail and can lead to more complex code compared to automatic memory management through garbage collection.

.. code-block:: c

    // Example of manual memory management in C
    #include <stdio.h>
    #include <stdlib.h>

    typedef struct {
        int value;
    } MyStruct;

    int main() {
        MyStruct* obj1 = (MyStruct*)malloc(sizeof(MyStruct)); // Allocate memory for obj1
        obj1->value = 10; // Use obj1

        MyStruct* obj2 = (MyStruct*)malloc(sizeof(MyStruct)); // Allocate memory for obj2
        obj2->value = 20; // Use obj2

        free(obj1); // Deallocate memory for obj1
        free(obj2); // Deallocate memory for obj2

        return 0;
    }

.. attention:: 

    Manual memory management can lead to issues such as memory leaks and dangling pointers if not done correctly, so it is important for developers to be diligent in managing memory when using this approach.

    In Python and Java, memory management is handled automatically through garbage collection, so developers do not need to worry about manual memory management. However, it is still important to be mindful of memory usage and to avoid creating unnecessary objects or holding onto references that are no longer needed, as this can lead to increased memory usage and potential performance issues.

    In C and C++, developers must be careful to ensure that every allocation of memory has a corresponding deallocation, and to avoid common pitfalls such as double freeing (where memory is deallocated more than once) and use-after-free (where memory is accessed after it has been deallocated). Using tools such as smart pointers in C++ can help to automate memory management and reduce the risk of these issues.

.. code-block:: cpp

    // Example of using smart pointers in C++
    #include <iostream>
    #include <memory>

    class MyClass {
    public:
        MyClass(int value) : value(value) {}
        void display() { std::cout << "Value: " << value << std::endl; }
    private:
        int value;
    };

    int main() {
        std::unique_ptr<MyClass> obj1 = std::make_unique<MyClass>(10); // Automatically managed memory
        obj1->display(); // Use obj1

        std::unique_ptr<MyClass> obj2 = std::make_unique<MyClass>(20); // Automatically managed memory
        obj2->display(); // Use obj2

        // No need to manually free memory, it will be automatically deallocated when the unique_ptr goes out of scope
        return 0;
    }

Object identity
^^^^^^^^^^^^^^^

Object identity is a fundamental concept in object-oriented programming that refers to the unique identity of an object, which distinguishes it from other objects. In OOP, each object has its own identity, which is typically represented by a memory address or a unique identifier. This allows objects to be compared for equality based on their identity rather than their state or value. Object identity is important for maintaining the integrity of data and ensuring that operations on objects are performed correctly, as it allows developers to determine whether two references point to the same object in memory. Understanding object identity is crucial for writing effective and efficient object-oriented code, as it can impact how objects are managed and manipulated within a program.

.. code-block:: python

    class MyClass:
        def __init__(self, value):
            self.value = value

    obj1 = MyClass(10)  # obj1 is created and has a unique identity
    obj2 = MyClass(10)  # obj2 is created and has a different unique identity

    print(obj1 == obj2)  # Output: False (obj1 and obj2 are different objects)
    print(obj1 is obj2)  # Output: False (obj1 and obj2 do not have the same identity)

    obj3 = obj1  # obj3 references the same object as obj1
    print(obj1 == obj3)  # Output: True (obj1 and obj3 are the same object)
    print(obj1 is obj3)  # Output: True (obj1 and obj3 have the same identity)

.. code-block:: java

    public class MyClass {
        private int value;

        public MyClass(int value) {
            this.value = value;
        }
    }

    public class Main {
        public static void main(String[] args) {
            MyClass obj1 = new MyClass(10); // obj1 is created and has a unique identity
            MyClass obj2 = new MyClass(10); // obj2 is created and has a different unique identity

            System.out.println(obj1.equals(obj2)); // Output: false (obj1 and obj2 are different objects)
            System.out.println(obj1 == obj2); // Output: false (obj1 and obj2 do not have the same identity)

            MyClass obj3 = obj1; // obj3 references the same object as obj1
            System.out.println(obj1.equals(obj3)); // Output: true (obj1 and obj3 are the same object)
            System.out.println(obj1 == obj3); // Output: true (obj1 and obj3 have the same identity)
        }
    }

Shallow copy vs. deep copy
^^^^^^^^^^^^^^^^^^^^^^^^^^

Copying objects in object-oriented programming can be done in two ways: shallow copy and deep copy. A shallow copy creates a new object that is a copy of the original object, but it only copies the references to the objects contained within the original object. This means that if the original object contains mutable objects (such as lists or dictionaries), both the original and the shallow copy will reference the same mutable objects, and changes to those objects will affect both the original and the copy. On the other hand, a deep copy creates a new object that is a copy of the original object, along with copies of all the objects contained within it. This means that changes to mutable objects in the deep copy will not affect the original object, as they are completely independent. Understanding the difference between shallow and deep copying is important for managing memory and ensuring that your code behaves as expected when working with complex data structures.

.. code-block:: python

    import copy

    class MyClass:
        def __init__(self, value):
            self.value = value

    original = MyClass([1, 2, 3])  # Original object with a mutable list
    shallow_copy = copy.copy(original)  # Shallow copy of the original object
    deep_copy = copy.deepcopy(original)  # Deep copy of the original object

    shallow_copy.value.append(4)  # Modifying the mutable list in the shallow copy
    print(original.value)  # Output: [1, 2, 3, 4] (original is affected by changes to shallow copy)
    print(deep_copy.value)  # Output: [1, 2, 3] (deep copy is unaffected by changes to shallow copy)

    deep_copy.value.append(5)  # Modifying the mutable list in the deep copy
    print(original.value)  # Output: [1, 2, 3, 4] (original is unaffected by changes to deep copy)
    print(deep_copy.value)  # Output: [1, 2, 3, 5] (deep copy is modified independently of original)

.. attention:: 

    In Java, the concept of shallow and deep copying can be implemented using the ``clone()`` method for shallow copying and by implementing a custom method for deep copying, as Java does not provide built-in support for deep copying. It is important to be mindful of how objects are copied in Java, especially when dealing with mutable objects, to avoid unintended side effects.

.. code-block:: java

    public class MyClass implements Cloneable {
        private List<Integer> value;

        public MyClass(List<Integer> value) {
            this.value = value;
        }

        @Override
        protected Object clone() throws CloneNotSupportedException {
            return super.clone(); // Shallow copy
        }

        public MyClass deepCopy() {
            List<Integer> newValue = new ArrayList<>(this.value); // Deep copy of the list
            return new MyClass(newValue);
        }
    }

Immutability
^^^^^^^^^^^^

Immutabiltiy is a design principle in object-oriented programming that refers to the state of an object being unchangeable after it has been created. An immutable object is one whose state cannot be modified after it has been instantiated, meaning that any changes to the object's state result in the creation of a new object rather than modifying the existing one. Immutability can help to improve the safety and predictability of code, as it eliminates issues related to shared mutable state and makes it easier to reason about the behavior of objects. In languages like Java, immutability can be achieved by declaring fields as final and not providing setter methods, while in Python, immutability can be achieved by using tuples or by defining classes with read-only properties.

.. code-block:: python

    class ImmutableClass:
        def __init__(self, value):
            self._value = value  # Private attribute to store the value

        @property
        def value(self):
            return self._value  # Read-only property to access the value

    obj1 = ImmutableClass(10)  # Create an immutable object
    print(obj1.value)  # Output: 10

    # Attempting to modify the value will result in an error
    # obj1.value = 20  # This will raise an AttributeError

.. code-block:: java

    public final class ImmutableClass {
        private final int value; // Final field to store the value

        public ImmutableClass(int value) {
            this.value = value; // Initialize the value in the constructor
        }

        public int getValue() {
            return value; // Getter method to access the value
        }
    }

    public class Main {
        public static void main(String[] args) {
            ImmutableClass obj1 = new ImmutableClass(10); // Create an immutable object
            System.out.println(obj1.getValue()); // Output: 10

            // Attempting to modify the value will result in a compilation error
            // obj1.value = 20; // This will cause a compilation error due to the final field
        }
    }

Error handling and contracts
----------------------------

Error handling is an important aspect of object-oriented programming, as it allows developers to manage and respond to exceptional conditions that may arise during the execution of a program. In OOP, error handling can be implemented using techniques such as try-catch blocks, custom exceptions, and assertions. By using these techniques, developers can create more robust and reliable code that can gracefully handle errors and prevent crashes or unexpected behavior. Additionally, contracts can be used to define the expected behavior of methods and classes, ensuring that they are used correctly and that any violations of the contract are properly handled. Understanding error handling and contracts is crucial for writing effective and maintainable object-oriented code.

Exception handling
^^^^^^^^^^^^^^^^^^

Exception handling is a mechanism in object-oriented programming that allows developers to manage and respond to errors or exceptional conditions that may occur during the execution of a program. This is typically done using try-catch blocks, where code that may throw an exception is placed within a try block, and the corresponding catch block is used to handle the exception if it occurs. Exception handling helps to improve the robustness and reliability of code by allowing developers to gracefully handle errors and prevent crashes or unexpected behavior. Additionally, custom exceptions can be created to provide more specific error information and to allow for more fine-grained error handling.

Exceptions are typically used to signal that an error has occurred, and they can be caught and handled by the program to prevent it from crashing. In Java, exceptions are categorized into checked exceptions (which must be declared in the method signature) and unchecked exceptions (which do not need to be declared). In Python, all exceptions are unchecked, and developers can create custom exception classes by inheriting from the built-in Exception class.

Several exception includes:

- **FileNotFoundError:** Raised when a file or directory is requested but cannot be found.
- **ValueError:** Raised when a built-in operation or function receives an argument that has the right type but an inappropriate value.
- **TypeError:** Raised when an operation or function is applied to an object of inappropriate type.
- **IndexError:** Raised when a sequence subscript is out of range.
- **KeyError:** Raised when a mapping (dictionary) key is not found in the set of existing keys.
- **ZeroDivisionError:** Raised when the second argument of a division or modulo operation is zero.
- **Custom exceptions:** Developers can create their own exception classes to represent specific error conditions in their applications, allowing for more precise error handling and improved code readability.

There are several best practices for exception handling in object-oriented programming, including:

- Catching specific exceptions rather than using a generic catch-all approach, to ensure that errors are handled appropriately and to avoid masking other issues.
- Providing meaningful error messages and logging information to help with debugging and troubleshooting.
- Avoiding the use of exceptions for control flow, as this can lead to code that is difficult to read and maintain.
- Ensuring that resources are properly released in the event of an exception, such as by using finally blocks or context managers to manage resource cleanup.

.. attention:: 

    It is important to use exception handling judiciously, as overusing exceptions or using them inappropriately can lead to code that is difficult to read and maintain. Developers should strive to write code that is robust and handles errors gracefully, while also ensuring that exceptions are used in a way that enhances the clarity and maintainability of the codebase.

.. code-block:: java

    public class Main {
        public static void main(String[] args) {
            try {
                // Code that may throw an exception
                int result = 10 / 0; // This will throw a ZeroDivisionError
            } catch (ArithmeticException e) {
                System.out.println("Error: " + e.getMessage()); // Handle the exception
            } finally {
                System.out.println("This block will always execute."); // Resource cleanup or final actions
            }
        }
    }

.. code-block:: python

    try:
        # Code that may throw an exception
        result = 10 / 0  # This will raise a ZeroDivisionError
    except ZeroDivisionError as e:
        print(f"Error: {e}")  # Handle the exception
    finally:
        print("This block will always execute.")  # Resource cleanup or final actions

Custom exceptions
^^^^^^^^^^^^^^^^^

Some exceptions are built into programming languages, but developers can also create their own custom exceptions to represent specific error conditions in their applications. Custom exceptions can be created by defining a new class that inherits from the built-in Exception class (or a relevant subclass) and adding any additional attributes or methods as needed. This allows developers to provide more specific error information and to allow for more fine-grained error handling in their code. For example, in Python, you can create a custom exception like this: 

.. code-block:: python

    class CustomError(Exception):
        def __init__(self, message):
            super().__init__(message)  # Call the base class constructor with the error message

    # Example usage of the custom exception
    try:
        raise CustomError("This is a custom error message.")  # Raise the custom exception
    except CustomError as e:
        print(f"Caught a custom exception: {e}")  # Handle the custom exception

In Java, you can create a custom exception by defining a new class that extends the Exception class (or a relevant subclass) and providing a constructor to initialize the error message. For example:

.. code-block:: java

    public class CustomException extends Exception {
        public CustomException(String message) {
            super(message); // Call the base class constructor with the error message
        }
    }

    // Example usage of the custom exception
    public class Main {
        public static void main(String[] args) {
            try {             
                throw new CustomException("This is a custom error message."); // Raise the custom exception
            } catch (CustomException e) {
                System.out.println("Caught a custom exception: " + e.getMessage()); // Handle the custom exception
            }
        }
    }

Custom exceptions can be particularly useful for representing specific error conditions that are relevant to the domain of the application, allowing for more precise error handling and improved code readability. By using custom exceptions, developers can create a more robust and maintainable codebase that can effectively manage and respond to errors in a way that is meaningful to the context of the application. 

Contracts and assertions
^^^^^^^^^^^^^^^^^^^^^^^^

Contracts and assertions are techniques used in object-oriented programming to define the expected behavior of methods and classes, ensuring that they are used correctly and that any violations of the contract are properly handled. A contract is a formal agreement between a method or class and its callers, specifying the preconditions (what must be true before the method is called), postconditions (what must be true after the method is called), and invariants (conditions that must always hold true for the class). Assertions are statements that check for specific conditions at runtime, and if an assertion fails, it typically raises an error or exception. By using contracts and assertions, developers can improve the reliability and maintainability of their code by catching errors early and ensuring that methods and classes are used in a way that adheres to their intended design. For example, in Python, you can use assertions to check for preconditions and postconditions like this:

.. code-block:: python

    def divide(a, b):
        assert b != 0, "Precondition failed: denominator must not be zero"  # Precondition
        result = a / b
        assert result >= 0, "Postcondition failed: result must be non-negative"  # Postcondition
        return result

    # Example usage of the divide function
    try:
        print(divide(10, 2))  # This will work and print 5.0
        print(divide(10, 0))  # This will raise an assertion error due to the precondition
    except AssertionError as e:
        print(f"Assertion error: {e}")

In Java, you can use assertions to check for conditions at runtime by using the assert keyword. For example:

.. code-block:: java

    public class Main {
        public static void main(String[] args) {
            int a = 10;
            int b = 0;

            assert b != 0 : "Precondition failed: denominator must not be zero"; // Precondition
            int result = a / b; // This will throw an ArithmeticException if b is zero
            assert result >= 0 : "Postcondition failed: result must be non-negative"; // Postcondition

            System.out.println(result);
        }
    }

For contracts, you can use design by contract principles to define the expected behavior of methods and classes, and you can use tools such as JML (Java Modeling Language) for Java or PyContracts for Python to specify contracts in a more formal way. By using contracts and assertions effectively, developers can create more robust and maintainable code that adheres to the intended design and can catch errors early in the development process. 

.. code-block:: java

    // Example of using JML for design by contract in Java
    public class Calculator {
        //@ requires b != 0; // Precondition: denominator must not be zero
        //@ ensures \result >= 0; // Postcondition: result must be non-negative
        public int divide(int a, int b) {
            return a / b; // This will throw an ArithmeticException if b is zero
        }
    }

.. code-block:: python

    # Example of using PyContracts for design by contract in Python
    from contracts import contract

    @contract
    def divide(a: int, b: int) -> int:
        """Divide two integers with preconditions and postconditions."""
        assert b != 0, "Precondition failed: denominator must not be zero"  # Precondition
        result = a // b
        assert result >= 0, "Postcondition failed: result must be non-negative"  # Postcondition
        return result

Modern OOP extensions
---------------------

In modern object-oriented programming, there are several extensions and features that have been introduced to enhance the capabilities of OOP languages and to provide developers with more tools for writing efficient and maintainable code. Some of these modern OOP extensions include: 

- **Annotations:** Annotations are a way to provide metadata about code elements such as classes, methods, and fields. They can be used for various purposes, such as documentation, code analysis, and runtime processing. Annotations allow developers to add additional information to their code without affecting its functionality, making it easier to understand and maintain.
- **Reflection:** Reflection is a feature that allows a program to inspect and modify its own structure and behavior at runtime. This can be useful for tasks such as dynamically loading classes, invoking methods, and accessing fields. Reflection provides a powerful way to create flexible and adaptable code, but it should be used with caution as it can lead to performance issues and security vulnerabilities if not used properly.
- **Generics:** Generics are a feature that allows developers to create classes, interfaces, and methods that can operate on different types of data while providing type safety. Generics enable code reuse and can help to reduce the need for type casting, making code more readable and maintainable. They are commonly used in collections and data structures to allow for type-safe operations on different types of objects.
- **Dependency injection:** Dependency injection is a design pattern that allows for the decoupling of components in a software system by injecting dependencies into a class rather than having the class create its own dependencies. This promotes loose coupling and makes it easier to test and maintain code, as dependencies can be easily swapped out or mocked during testing.
- **Inversion of control:** Inversion of control (IoC) is a design principle that refers to the reversal of the flow of control in a software system. Instead of a class controlling its own dependencies and behavior, control is inverted and delegated to an external entity, such as a framework or container. This allows for greater flexibility and modularity in code, as it promotes separation of concerns and makes it easier to manage dependencies and interactions between components. 

Annotations
^^^^^^^^^^^

Annotations are a way to provide metadata about code elements such as classes, methods, and fields. They can be used for various purposes, such as documentation, code analysis, and runtime processing. Annotations allow developers to add additional information to their code without affecting its functionality, making it easier to understand and maintain. In Java, annotations are defined using the @interface keyword and can be applied to various code elements using the @ symbol. In Python, annotations can be added using decorators or by using type hints to provide information about the expected types of function parameters and return values.

.. code-block:: java

    // Example of using annotations in Java
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface MyAnnotation {
        String value(); // Define an annotation with a value element
    }

    public class MyClass {
        @MyAnnotation("This is a custom annotation") // Apply the annotation to a method
        public void myMethod() {
            // Method implementation
        }
    }   

.. code-block:: python  

    # Example of using annotations in Python
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            print("This is a custom annotation")  # Add metadata or behavior to the function
            return func(*args, **kwargs)
        return wrapper

    @my_decorator  # Apply the decorator as an annotation to the function
    def my_function():
        print("This is the original function.")

    my_function()  # This will print the annotation message followed by the original function message

Reflection
^^^^^^^^^^

Reflection is a feature that allows a program to inspect and modify its own structure and behavior at runtime. This can be useful for tasks such as dynamically loading classes, invoking methods, and accessing fields. Reflection provides a powerful way to create flexible and adaptable code, but it should be used with caution as it can lead to performance issues and security vulnerabilities if not used properly. In Java, reflection is provided through the java.lang.reflect package, while in Python, reflection can be achieved using built-in functions such as getattr(), setattr(), and the inspect module.

.. code-block:: java

    // Example of using reflection in Java
    import java.lang.reflect.Method;

    public class Main {
        public static void main(String[] args) {
            try {
                Class<?> clazz = Class.forName("MyClass"); // Dynamically load the MyClass
                Method method = clazz.getMethod("myMethod"); // Get the myMethod from MyClass   
                method.invoke(clazz.newInstance()); // Invoke the myMethod on an instance of MyClass
            } catch (Exception e) {
                e.printStackTrace(); // Handle any exceptions that may occur
            }
        }
    }

.. code-block:: python

    // Example of using reflection in Python
    class MyClass:
        def my_method(self):
            print("This is my_method in MyClass.")

    # Dynamically load the MyClass and invoke my_method
    class_name = "MyClass"
    method_name = "my_method"
    clazz = globals()[class_name]  # Get the class from the global namespace
    method = getattr(clazz(), method_name)  # Get the method from the class instance
    method()  # Invoke the method, which will print the message from my_method

Generics
^^^^^^^^

Generics are a feature that allows developers to create classes, interfaces, and methods that can operate on different types of data while providing type safety. Generics enable code reuse and can help to reduce the need for type casting, making code more readable and maintainable. They are commonly used in collections and data structures to allow for type-safe operations on different types of objects. In Java, generics are implemented using angle brackets (<>), while in Python, generics can be achieved using type hints and the typing module.

.. code-block:: java

    // Example of using generics in Java
    public class Box<T> {
        private T content; // Generic type parameter

        public void setContent(T content) {
            this.content = content; // Set the content of the box
        }

        public T getContent() {
            return content; // Get the content of the box
        }
    }

    public class Main {
        public static void main(String[] args) {
            Box<String> stringBox = new Box<>(); // Create a box for strings
            stringBox.setContent("Hello, Generics!"); // Set the content of the string box
            System.out.println(stringBox.getContent()); // Output: Hello, Generics!

            Box<Integer> integerBox = new Box<>(); // Create a box for integers
            integerBox.setContent(42); // Set the content of the integer box
            System.out.println(integerBox.getContent()); // Output: 42
        }
    }

.. code-block:: python

    # Example of using generics in Python with type hints
    from typing import TypeVar, Generic

    T = TypeVar('T')  # Define a generic type variable

    class Box(Generic[T]):
        def __init__(self):
            self.content: T = None  # Initialize content with the generic type

        def set_content(self, content: T) -> None:
            self.content = content  # Set the content of the box

        def get_content(self) -> T:
            return self.content  # Get the content of the box

    string_box = Box[str]()  # Create a box for strings
    string_box.set_content("Hello, Generics!")  # Set the content of the string box
    print(string_box.get_content())  # Output: Hello, Generics!

Dependency injection
^^^^^^^^^^^^^^^^^^^^

Dependencies are objects or components that a class relies on to perform its functionality. In object-oriented programming, managing dependencies is crucial for creating modular and maintainable code. One common approach to managing dependencies is through the use of dependency injection, which allows for the decoupling of components in a software system by injecting dependencies into a class rather than having the class create its own dependencies. This promotes loose coupling and makes it easier to test and maintain code, as dependencies can be easily swapped out or mocked during testing. In Java, dependency injection can be implemented using frameworks such as Spring or Guice, while in Python, it can be achieved using libraries such as dependency-injector or by manually passing dependencies through constructors or function parameters.

Dependency injection is a design pattern that allows for the decoupling of components in a software system by injecting dependencies into a class rather than having the class create its own dependencies. This promotes loose coupling and makes it easier to test and maintain code, as dependencies can be easily swapped out or mocked during testing. In Java, dependency injection can be implemented using frameworks such as Spring or Guice, while in Python, it can be achieved using libraries such as dependency-injector or by manually passing dependencies through constructors or function parameters.

Dependency injection can be implemented in various ways, including constructor injection (where dependencies are provided through the class constructor), setter injection (where dependencies are provided through setter methods), and interface injection (where dependencies are provided through an interface). By using dependency injection, developers can create more modular and flexible code that is easier to test and maintain, as it allows for the separation of concerns and promotes the use of interfaces and abstractions. For example, in Java, you can use constructor injection with the Spring framework like this:

.. code-block:: java

    // Example of using dependency injection with Spring in Java
    @Component
    public class MyService {
        private final MyRepository repository; // Dependency to be injected

        @Autowired
        public MyService(MyRepository repository) {
            this.repository = repository; // Constructor injection of the dependency
        }

        public void performAction() {
            repository.doSomething(); // Use the injected dependency
        }
    }

    @Component
    public class MyRepository {
        public void doSomething() {
            // Implementation of the repository method
        }
    }

.. code-block:: python

    # Example of using dependency injection in Python
    class MyService:
        def __init__(self, repository):
            self.repository = repository  # Constructor injection of the dependency

        def perform_action(self):
            self.repository.do_something()  # Use the injected dependency

    class MyRepository:
        def do_something(self):
            # Implementation of the repository method
            pass

    # Manually injecting the dependency
    repository = MyRepository()  # Create an instance of the repository
    service = MyService(repository)  # Inject the repository into the service
    service.perform_action()  # Call a method on the service that uses the injected dependency

Inversion of control
^^^^^^^^^^^^^^^^^^^^

Control is a fundamental principle in software design that refers to the flow of execution in a program. In traditional programming, the flow of control is typically determined by the program itself, with the main function or entry point controlling the execution of the program. However, in object-oriented programming, there is a design principle called inversion of control (IoC) that refers to the reversal of the flow of control in a software system. Instead of a class controlling its own dependencies and behavior, control is inverted and delegated to an external entity, such as a framework or container. This allows for greater flexibility and modularity in code, as it promotes separation of concerns and makes it easier to manage dependencies and interactions between components. Inversion of control can be implemented using various techniques, such as dependency injection, event-driven programming, and service locators. By using inversion of control, developers can create more flexible and adaptable code that can easily accommodate changes in requirements and promote better separation of concerns. For example, in Java, you can use the Spring framework to implement inversion of control like this:

.. code-block:: java

    // Example of using inversion of control with Spring in Java
    @Component
    public class MyService {
        private final MyRepository repository; // Dependency to be injected

        @Autowired
        public MyService(MyRepository repository) {
            this.repository = repository; // Constructor injection of the dependency
        }

        public void performAction() {
            repository.doSomething(); // Use the injected dependency
        }
    }

    @Component
    public class MyRepository {
        public void doSomething() {
            // Implementation of the repository method
        }
    }

.. code-block:: python

    # Example of using inversion of control in Python
    class MyService:
        def __init__(self, repository):
            self.repository = repository  # Constructor injection of the dependency

        def perform_action(self):
            self.repository.do_something()  # Use the injected dependency

    class MyRepository:
        def do_something(self):
            # Implementation of the repository method
            pass

    # Manually injecting the dependency
    repository = MyRepository()  # Create an instance of the repository
    service = MyService(repository)  # Inject the repository into the service
    service.perform_action()  # Call a method on the service that uses the injected dependency

