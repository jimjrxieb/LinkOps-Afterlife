# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage with Caddy
FROM caddy:2-alpine
COPY --from=build /app/dist /srv
# Simple Caddyfile for serving static files
RUN printf ":8080 {\n\troot * /srv\n\tfile_server\n\ttry_files {path} /index.html\n}\n" > /etc/caddy/Caddyfile
EXPOSE 8080