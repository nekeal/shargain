# System Patterns: Application for following websites for new offers

## System Architecture
- Clean Architecture: Business logic is independent of frameworks and delivery mechanisms
- Application Service Layer: Pure Python, all business logic, no Telegram dependencies
- Adapter Layer: Connects Telegram API (and other delivery mechanisms) to application services
- Adapter Pattern: For integrating with Telegram, email, etc.
- Dependency Inversion: Core logic depends on abstractions, not concrete implementations

## Key Technical Decisions
- Strict separation of concerns between application logic and delivery mechanisms.
- Use of dependency inversion to decouple components.

## Error Handling
- **Structured Exceptions:** The application layer uses a set of custom, structured exceptions that inherit from a base `ApplicationException`.
- **Declarative Exceptions:** Each exception is a simple class with `code` and `message` defined as class attributes. This makes them easy to manage and consistent.
- **Instantiation:** Exceptions are raised without arguments (e.g., `raise TargetDoesNotExist()`), making the code cleaner.

## Design Patterns in Use

## Component Relationships
- **Telegram Handlers (Controller/Adapter):** Receive requests from the Telegram API.
- **Application Services:** Receive data from adapters, execute business logic.
- **`ActionResult`:** A data class used for standardized responses from services, indicating success or failure and carrying a message.

## Critical Implementation Paths
- The flow for handling a user command: Telegram Handler -> Adapter -> Application Service -> ActionResult -> Adapter -> Telegram Reply.
