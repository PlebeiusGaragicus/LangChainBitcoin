from langchain_core.runnables.utils import Output
from lightning import LndNode
from all_tools.bitcoin_tools import LndTools
from all_tools.api_tools import APITools
from L402 import L402APIChain
from langchain import hub
from langchain.schema import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.schema.runnable import RunnableMap


def get_memes_api_chain(lnd_node: LndNode) -> L402APIChain:
    API_DOCS = """BASE URL: https://memes.innovativecommercegroup.com/
  
    API Documentation
    The API endpoint /quote/ can be used to fetch inspirational quotes. Currenttly 5 quotes are availalble 1 through 5. 
  
    Request:
    The number of the meme or quote needs to be included in the URL, example /quote/2. 
  
    Response:
    The response from the /quote/ endpoint is text. 
    """
    llm = OpenAI(temperature=0)

    memes_api_chain = L402APIChain.from_llm_and_api_docs(
        llm,
        API_DOCS,
        lightning_node=lnd_node,
        verbose=True,
        limit_to_domains=["https://memes.innovativecommercegroup.com", "localhost"],
    )
    return memes_api_chain


def get_lnd_agent_executor(lnd_node):
    lnd_tools = LndTools.from_lnd_node(lnd_node=lnd_node).get_tools()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = hub.pull("hwchase17/structured-chat-agent")
    agent = create_structured_chat_agent(llm=llm, prompt=prompt, tools=lnd_tools)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=lnd_tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def get_entry_point(lnd_node):
    memes_api_chain = get_memes_api_chain(lnd_node=lnd_node)
    lnd_tools = LndTools.from_lnd_node(lnd_node=lnd_node).get_tools()
    api_tools = APITools.from_api_chains(memes_api_chain=memes_api_chain).get_tools()
    all_tools = lnd_tools + api_tools

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = hub.pull("hwchase17/structured-chat-agent")
    agent = create_structured_chat_agent(llm=llm, prompt=prompt, tools=all_tools)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

    return agent_executor


def get_entry_point_v2(lnd_node):
    prompt = PromptTemplate.from_template(
        """If the input is about payments, balance, general info of specific  Lighting node, respond with `LND`. If the input is about general info of Lighting node technology, Bitcoin or blockchain in general, respond with `BLOCKCHAIN`.
      If the input is about  quotes or memes, respond with `MEMES`. If the input is about the functionality if this tool or how this tool may help user, respond with `FAQ`. Otherwise, respond `OTHER`
    
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

    faq_str = """You are a tool designed to help users communicate with Lighting Network that is on top of the bitcoin blockchain. Also you are able to communicate with some websites API. One of them is: `https://memes.innovativecommercegroup.com/`. On this website you can find memes. You can also find quotes and other information. Respond with information about your features.
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

    memes_api_chain = get_memes_api_chain(lnd_node=lnd_node)
    agent_executor = get_lnd_agent_executor(lnd_node)

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
        elif output["action"] == "MEMES":
            return memes_api_chain
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
    entry_point = get_entry_point_v2(lnd_node)
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
