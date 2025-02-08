FROM e2bdev/code-interpreter:latest

# Install UV tool
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV tool to PATH
ENV PATH="/root/.local/bin/:$PATH"

# Install Rust and Cargo
RUN apt-get update && apt-get install -y curl build-essential
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone the repository
RUN git clone https://github.com/mkinf-io/mkinf-mcp-servers

# Extract only the right mcp server
RUN mv mkinf-mcp-servers/servers/ScrapeGraphAI/scrapegraphai ./

# Change directory and run UV sync
WORKDIR scrapegraphai

RUN uv sync

# Install playwright
RUN uv pip install playwright
RUN uv run playwright install
RUN uv run playwright install-deps

