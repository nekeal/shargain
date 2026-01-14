# Tech Stack

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | | | | |
| Language | TypeScript | `<5.9.0` | Provides static typing for JavaScript. | Enhances code quality, readability, and developer experience. |
| Framework | React | `^19.0.0` | A JavaScript library for building user interfaces. | Component-based architecture and vast ecosystem make it ideal for SPAs. |
| UI Components | shadcn/ui | `latest` | A collection of reusable components built with Radix UI and Tailwind CSS. | Provides accessible, unstyled components that are easy to customize. |
| State Mgmt | TanStack Query | `^5.84.1` | Manages server state, including caching, refetching, and mutations. | Simplifies data fetching and state synchronization with the backend API. |
| CSS Framework | Tailwind CSS | `^4.1.11` | A utility-first CSS framework for rapid UI development. | Allows for building custom designs without leaving your HTML. |
| Build Tool | Vite | `^6.3.5` | A modern frontend build tool that provides an extremely fast development experience. | Offers near-instant server start and Hot Module Replacement (HMR). |
| Testing | Vitest | `^3.0.5` | A fast and modern testing framework for Vite projects. | Seamless integration with Vite and a familiar Jest-like API. |
| **Backend** | | | | |
| Language | Python | `>=3.13` | A high-level, general-purpose programming language. | Strong ecosystem for web development, data science, and more. |
| Framework | Django | `~5.0` | A high-level Python web framework that encourages rapid development. | "Batteries-included" philosophy provides many features out of the box. |
| API Style | Django Ninja | `latest` | A fast, async-ready, and type-hint based API framework for Django. | Enables building modern, OpenAPI-compliant APIs with Pydantic-style schemas. |
| Async Tasks | Celery | `latest` | A distributed task queue for processing asynchronous jobs. | Essential for offloading long-running tasks from the main web thread. |
| **Database** | | | | |
| Main Database | PostgreSQL | `13-alpine` | A powerful, open-source object-relational database system. | Known for its reliability, feature robustness, and performance. |
| Message Broker| RabbitMQ | `latest` | A robust and widely used open-source message broker. | Reliably handles message queuing for Celery's distributed tasks. |
| Cache | Django Cache | `N/A` | Django's built-in caching framework (e.g., in-memory). | Provides basic caching. Can be swapped for Redis if needed. |
| **Infrastructure**| | | | |
| File Storage | Local Filesystem | `N/A` | Stores user-uploaded media on the server's disk. | Simple for development. Recommend AWS S3 for production scalability. |
| Authentication | Django Auth + django-allauth | `latest` | Handles user registration, login, and session management, including OAuth2. | Combines Django's robust system with `django-allauth`'s comprehensive social authentication support. |
| IaC Tool | Docker Compose | `latest` | A tool for defining and running multi-container Docker applications. | Simplifies container orchestration for local development and production. |
| CI/CD | GitHub Actions | `N/A` | Automates the build, test, and deployment pipeline. | Tightly integrated with the GitHub repository for seamless workflow management. |
| Monitoring | Sentry | `latest` | Error tracking and performance monitoring. | Provides real-time insight into application errors and performance. |
| **Testing** | | | | |
| Backend | Pytest | `latest` | A mature, feature-rich testing framework for Python. | Enables writing simple, scalable tests from small units to complex functions. |
| E2E | TBD | `N/A` | End-to-end testing framework. | Recommendation: Playwright for its modern features and cross-browser support. |
