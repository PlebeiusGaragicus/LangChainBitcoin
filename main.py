import os
from dotenv import dotenv_values
from lightning import LndNode
from utils import LLMUtils

config = {**dotenv_values(".env.shared"), **dotenv_values(".env.secret"), **os.environ}

os.environ["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY", "missed")

lnd_node = LndNode(
    cert_path=config.get("CERT_PATH", "missed"),
    macaroon_path=config.get("MACAROON_PATH", "missed"),
    host=config.get("LND_NODE_HOST", "missed"),
    port=config.get("LND_NODE_PORT", "0"),
)

llm_utils = LLMUtils(lnd_node=lnd_node)
target_api_tool = llm_utils.get_target_api_tool()
agent_executor = llm_utils.get_entry_point(additional_tools=[target_api_tool])

# Invoke with query related to the api
# api_output = agent_executor.invoke({"input": "Purchase quote #3"})
# Invoke with query related to lnd node
lnd_output = agent_executor.invoke({"input": "How many open channels do I have?"})
# print(f"API resp:\n`{api_output['output']}`")
# print(f"LND resp:\n`{lnd_output['output']}`")
