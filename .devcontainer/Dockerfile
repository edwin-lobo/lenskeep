FROM python:3.13.5-slim

# --- base deps (incl. tools needed to create users) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git \
    passwd sudo \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libxshmfence1 fonts-liberation libcurl4 libpci3 \
    libwayland-client0 libwayland-server0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# --- install uv system-wide ---
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && uv --version

# --- create non-root user with stable UID/GID ---
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

# Create group if needed, or reuse existing GID
RUN if getent group ${USER_GID} >/dev/null; then \
      groupmod -n ${USERNAME} $(getent group ${USER_GID} | cut -d: -f1); \
    else \
      groupadd --gid ${USER_GID} ${USERNAME}; \
    fi && \
    useradd -m -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# optional: prepare playwright cache dir owned by user
ENV PLAYWRIGHT_BROWSERS_PATH=/home/${USERNAME}/.cache/ms-playwright
RUN mkdir -p ${PLAYWRIGHT_BROWSERS_PATH} && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

# switch to user
USER ${USERNAME}
WORKDIR /workspace
