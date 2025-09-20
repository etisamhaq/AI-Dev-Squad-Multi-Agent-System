#!/bin/bash

# Start Coral Server for AI Dev Squad
# This script starts the Coral Server with the correct configuration

echo "🚀 Starting Coral Server for AI Dev Squad..."

# Check if Java is installed (required for Coral Server)
if ! command -v java &> /dev/null; then
    echo "❌ Java is not installed. Installing OpenJDK..."
    sudo apt-get update
    sudo apt-get install -y openjdk-11-jdk
fi

# Set configuration paths
export CONFIG_FILE_PATH="$(pwd)/coral/config.toml"
export REGISTRY_FILE_PATH="$(pwd)/coral/registry.toml"

# Check if Coral Server is already downloaded
if [ ! -d "coral-server-repo" ]; then
    echo "📦 Coral Server not found. Cloning repository..."
    git clone https://github.com/Coral-Protocol/coral-server.git coral-server-repo
fi

cd coral-server-repo

# Build Coral Server if not already built
if [ ! -f "build/libs/coral-server.jar" ]; then
    echo "🔨 Building Coral Server..."
    ./gradlew build
fi

# Run Coral Server
echo "✅ Starting Coral Server on port 5555..."
echo "📁 Config: $CONFIG_FILE_PATH"
echo "📁 Registry: $REGISTRY_FILE_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

./gradlew run