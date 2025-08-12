FROM node:18 AS build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Install TailwindCSS in the container
RUN npm install -D tailwindcss postcss autoprefixer react-markdown

# Generate Tailwind + PostCSS configs if not already present
# (Only runs if tailwind.config.js doesn't exist in project)
RUN [ ! -f tailwind.config.js ] && npx tailwindcss init -p || echo "Tailwind config already exists"

# Build the React app
RUN npm run build

# Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
