from langchain_core.runnables.utils import Output
from lightning import LndNode
from all_tools.bitcoin_tools import LndTools
from L402 import L402APIChain
from langchain import hub
from all_tools import api_tools
from langchain.schema import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.schema.runnable import RunnableMap
from dotenv import dotenv_values

config = dotenv_values(".env.shared")


class LLMUtils:
    lnd_node: LndNode

    def __init__(self, lnd_node: LndNode):
        self.lnd_node = lnd_node
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    def api_chain_factory(self, api_docs: str, api_host: str):
        api_chain = L402APIChain.from_llm_and_api_docs(
            self.llm,
            api_docs,
            lightning_node=self.lnd_node,
            verbose=True,
            limit_to_domains=[api_host, "localhost"],
        )
        return api_chain

    def get_target_api_chain(self) -> L402APIChain:

        target_host = config.get("TARGET_HOST", "unknown_host")
        API_DOCS = f"""BASE URL: {target_host}
      
        API Documentation
        The API endpoint /quote/ can be used to fetch inspirational quotes. Currenttly 5 quotes are availalble 1 through 5. 
      
        Request:
        The number of the meme or quote needs to be included in the URL, example /quote/2. 
      
        Response:
        The response from the /quote/ endpoint is text. 
        """
        target_api_chain = self.api_chain_factory(
            api_docs=API_DOCS, api_host=target_host
        )
        return target_api_chain

    def get_target_api_tool(self):
        name = config.get("API_TOOL_NAME", "Default api tool name")
        description = config.get("API_TOOL_DESCRIPTION", "Default api tool description")
        target_api_chain = self.get_target_api_chain()
        target_api_tool = api_tools.api_tool_factory(
            api_chain=target_api_chain, name=name, description=description
        )
        return target_api_tool

    def _get_agent_executor(self, tools):
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(llm=self.llm, prompt=prompt, tools=tools)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        return agent_executor

    def get_lnd_agent_executor(self):
        lnd_tools = LndTools.from_lnd_node(lnd_node=self.lnd_node).get_tools()
        agent_executor = self._get_agent_executor(tools=lnd_tools)
        return agent_executor

    def get_entry_point(self, additional_tools):
        lnd_tools = LndTools.from_lnd_node(lnd_node=self.lnd_node).get_tools()
        all_tools = lnd_tools + additional_tools
        agent_executor = self._get_agent_executor(tools=all_tools)
        return agent_executor

    def get_entry_point_v2(self):
        prompt = PromptTemplate.from_template(
            """If the input is about payments, balance, general info of specific  Lighting node, respond with `LND`. If the input is about general info of Lighting node technology, Bitcoin or blockchain in general, respond with `BLOCKCHAIN`.
          If the input is about  retreaving API data, respond with `API`. If the input is about the functionality if this tool or how this tool may help user, respond with `FAQ`. Otherwise, respond `OTHER`
        
        Question: {question}"""
        )

        blockchain_llm_chain = (
            PromptTemplate.from_template(
                """You are an expert in Blockchain technology.You have hure experience with Bitcoin and Lighting Network. Respond to the question:
      
        Question: {input}"""
            )
            | ChatOpenAI()
            | StrOutputParser()
        )
        target_host = config.get("TARGET_HOST", "missed")

        faq_str = f"""You are a tool designed to help users communicate with Lighting Network that is on top of the bitcoin blockchain. Also you are able to communicate with some websites API. One of them is: `{target_host}`. On this website you can find API data and services. You can also find other information. Respond with information about your features.
        """
        faq_llm_chain = (
            PromptTemplate.from_template(
                faq_str
                + """
      
        Question: {input}"""
            )
            | ChatOpenAI()
            | StrOutputParser()
        )

        general_llm_chain = (
            PromptTemplate.from_template(
                f"""Respond that you dont have answer for user query and provide information about your features based on this text: ###{faq_str}###
      
        Question: {input}"""
            )
            | ChatOpenAI()
            | StrOutputParser()
        )

        router_chain = prompt | ChatOpenAI() | StrOutputParser()

        target_api_chain = self.get_target_api_chain()
        agent_executor = self.get_lnd_agent_executor()

        # Add the routing logic - use the action key to route
        def select_chain(output):
            if output["action"] == "LND":
                return agent_executor
            elif output["action"] == "OTHER":
                return general_llm_chain
            elif output["action"] == "FAQ":
                return faq_llm_chain
            elif output["action"] == "BLOCKCHAIN":
                return blockchain_llm_chain
            elif output["action"] == "API":
                return target_api_chain
            else:
                raise ValueError

        chain = (
            RunnableMap(
                {"action": router_chain, "input": {"question": lambda x: x["question"]}}
            )
            | select_chain
        )

        return chain


if __name__ == "__main__":
    lnd_node = LndNode(
        cert_path="/home/runner/L402-LangChainBitcoin-Bitcoind-LND/tls.cert",
        macaroon_path="/home/runner/L402-LangChainBitcoin-Bitcoind-LND/admin.macaroon",
        host="lang-chain-bitcoin-testing.t.voltageapp.io",
        port=10009,
    )
    llm_utils = LLMUtils(lnd_node=lnd_node)
    entry_point = llm_utils.get_entry_point_v2()
    result = entry_point.invoke(
        {"question": "How many channels does my node have open?"}
    )
    print(f"LND result: {result}")

    result = entry_point.invoke("How can you help me?")
    print(f"\nFAQ result: {result}")

    result = entry_point.invoke(
        {"question": "Purchase quote #2"}
    )  # Will fail with an error: `ValueError: Missing some input keys: {'question'}`
    print(f"\nQuote result: {result}")
