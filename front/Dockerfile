FROM node:20-alpine

WORKDIR /app

COPY front/package*.json ./
RUN npm install

COPY front/ .

RUN npm run build

WORKDIR /app/out/

CMD [ "echo", "frontend", "builder", "stops" ]

