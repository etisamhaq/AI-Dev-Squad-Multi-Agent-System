FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production || npm install

# Copy application files
COPY . .

# Build the application
RUN npm run build || echo "Build step skipped"

EXPOSE 3000

CMD ["npm", "start"]