"""
Prompts for XOFlowers Conversational AI
This module defines the system and user prompts used to guide the
Large Language Model (LLM) in generating helpful and natural responses.
"""

from typing import List, Dict, Any
from .conversation_context import ConversationSession

def get_system_prompt() -> str:
    """
    Returns the system prompt that defines the AI's persona and instructions.
    """
    return """
Tu ești un asistent virtual expert în flori pentru XOFlowers, o florărie premium din Chișinău, Moldova.
Misiunea ta este să oferi o experiență de cumpărături excepțională, personalizată și prietenoasă.

**Instrucțiuni cheie:**
1.  **Fii un expert florar:** Oferă sfaturi competente despre flori, aranjamente și ocazii. Cunoști semnificația florilor și poți recomanda buchete pentru orice eveniment.
2.  **Ton prietenos și natural:** Comunică într-un stil cald, empatic și conversațional. Evită răspunsurile robotice. Adresează-te clientului cu "dumneavoastră" sau "tu", în funcție de cum inițiază conversația.
3.  **Fii proactiv și ajutător:** Anticipează nevoile clientului. Dacă un client caută ceva, pune întrebări de clarificare pentru a oferi cele mai bune recomandări (ex: "Pentru ce ocazie căutați florile?", "Aveți un buget anume?").
4.  **Integrează produsele natural:** Când prezinți produse, fă-o într-un mod fluid și conversațional. Nu lista doar produsele. Descrie-le atractiv și explică de ce sunt o alegere bună.
5.  **Gestionează contextul:** Fii atent la istoricul conversației pentru a oferi răspunsuri relevante și personalizate.
6.  **Limba:** Răspunde întotdeauna în limba română.
"""

def get_user_prompt(session: ConversationSession) -> str:
    """
    Constructs the user prompt based on the current conversation session.

    Args:
        session: The current conversation session.

    Returns:
        The user prompt to be sent to the LLM.
    """
    # Build the conversation history string
    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in session.messages])

    # Build the search results string if available
    search_results_str = "Niciun produs găsit."
    if session.current_search_context and session.current_search_context.get("results"):
        search_results_str = "Am găsit următoarele produse care s-ar potrivi:\n"
        for res in session.current_search_context["results"]:
            search_results_str += f"- **{res['name']}** ({res['price']} MDL): {res.get('document', '')}\n"

    return f"""
**Istoricul Conversației:**
{history_str}

**Rezultate Căutare Produse (dacă este cazul):**
{search_results_str}

**Instrucțiune:**
Pe baza conversației de mai sus și a rezultatelor căutării, generează un răspuns natural și ajutător pentru client.
"""