# Airline Management System - Documentation

## Overview
The Airline Management System is a Java-based desktop application designed to manage airline operations, including flight details, customer information, booking, and ticket cancellation. The system features a graphical user interface (GUI) with a menu-driven interface, allowing users to navigate through various functions.

## Project Statistics
- **Total Files**: 15
- **Programming Languages**: Java, XML, Properties
- **Last Updated**: [Current Date]

## Technology Stack
- Java ( Swing, AWT, SQL)
- XML
- Properties

## Architecture Overview
The system follows a modular architecture, with separate classes for each functional component, such as `AddCustomer`, `BookFlight`, `FlightInfo`, and `Cancel`. The application uses a database connection class (`ConnDB`) to interact with the database.

## Documentation Navigation
- 📐 [Architecture](./architecture.md) - System design and components
- 🗄️ [Database](./database.md) - Data models and relationships
- 🏗️ [Classes](./classes.md) - Code structure and components  
- 🌐 [Web](./web.md) - API endpoints and web interfaces (Not applicable in this case)

## Getting Started
1. Clone the repository: `git clone AirlineManagementSystem`
2. Navigate to the project directory: `cd AirlineManagementSystem`
3. Compile the Java files: `javac *.java` (assuming you're in the `src/airlinemanagementsystem` directory)
4. Run the application: `java Home`

## Key Features
- Add Customer Details
- Flight Details
- Book Flight
- Journey Details
- Cancel Ticket
- Boarding Pass

## Project Structure
```
AirlineManagementSystem/
bproject/
private/
config.properties
project.xml
private.xml
src/
airlinemanagementsystem/
AddCustomer.java
BoardingPass.java
BookFlight.java
Cancel.java
ConnDB.java
FlightInfo.java
Home.java
JourneyDetails.java
Login.java
icons/
front.jpg
```

## External Integrations or Tools
- Database ( likely MySQL or another relational database management system, but the specific database is not mentioned)
- Java Swing and AWT libraries for GUI development

Note that some sections, such as `architecture.md`, `database.md`, `classes.md`, and `web.md`, are not created as part of this index.md file, but they can be created separately to provide more detailed information about the respective topics.