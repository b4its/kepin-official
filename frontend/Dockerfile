FROM node:22-alpine

ARG PUBLIC_API_URL=http://localhost:8000/api/v1
ENV PUBLIC_API_URL=$PUBLIC_API_URL

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --ignore-scripts

COPY . .
RUN pnpm build

EXPOSE 3000

CMD ["node", "build/index.js"]
