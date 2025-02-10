FROM e2bdev/code-interpreter:latest

# Clone the repository
RUN git clone https://github.com/mkinf-io/mkinf-mcp-servers

# Extract only the right mcp server
RUN mv mkinf-mcp-servers/servers/modelcontextprotocol/github ./

# Change directory and run UV sync
WORKDIR github

RUN npm install
RUN npm run build
