from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas import ChatRequest,ChatResponse
import logging
from langchain_core.messages import HumanMessage
from app.agent.graph import agent_graphe
from app.config import MAX_MESSAGES_HISTORIQUE, LLM_TIMEOUT, OPENAI_API_KEY
import asyncio

from collections import defaultdict
from openai import (
    RateLimitError,
    AuthenticationError,
    APIError,
)
from contextlib import asynccontextmanager


historiques_sessions = defaultdict(list)


app= FastAPI(title='SupportAgent API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.post("/chat", response_model=ChatResponse)
async def chat(requete: ChatRequest):

    session_id = requete.session_id

    historique = historiques_sessions[session_id]

    historique.append(
        HumanMessage(content=requete.message)
    )

    if len(historique) > MAX_MESSAGES_HISTORIQUE:
        historique[:] = historique[-MAX_MESSAGES_HISTORIQUE:]

    try:
        resultat = await asyncio.wait_for( agent_graphe.ainvoke(
            {
                "messages": historique
            }
        ),
        timeout = LLM_TIMEOUT +5,
        )

        reponse_msg = resultat["messages"][-1]

        historique.append(reponse_msg)

        return ChatResponse(
            response=reponse_msg.content,
            session_id=session_id,
        )
    except asyncio.TimeoutError:
        logger.warning(
            f"Timeout session {session_id}"
        )
        return ChatResponse(
            response="je mets un peu trop de temps a repondre. Veuillez reessayer.",
            session_id=session_id
        )
    except RateLimitError:
        logger.error("Quota openAI depasse")
        raise HTTPException(
            status_code=429,
            detail="Service temporairement indisponible. Reesayez dans quelques minutes."

        )
    except AuthenticationError:
        logger.critical(
            "Cle API OpenAI invalide !"
        )
        raise HTTPException(
            status_code=500,
            detail="Erreur de config serveur"
        )
    except APIError as e:
        logger.error(
            f"Erreur API OpenAI : {e}"
        )
        return ChatResponse(
            response = " Une erreur temporaire s'est produite. Veuillez reessayer.",
            session_id=session_id
        )
    except Exception as e:
        logger.error(
            f"Erreur inattendue : {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur."
        )
    
@asynccontextmanager
async def lifespan(app:FastAPI):
    if not OPENAI_API_KEY:
        logger.critical(
            "ERREUR : OPENAI_API_KEY manquante !"
        )
        raise RuntimeError(
            "OPENAI_APIKEY non configure."
        )
    logger.info(
        "StyleShop Support api demarre"
    )
    logger.info(
        f"Modele LLM : gpt-4o-mini | Timeout : {LLM_TIMEOUT}"
    )
    yield

    logger.info(
        " StyleShop Support API  arretee"
    )

@app.get('/health')
async def health_check():
    return {
        'status' : 'ok',
        'timesstamp' : datetime.now().isoformat(),
        'version' : '1.0.0'
    }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)