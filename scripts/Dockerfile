FROM postgres:15-alpine

# Install required tools
RUN apk add --no-cache bash

# Copy setup script
COPY setup-databases.sh /setup-databases.sh
RUN chmod +x /setup-databases.sh

# Set entrypoint
ENTRYPOINT ["/setup-databases.sh"]