import uuid
import requests
import streamlit as st

st.set_page_config(
    page_title="StyleShop | Support Client",
    page_icon="👗",
    layout="centered",
    initial_sidebar_state="expanded"
)

API_BASE_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_ok" not in st.session_state:
    st.session_state.api_ok = None

def appeler_api_chat(message: str, session_id : str) -> str :
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "session_id": session_id,
                "message": message,
            },
            timeout=90,
        )
        if response.status_code ==200 :
            return response.json()["response"]
        
        if response.status_code == 504 : 
            return "Timeout - reeassayer dans quelques instants."
    except requests.exceptions.ConnectionError:
        return "API non joignable. Lancez le serveur."
    except requests.exceptions.Timeout:
        return "Timeout"

def verifier_connexion_api() -> bool:
    try:
        r=requests.get(
            f"{API_BASE_URL}/health",
            timeout=4,
        )
        return r.status_code == 200
    except Exception:
        return False
    
def reinitialiser_conversation():
    st.session_state.messages = []
    st.session_state.session_id = (str(uuid.uuid4())[:8])
        

with st.sidebar:

    st.markdown("## Panneau de controle")
    if st.button(
        "Teste la connexion",
        use_container_width=True
    ):
        st.session_state.api_ok = (
            verifier_connexion_api()
        )
    if st.session_state.api_ok is True:
        st.success(" API Connectee")
    elif st.session_state.api_ok is False:
        st.error("API indisponible")
    
    st.divider()

    st.write(
        f"Session : {st.session_state.session_id}"
    )

    if st.button(
        "Nouvelle conversation",
        use_container_width=True
    ):
        reinitialiser_conversation()
        st.rerun()

exemples = [
    "Quel est le status de ma commande 2 ?",
    "Donne-moi les details de la commande 4",
    "Je veux changer l'adresse de la commande 3",
    "Quelle est votre politique de retour?",
    "Comment choisir ma taille pour un pull",
    "Quels moyens de paiment acceptez-vous ?"
]

with st.sidebar:
    st.divider(
    )
    st.markdown("### Questions exemples")

    for exemple in exemples:
        if st.button(exemple):
            st.session_state.exemple = exemple

st.markdown(
    """
    # StyleShop
    Assistant Support Client 
"""
)
if not st.session_state.messages:
    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):
        st.markdown(
            """Bonjour !
            Je suis **Alex**, votre assistant StyleShop.
            Comment puis-je vous aidez aujourd'hui ? """
        )

for message in st.session_state.messages:
    avatar=(
        "🧑"
        if message["role"] == "user"
        else "🤖"
    )
    with st.chat_message(
        message["role"],
        avatar=avatar
    ):
        st.markdown(
            message['content']
        )

user_input = st.chat_input(
    "Ecrivez votre message..."
)

if user_input:
    with st.chat_message(
        "user",
        avatar="🧑"
    ):
        st.markdown(user_input)
    
    st.session_state.messages.append(
        {
            "role" : "user",
            "content": user_input,
        }
    )
    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):
        with st.spinner(
            "Alex reflechit..."
        ):
            response = appeler_api_chat(
                user_input,
                st.session_state.session_id
            )
        st.markdown(response)
    st.session_state.messages.append(
        {
            "role":"assistant",
            "content": response
        }
    )