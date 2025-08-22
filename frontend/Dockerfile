# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy dependency definition files
COPY package.json pnpm-lock.yaml ./

RUN --mount=type=cache,target=/pnpm/store pnpm install --frozen-lockfile

COPY src/ ./src
COPY public/ ./public
COPY ["index.html", ".env.production", "vite.config.ts", "tsconfig.json", "tailwind.config.ts", "eslint.config.js", "components.json", "./"]

# Build the application
RUN pnpm build

# Stage 2: Production environment
FROM nginx:1.25-alpine

# Copy the built static files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
