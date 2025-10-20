ARG BUILD_UPSTREAM_REPO
ARG BUILD_UPSTREAM_REPO_BRANCH

# Use a Debian Bookworm base image with necessary dependencies pre-installed
FROM docker.io/luisbandalap/debian-bookworm:latest

# Create user tgbot with sudo privileges
RUN addgroup --gid 1001 tgbot && \
    useradd --no-log-init --uid 1001 --shell /bin/bash -g tgbot -G root,sudo --create-home tgbot

# Allow passwordless sudo for tgbot user
RUN echo "tgbot ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER tgbot

# Set environment variables for userbot
ENV UPSTREAM_REPO=$BUILD_UPSTREAM_REPO \
    UPSTREAM_REPO_BRANCH=$BUILD_UPSTREAM_REPO_BRANCH \
    VENV_PATH=/home/tgbot/userbot-venv \
    CHROME_BIN=/usr/bin/chromium \
    ENV=True

# Create and activate virtual environment
RUN mkdir -p $VENV_PATH && \
    python -m venv $VENV_PATH

# Copy userbot source code
COPY --chown=tgbot:tgbot ./ /home/tgbot/userbot/

WORKDIR /home/tgbot/userbot

# Install Python dependencies inside the virtual environment
RUN $VENV_PATH/bin/pip install --no-cache-dir --upgrade setuptools wheel && \
    $VENV_PATH/bin/pip install --no-cache-dir --upgrade PyDictionary lxml_html_clean && \
    $VENV_PATH/bin/pip install --no-cache-dir -r requirements.txt && \
    $VENV_PATH/bin/pip install --no-cache-dir --upgrade yt-dlp-ejs yt-dlp[default,curl-cffi] && \
    rm -rf /tmp/* && \
    rm -rf /home/tgbot/userbot/.cache/*    

# Set tini as the entrypoint for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Set the default command to run the userbot
CMD ["/home/tgbot/userbot-venv/bin/python", "-m", "userbot"]
