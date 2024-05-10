# LangChainBitcoin

`LangChainBitcoin` is a suite of tools that enables `langchain` agents to
directly interact with Bitcoin and also the Lightning Network. This package has
two main features:
  
  * **LLM Agent BitcoinTools**: Using the newly available Open AP GPT-3/4
    function calls and the built in set of abstractions for tools in
    `langchain`, users can create agents that are capaable of holding Bitcoin
    balance (on-chain and on LN), sending/receiving Bitcoin on LN, and also
    generally interacting with a Lightning node (lnd).

  * **L402 HTTP API Traversal**: LangChainL402 is a Python project that enables
    users of the `requests` package to easily navigate APIs that require
    [L402](https://docs.lightning.engineering/the-lightning-network/l402) based
    authentication. This project also includes a LangChain APIChain compatible
    wrapper that enables LangChain agents to interact with APIs that require
    L402 for payment or authentication. This enables agents to access
    real-world resources behind a Lightning metered API.


## Features
- Provides a wrapper around `requests` library to handle LSATs and Lightning
  payments.

- Easily integrates with APIs requiring L402-based authentication.

- Designed to operate seamlessly with LND (Lightning Network Daemon).

- Enables LangChain Agents traverse APIs that require L402 authentication
  within an API Chain.

- Generic set of Bitcoin tools giving agents the ability to hold and use the
  Internet's native currency.



## Installation

To install the LangChainL402 project, you can clone the repository directly
from GitHub:

```bash
git clone https://github.com/lightninglabs/LangChainBitcoin.git
cd LangChainBitcoin
```

Please ensure you have all the necessary Python dependencies installed. You can
install them using pip:
```
pip install -r requirements.txt
```

## Usage

### LLM Agent Bitcoin Tools

Check out the contained Jupyter notebook for an interactive example you can
run/remix: [LLM Bitcoin Tools](llm_bitcoin_tools.ipynb).

### L402 API Traversal

Check out the contained Jupyter notebook for an interactive example you can
run/remix: [LangChain402](langchain_L402_agent.ipynb).

This project provides classes to handle Lightning payments (e.g., `LndNode`,
`LightningNode`) and to manage HTTP requests with L402-based authentication
(`RequestsL402Wrapper`, `ResponseTextWrapper`).

First, initialize the `LndNode` with your Lightning node's details. Then, you
can use the modified `L402APIChain` wrapper around the normal `APIChain` class
to instantiate an L402-aware API Chain. If the server responds with a 402
Payment Required status code, the library will automatically handle the payment
and retry the request.

Here is a basic example:
```python
import requests

from lightning import LndNode

from l402_api_chain import L402APIChain
from langchain_openai import OpenAI

# Initialize LndNode
Add node data to the .env.shared file

# Add API data
Specifics of the serivce to be used can be added to API_DOCS via utils.py

# Instruction the AI agent
Instructions can be delivered to the AI agent via agent_executor.invoke main.py
```
