FROM ghcr.io/astral-sh/uv:alpine

ARG COMPOSE_BAKE=true

# Set working directory
WORKDIR /app

# Set correct timezone
ENV TZ=Europe/Berlin

# Install runtime dependencies only
RUN apk add --no-cache \
    libffi \
    openssl \
    curl \
    git \
    tzdata && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy application files
COPY . .

# Set default command
CMD ["uv", "run", "main.py"]
