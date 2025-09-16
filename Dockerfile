# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install curl for health checks
RUN apk add --no-cache curl

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build TypeScript to JavaScript
RUN npm run build

# Expose the application port (for documentation)
EXPOSE 8001

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD ["npm", "start"]