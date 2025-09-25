import os
from typing import Dict, Optional
from google import genai
from google.genai import types

# Previous Llama Scout implementation
"""
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

class LlamaScoutClient:
    def __init__(self, model: str = "meta/Llama-4-Scout-17B-16E-Instruct"):
        \"""Initialize GitHub Marketplace Llama-4-Scout client\"""
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(github_token),
        )
        self.model = model
    
    def call_llm(self, prompt: str, system_message: str = "You are a code documentation assistant.") -> str:
        \"""Make LLM API call with error handling.\"""
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(system_message),
                    UserMessage(prompt),
                ],
                model=self.model,
                top_p=0.9,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
"""

class LlamaScoutClient:
    def __init__(self, model: str = "gemini-2.5-pro"):
        """Initialize Gemini Pro client"""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def call_llm(self, prompt: str, system_message: str = "You are a code documentation assistant.") -> str:
        """Make LLM API call with error handling."""
        try:
            full_prompt = f"{system_message}\n\n{prompt}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                ),
            )

            return response.text.strip() if response.text else "No response text returned."
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_documentation(self, codebase_content: str, doc_type: str) -> str:
        """Generate specific documentation type using Llama-4-Scout"""
        
        system_messages = {
            'index': "You are a technical documentation expert specializing in project overviews and navigation.",
            'architecture': "You are a software architect specializing in system design documentation.",
            'database': "You are a database architect specializing in data model documentation.",
            'classes': "You are a code analyst specializing in class structure documentation.",
            'web': "You are a web API analyst specializing in interface documentation."
        }
        
        prompts = {
            'index': self._get_index_prompt(),
            'architecture': self._get_architecture_prompt(),
            'database': self._get_database_prompt(),
            'classes': self._get_classes_prompt(),
            'web': self._get_web_prompt()
        }
        
        system_message = system_messages.get(doc_type, system_messages['index'])
        prompt_template = prompts.get(doc_type, prompts['index'])
        
        full_prompt = f"{prompt_template}\n\nANALYZE THIS CODEBASE:\n\n{codebase_content}"
        
        return self.call_llm(full_prompt, system_message)
    
    def _get_index_prompt(self) -> str:
        return """Create a comprehensive index.md that serves as the main entry point for this codebase documentation.
 Try to give more concise information and along with detailed explanations instead of single line explanation.
REQUIREMENTS:
1. Analyze the actual codebase structure, files, and dependencies
2. Identify the real project purpose from code patterns and file names
3. Create accurate technology stack list from actual imports and package files
4. Generate real project statistics and features
5. Provide genuine getting started instructions
6. If there are any external or third-party integrations or tools used, mention them accurately

FORMAT:
# [Project Name] - Documentation

## Overview
[Real project description based on code analysis]

## Project Statistics
- **Total Files**: [actual count] 
- **Programming Languages**: [actual languages found]
- **Last Updated**: [current date]

## Technology Stack
[List actual technologies found in imports and config files]

## Architecture Overview
[Brief description of actual architecture pattern used]

## Documentation Navigation
- 📐 [Architecture](./architecture.md) - System design and components
- 🗄️ [Database](./database.md) - Data models and relationships
- 🏗️ [Classes](./classes.md) - Code structure and components  
- 🌐 [Web](./web.md) - API endpoints and web interfaces

## Getting Started
[Real commands based on package.json or setup files found]

## Key Features
[List actual features identified from code structure]

## Project Structure
```
[Real directory tree with key folders explained]
```

Base everything on actual code analysis, not generic templates."""

    def _get_architecture_prompt(self) -> str:
        return """Create detailed architecture.md documentation based on actual code analysis.
Try to give more concise information and along with detailed explanations instead of single line explanation.
Condition: Produce mermaid diagrams without syntax errors.
REQUIREMENTS:
1. Analyze real component relationships and dependencies
2. Identify actual architectural patterns used (MVC, Component-based, etc.)
3. Map real data flow between components
4. Create accurate Mermaid diagrams showing actual file relationships
5. Document real technology integrations found in code

GO through the mermaid syntax and check for any syntax errors. If there are any syntax errors, fix them.

FORMAT:
# System Architecture

## Architecture Overview
[Real architecture pattern based on code structure]

## Component Architecture
[Actual component hierarchy and relationships]

## System Flow
```mermaid
graph TD
    A[Main Entry] --> B[Core Components]
    B --> C[Feature Modules]
    C --> D[Services/APIs]
    D --> E[Data Layer]
    
    subgraph "Frontend"
        F[UI Components]
        G[State Management]
        H[Routing]
    end
    
    subgraph "Backend"
        I[API Services]
        J[Business Logic]
        K[Data Access]
    end
```

## Technology Integration
[How different technologies work together based on actual usage]

## Data Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database
    
    User->>Frontend: Interaction
    Frontend->>API: Request
    API->>Database: Query
    Database-->>API: Response
    API-->>Frontend: Data
    Frontend-->>User: Update
```

## Security Architecture
[Real authentication and authorization patterns found]

## Directory Structure
```
[Real directory tree with explanations of each major folder]
```

## Key Design Patterns
[Actual patterns identified in the code]

Create all diagrams based on REAL file relationships and imports found in the codebase."""

    def _get_database_prompt(self) -> str:
        return """Create database.md based on actual database usage patterns found in the code.
Condition: Produce mermaid diagrams without syntax errors.
Try to give more concise information and along with detailed explanations instead of single line explanation.
REQUIREMENTS:
1. Analyze actual API calls and database operations
2. Identify real data models from service files and schemas
3. Map actual relationships between entities
4. Create accurate ERD based on real usage patterns
5. Document actual database technology and configuration

GO through the mermaid syntax and check for any syntax errors. If there are any syntax errors, fix them.

FORMAT:
# Database Documentation

## Database Overview
[Real database technology identified from code]

## Data Models
[Actual entities/models found in code with their attributes]

## Entity Relationships
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    CATEGORY ||--o{ PRODUCT : contains
    
    USER {
        int id PK
        string email
        string name
        datetime created_at
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
        datetime created_at
    }
```

## API Integration
[How database integrates with application based on actual service files]

## Data Access Patterns
[Real patterns found in data access code - ORM, Query Builder, Raw SQL, etc.]

## Database Operations
[Actual CRUD operations found in service files]

## Configuration
[Real database configuration from config files]

Base all content on ACTUAL database usage patterns, API calls, and data structures found in the codebase."""

    def _get_classes_prompt(self) -> str:
        return """Create classes.md documenting the actual code structure and components.
Condition: Produce mermaid diagrams without syntax errors.
Try to give more concise information and along with detailed explanations instead of single line explanation.
REQUIREMENTS:
1. Analyze real classes, functions, and modules
2. Map actual inheritance and composition relationships
3. Document real component interfaces and props
4. Create accurate class diagrams based on actual code
5. Explain real design patterns used
6. Identify the type of inheritance or composition

GO through the mermaid syntax and check for any syntax errors. If there are any syntax errors, fix them.

FORMAT:
# Classes and Code Structure

## Component Overview
[Real components/classes found in codebase with descriptions]

Add all the methods and properties of the classes in the mermaid diagram below.
## Class Hierarchy
```mermaid
classDiagram
    class BaseClass {
        +method1()
        +method2()
    }
    
    class DerivedClass {
        +method3()
        +method4()
    }
    
    class UtilityClass {
        +staticMethod()
    }
    
    BaseClass <|-- DerivedClass
    DerivedClass --> UtilityClass : uses
```
A definition of the classes and their relationships based on actual code analysis. 
Example: is a relationship, has a relationship, what type of inheritance or composition.

## Key Components
[Actual important classes/components with their methods and properties]

## Inheritance and Composition
[Real inheritance and composition relationships found and classify what type of inheritance or composition it is]

## Interfaces and Contracts
[Real interfaces, props, and method signatures found in code]

## Design Patterns
[Actual patterns identified in the code structure - Singleton, Factory, Observer, etc.]

## Component Relationships
```mermaid
graph LR
    A[Main Component] --> B[Service Layer]
    B --> C[Data Layer]
    A --> D[Helper Classes]
    B --> E[External APIs]
```

## Module Dependencies
[Real dependencies and interactions between modules/components]

Document only REAL classes, functions, and components found in the actual codebase."""

    def _get_web_prompt(self) -> str:
        return """Create web.md documenting actual web interfaces and API endpoints.
Condition: Produce mermaid diagrams without syntax errors.
Try to give more concise information and along with detailed explanations instead of single line explanation.
Don't halucinate or fabricate any information. Instead give a confident and concise information.
REQUIREMENTS:
1. Analyze real API endpoints and routes
2. Document actual web components and pages
3. Map real user interface structure
4. Identify actual authentication and authorization
5. Document real API integration patterns

GO through the mermaid syntax and check for any syntax errors. If there are any syntax errors, fix them.
FORMAT:
# Web Components and APIs

## API Endpoints
[Real endpoints found in service files and route definitions]

### Authentication
- POST /auth/login
- POST /auth/register
- POST /auth/logout

### Core Resources
[Actual API endpoints with methods, parameters, and responses]

## Web Pages and Routes
[Actual pages and routing structure found in code]

## User Interface Flow
```mermaid
graph TD
    A[Landing Page] --> B{User Logged In?}
    B -->|No| C[Login Page]
    B -->|Yes| D[Dashboard]
    C --> E[Registration]
    C --> D
    D --> F[Feature Pages]
    F --> G[Profile/Settings]
```

## Component Architecture
```mermaid
graph TB
    subgraph "Frontend Components"
        H[App Component]
        I[Header/Navigation]
        J[Main Content]
        K[Footer]
        L[Modal/Dialog]
    end
    
    subgraph "Page Components"
        M[Dashboard]
        N[Profile]
        O[Settings]
    end
    
    H --> I
    H --> J
    H --> K
    J --> M
    J --> N
    J --> O
```

## Authentication Flow
[Real authentication implementation found in code]

## API Integration
[How frontend integrates with backend/APIs based on actual code]

## State Management
[Real state management patterns - Redux, Context, Local State, etc.]

## User Experience Flow
[Actual user journeys based on route and component analysis]

Base everything on ACTUAL API calls, routes, and web components found in the codebase."""
