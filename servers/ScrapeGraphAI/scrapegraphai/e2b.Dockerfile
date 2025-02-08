FROM e2bdev/code-interpreter:latest

# Install UV tool
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV tool to PATH
ENV PATH="/root/.local/bin/:$PATH"

# Clone the repository
RUN git clone https://github.com/mkinf-io/mkinf-mcp-servers

# Extract only the right mcp server
RUN mv mkinf-mcp-servers/servers/ScrapeGraphAI/scrapegraphai ./

# Change directory and run UV sync
WORKDIR scrapegraphai

RUN uv sync

