FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Recibir el ARG en build time
ARG VITE_BACKEND_URL=http://localhost:8000

# Convertirlo en ENV para que esté disponible en runtime
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}

# Expose port
EXPOSE 5173

# Run development server
CMD ["npm", "run", "dev", "--", "--host"]
