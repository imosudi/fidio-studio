FROM node:20-alpine AS builder

WORKDIR /app

COPY apps/web/package*.json ./
RUN npm ci --silent || npm install

COPY apps/web/ .
RUN npm run build || true

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "start"]
