FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

ARG VITE_PUBLIC_APP_URL=https://calculadora-gcp.web.app
ARG VITE_API_BASE_URL=https://calculadora-gcp-backend-563306928786.us-central1.run.app
ENV VITE_PUBLIC_APP_URL=$VITE_PUBLIC_APP_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
