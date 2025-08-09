The project uses ESLint for linting and Prettier for formatting. The `lint:fix` script can be used to automatically fix linting errors. The `make autoformatters` command should be run after implementing all changes to auto format the code.

For project structure, we ensure high cohesion. This means that all files related to a specific feature (components, hooks, types, etc.) should be grouped together in a dedicated folder. So in components folder when some component grows, convert it to a folder and split it into multiple files.
