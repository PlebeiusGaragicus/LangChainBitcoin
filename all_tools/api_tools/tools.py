from dotenv import dotenv_values
from langchain.tools import StructuredTool
from langchain.chains import APIChain

config = dotenv_values(".env.shared")


def api_tool_factory(api_chain: APIChain, name: str, description: str):
    api_tool = StructuredTool.from_function(
        func=lambda query: api_chain.invoke(query),
        name=name,
        description=description,
        return_direct=True,
    )
    return api_tool
