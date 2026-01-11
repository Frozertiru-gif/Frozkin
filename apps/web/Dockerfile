FROM node:20-alpine

WORKDIR /app

COPY apps/web/package.json apps/web/package-lock.json ./

RUN npm config set registry https://registry.npmjs.org/ \
  && npm config set fetch-retries 5 \
  && npm config set fetch-retry-mintimeout 20000 \
  && npm config set fetch-retry-maxtimeout 120000 \
  && npm config set prefer-online true

RUN --mount=type=cache,target=/root/.npm \
  npm ci --no-audit --no-fund --verbose

COPY apps/web/ ./

RUN npm run build
