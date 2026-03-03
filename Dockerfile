# Use lightweight Python base
FROM python:3.9-alpine

# Create a non-root user
RUN adduser -D -u 54000 radio

# Install build dependencies for pip packages
RUN apk add --no-cache git gcc musl-dev bash

# Create application directory and set ownership
RUN mkdir -p /opt/hblink3 && chown radio:radio /opt/hblink3

WORKDIR /opt/hblink3

# Copy application code
COPY --chown=radio:radio . .

# Copy entrypoint and set permissions
COPY --chown=radio:radio entrypoint /entrypoint
RUN dos2unix /entrypoint && chmod +x /entrypoint

# Install Python dependencies, then remove build dependencies to shrink image
RUN pip install --no-cache-dir -r requirements.txt \
    && apk del git gcc musl-dev

# Switch to non-root user
USER radio

# Use entrypoint
ENTRYPOINT ["/entrypoint"]