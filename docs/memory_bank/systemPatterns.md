# System Patterns: Application for following websites for new offers

## System Architecture
- Clean Architecture: Business logic is independent of frameworks and delivery mechanisms
- Application Service Layer: Pure Python, all business logic, no Telegram dependencies
- Adapter Layer: Connects Telegram API (and other delivery mechanisms) to application services
- Adapter Pattern: For integrating with Telegram, email, etc.
- Dependency Inversion: Core logic depends on abstractions, not concrete implementations

## Key Technical Decisions
- Use of service and adapter layers

## Design Patterns in Use

## Component Relationships

## Critical Implementation Paths
