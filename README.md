# Model Context Protocol (MCP) Setup

This is a complete, minimal, production-quality project demonstrating the execution of tools via Model Context Protocol (MCP) using an LLM to dynamically decide and execute reasoning.

## 🔄 Project Flow
User input → LLM → tool selection → MCP call → MCP server tool execution → tool response → final LLM response → terminal output

## 📁 Files

- `server.py`: The MCP server that registers and exposes Python tools via SSE transport.
- `client.py`: The client that uses the OpenRouter LLM to dynamically invoke tools from the MCP server.
- `.env`: A private file storing the required LLM API key.
- `requirements.txt`: The required dependencies for the project.

## 🛠️ Setup Instructions

1. **Install dependencies**. Make sure you are using Python 3.10+, create a virtual environment, and install the libraries:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify your API key**. The `.env` file contains your OpenRouter API Key.

## 🚀 Running the Project

You will need **two terminal tabs/windows** to run the system.

**Terminal 1: Start the MCP Server**
```bash
python server.py
```
> Let this run. It powers the external MCP server locally.

**Terminal 2: Start the Client**
```bash
python client.py
```
> The client will connect to the server, discover tools, and wait for your input.

## 🧪 Example Queries to Try

When you see the `You: ` prompt in the client, test the system by typing these exact commands:
- *"add 5 and 3"*
- *"multiply 4 and 6"*
- *"greet Mayuresh"*

You will see the console log tracking the execution exactly when the model realizes it needs a tool, forwards the query to the MCP Server, invokes the correct logic, and returns your final output.

## ⚙️ Tech Stack
- Python
- Model Context Protocol (MCP)
- OpenRouter (LLM)
- AsyncIO

## 🎯 Purpose
This project demonstrates how LLMs can dynamically decide and execute external tools using MCP.