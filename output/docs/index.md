# Airline Management System - Documentation

## Overview
This project is a desktop-based Airline Management System developed in Java. Analysis of the source code reveals a comprehensive application designed to handle core airline operations through a graphical user interface (GUI). The system facilitates passenger management, flight booking, ticket cancellation, and information retrieval. It directly interacts with a MySQL database to persist and manage all data, making it a classic example of a database-driven desktop application built using the Java Swing framework.

## Project Statistics
- **Total Files**: 13
- **Programming Languages**: Java, XML, properties
- **Last Updated**: 2024-05-23

## Technology Stack
- **Programming Language**:
    - **Java**: The core language used for the application's logic and structure.
- **User Interface**:
    - **Java Swing**: The primary framework used to build the graphical user interface (GUI) components, windows, and event handling.
- **Database**:
    - **MySQL**: The backend relational database used for storing all application data, including passenger details, flight information, and reservations. The connection string `jdbc:mysql:///airlinemanagementsystem` confirms its use.
    - **JDBC (Java Database Connectivity)**: The standard Java API used to connect and execute queries against the MySQL database. The `com.mysql.cj.jdbc.Driver` is explicitly loaded.
- **Development Environment**:
    - **Apache NetBeans**: The project is structured as a NetBeans project, indicated by the `nbproject` directory and associated XML configuration files.
- **Third-Party Libraries**:
    - **JCalendar (jcalendar-1.4.jar)**: Provides the `JDateChooser` component, a Swing widget used for easy date selection in the flight booking interface.
    - **RS2XML (rs2xml.jar)**: Contains the `net.proteanit.sql.DbUtils` utility, which is used to efficiently populate `JTable` components directly from a JDBC `ResultSet` in modules like `FlightInfo` and `JourneyDetails`.

## Architecture Overview
The application follows a monolithic architecture typical for desktop applications. It can be logically separated into three layers:
1.  **Presentation Layer**: Comprises all the Java Swing classes (`Home`, `AddCustomer`, `BookFlight`, etc.) that create the user interface. Each class represents a specific window or screen.
2.  **Business Logic Layer**: The logic is tightly coupled with the presentation layer within the `actionPerformed` event listeners. These methods handle user input, validate data, and orchestrate calls to the data access layer.
3.  **Data Access Layer**: A centralized `ConnDB.java` class manages the JDBC connection to the MySQL database. SQL queries are embedded directly within the methods of the presentation layer classes to perform CRUD (Create, Read, Update, Delete) operations.

## Documentation Navigation
- 📐 [Architecture](./architecture.md) - System design and components
- 🗄️ [Database](./database.md) - Data models and relationships
- 🏗️ [Classes](./classes.md) - Code structure and components  
- 🌐 [Web](./web.md) - API endpoints and web interfaces

## Getting Started

### Prerequisites
1.  **Java Development Kit (JDK)**: Version 8 or higher.
2.  **MySQL Server**: A running instance of MySQL database.
3.  **Apache NetBeans IDE**: Recommended for opening and running the project seamlessly.
4.  **Required Libraries**: `jcalendar-1.4.jar` and `rs2xml.jar`.

### Database Setup
1.  Start your MySQL server.
2.  Create a new database named `airlinemanagementsystem`.
   ```sql
   CREATE DATABASE airlinemanagementsystem;
   ```
3.  Connect to the database and create the necessary tables. The schemas can be inferred from the SQL queries in the Java files (e.g., `passenger`, `flight`, `reservation`, `cancel`).
4.  Ensure the database credentials in `src/airlinemanagementsystem/ConnDB.java` match your MySQL setup (default is user: `root`, password: `root`).
   ```java
   // From ConnDB.java
   c = DriverManager.getConnection("jdbc:mysql:///airlinemanagementsystem", "root", "root");
   ```

### Running the Application
1.  Clone or download the project source code.
2.  Open the project in Apache NetBeans IDE (`File -> Open Project`).
3.  Add the `jcalendar-1.4.jar` and `rs2xml.jar` files to the project's libraries/classpath.
4.  Locate the `Home.java` file, which is the main entry point of the application.
5.  Right-click on `Home.java` and select "Run File" to launch the application.

## Key Features
- **Customer Management**: Provides a dedicated interface (`AddCustomer.java`) to add new passengers to the system with details like name, aadhar number, address, and gender.
- **Flight Booking**: Allows users to book flights (`BookFlight.java`) by first fetching passenger details via Aadhar number, selecting a source and destination, and then creating a reservation with a unique PNR.
- **Ticket Cancellation**: Users can cancel an existing reservation (`Cancel.java`) by providing the PNR number. The system logs the cancellation and removes the booking.
- **Flight Information**: A screen (`FlightInfo.java`) displays a table of all available flights, showing details fetched directly from the database.
- **Journey Details Lookup**: Users can retrieve and view the complete details of a specific booking (`JourneyDetails.java`) using its PNR number.
- **Boarding Pass Generation**: A simple boarding pass (`BoardingPass.java`) can be generated and displayed on-screen by entering a valid PNR number.

## Project Structure
```
AirlineManagementSystem/
├── nbproject/           # NetBeans IDE project configuration files
│   ├── private/         # User-specific project metadata
│   └── project.xml      # Main project definition for NetBeans
├── src/
│   └── airlinemanagementsystem/ # Main package for all source code
│       ├── icons/             # Directory for UI icons and images
│       ├── AddCustomer.java   # GUI for adding a new passenger
│       ├── BoardingPass.java  # GUI for displaying a boarding pass
│       ├── BookFlight.java    # GUI for booking a flight ticket
│       ├── Cancel.java        # GUI for cancelling a reservation
│       ├── ConnDB.java        # Central class for database connection
│       ├── FlightInfo.java    # GUI to display all flight information
│       ├── Home.java          # Main application window with menu navigation
│       └── JourneyDetails.java# GUI to show details of a specific journey
└── build.xml            # Ant build script (auto-generated by NetBeans)
```