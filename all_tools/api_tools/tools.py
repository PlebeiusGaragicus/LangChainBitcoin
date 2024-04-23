from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool, tool

from protos import lightning_pb2 as ln
from langchain.chains import APIChain

from typing import List


class APITools(BaseToolkit):
    class Config:
        arbitrary_types_allowed = True

    memes_api_chain: APIChain

    @classmethod
    def from_api_chains(cls, memes_api_chain: APIChain):
        return cls(memes_api_chain=memes_api_chain)

    def _make_memes_api_request_tool(self):
        @tool
        def make_memes_api_request(query: str) -> str:
            """
            Makes Purchases of memes, and quotes by Communicating with website API `https://memes.innovativecommercegroup.com/`.
            """
            return self.memes_api_chain.invoke(query)

        return make_memes_api_request

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""

        tools = []

        for attribute_name in dir(self):
            if attribute_name.endswith("_tool"):
                attribute = getattr(self, attribute_name)

                if attribute is None:
                    continue

                tool_func = attribute()

                if tool_func is None:
                    continue

                if callable(attribute):
                    tools.append(attribute())

        return tools
