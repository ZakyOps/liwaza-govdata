FROM node:20-slim AS build

WORKDIR /app
ARG VITE_BACKEND_URL=http://localhost:8000
ARG VITE_API_KEY=
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
ENV VITE_API_KEY=$VITE_API_KEY
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
