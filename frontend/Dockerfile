FROM node:22-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --ignore-scripts

COPY . .
RUN pnpm build

RUN ls -la

EXPOSE 3000

CMD ["node", "build/index.js"]
