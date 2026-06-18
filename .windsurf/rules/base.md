---
trigger: always_on
---

# Rule: Clean Code Principles and Project Workflow

You must follow these core principles and workflow rules to ensure maintainable, readable, and effective code.

## Core Principles

- **KISS (Keep It Simple, Stupid):** Prioritize simplicity. Avoid unnecessary complexity in all solutions.
- **YAGNI (You Aren't Gonna Need It):** Only implement what is needed now. Do not add speculative features or abstractions.
- **SRP (Single Responsibility Principle):** Each component, function, or class should have one clear responsibility.
- **DRY (Don't Repeat Yourself):** Avoid unnecessary duplication, but only when it improves clarity.

### Balancing Principles

- Apply SRP only when it simplifies code or addresses a real need; avoid over-engineering.
- Use abstraction only when it genuinely reduces complexity or repetition.
- Refactor for clarity, not for the sake of abstraction.

## Coding Style

- Write code that is easy to read and understand.
- Use meaningful, descriptive names for variables, functions, and classes.
- Keep functions short and focused on a single task.
- Prefer explicit, straightforward solutions over clever or obscure ones.
- Add comments only where intent is not obvious.
- Include meaningful logs that aid debugging and provide context, but avoid excessive noise.

## Problem-Solving Approach

1. Understand the problem thoroughly before coding.
2. Start with the simplest working solution.
3. Refactor only when necessary for clarity or maintainability.
4. Add logging to help with troubleshooting and monitoring.
5. Handle edge cases and errors thoughtfully.

## Project Workflow Requirements

### Getting Started

- Record the session start timestamp in the format `yyyy-MM-dd_hh-mm`.

### Planning and Documentation

- Store all documentation in the `docs` directory.
- Before coding, create `docs/plan/plan-{timestamp}.md` with the session plan.
- Use the plan to generate a detailed task list in `docs/plan/tasks-{timestamp}.md`.
- Create or update `docs/plan.md` with improvements.
- Use `[ ]` and `[x]` for task completion status.
- Critically review plans and tasks against **KISS, YAGNI, SRP, DRY** before implementation.
- Request user review and approval for the plan and task list before generating code.

### Implementation Process

- Follow the documented task list.
- Mark tasks as completed `[x]` as you soon as you complete each of them. This is very important!
- Implement only one task at a time.
- Implement only what is in the plan.
- Check for existing solutions before adding new code.
- Commit all work to the branch upon completion.
- Replace deprecated APIs with modern alternatives.
- After implementing all changes run `just autoformatters` to auto format the code. 

---

**Remember:** Code is written for humans to read and only incidentally for machines to execute.
