FROM e2bdev/code-interpreter:latest

# Install UV tool
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV tool to PATH
ENV PATH="/root/.local/bin/:$PATH"

# Clone the repository
RUN git clone https://github.com/mkinf-io/mkinf-mcp-servers

# Change directory and run UV sync
WORKDIR mkinf-mcp-servers

# Checkout only the repo folder
RUN git sparse-checkout init --cone
RUN git sparse-checkout set servers/cyclotruc/gitingest
RUN git checkout main

RUN uv sync

