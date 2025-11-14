# Multi-stage build for Template Service
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json ./

# Install dependencies
RUN pnpm install

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json ./

# Install only production dependencies
RUN pnpm install --prod

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3001

# Start the application
CMD ["node", "dist/main"]