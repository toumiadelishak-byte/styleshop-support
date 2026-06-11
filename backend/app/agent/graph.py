from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from app.config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
    LLM_MAX_RETRIES,
)
from app.agent.prompt import SYSTEM_PROMPT

class EtatAgent(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

_llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    timeout=LLM_TIMEOUT,
    max_retries= LLM_MAX_RETRIES,
    api_key= OPENAI_API_KEY # type: ignore
)

def noeud_agent(etat: EtatAgent) -> dict:
    messages_avec_contexte = (
        [SystemMessage(content=SYSTEM_PROMPT)]
        + etat["messages"]
    )

    reponse_llm = _llm.invoke(messages_avec_contexte)

    return {
        "messages": [reponse_llm]
    }

def construire_graphe():
    graphe = StateGraph(EtatAgent)

    graphe.add_node("agent", noeud_agent)

    graphe.add_edge(START, "agent")
    graphe.add_edge("agent", END)



    return graphe.compile()

agent_graphe = construire_graphe()