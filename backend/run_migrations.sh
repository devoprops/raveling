#!/bin/bash
set -e

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Run database migrations
echo "Running database migrations..."
uv run alembic upgrade head

echo "Migrations completed successfully!"
