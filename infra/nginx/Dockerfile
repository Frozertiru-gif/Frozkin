FROM node:20-alpine AS webbuild

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

FROM nginx:1.25
COPY infra/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=webbuild /app/dist /usr/share/nginx/html
