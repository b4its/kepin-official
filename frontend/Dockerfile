FROM node:22-alpine

ARG PUBLIC_API_URL=http://localhost:8000/api/v1
ENV PUBLIC_API_URL=$PUBLIC_API_URL

WORKDIR /app

# Pin versi pnpm via corepack agar build reproducible. `npm install -g pnpm`
# menarik versi terbaru (floating) yang rentan SIGSEGV (exit 139) pada
# node:*-alpine (musl) saat dijalankan di dalam BuildKit.
ARG PNPM_VERSION=10.15.1
RUN corepack enable && corepack prepare "pnpm@${PNPM_VERSION}" --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN pnpm install --ignore-scripts --frozen-lockfile

COPY . .
RUN pnpm build

EXPOSE 3000

CMD ["node", "build/index.js"]
