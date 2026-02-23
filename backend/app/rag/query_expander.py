import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from flask import current_app


def expand_query(question: str) -> list[str]:
    """
    Genera hasta 2 reformulaciones alternativas de la pregunta para ampliar el recall.
    Siempre retorna una lista que incluye la pregunta original.
    Falla silenciosamente: retorna [question] si el LLM o el parsing falla.
    """
    if not current_app.config.get('RAG_ENABLE_QUERY_EXPANSION', True):
        return [question]

    try:
        llm = ChatOllama(
            model=current_app.config['LLM_MODEL'],
            base_url=current_app.config['OLLAMA_BASE_URL'],
            temperature=0.0,
            num_ctx=512,
        )
        system = SystemMessage(content=(
            'Eres un asistente que reformula preguntas académicas en español. '
            'Responde ÚNICAMENTE con un JSON válido, sin markdown ni texto adicional.'
        ))
        human = HumanMessage(content=(
            f'Genera 2 reformulaciones alternativas de esta pregunta para mejorar '
            f'la búsqueda en documentos universitarios. Usa sinónimos o perspectivas '
            f'distintas pero mantén el mismo significado.\n'
            f'Pregunta original: {question}\n\n'
            'Responde solo con este JSON:\n'
            '{"queries": ["reformulacion1", "reformulacion2"]}'
        ))

        response = llm.invoke([system, human])
        content = response.content.strip()

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(content[start:end])
            else:
                return [question]

        variants = [v.strip() for v in parsed.get('queries', []) if v and v.strip()]
        all_queries = [question]
        for v in variants:
            if v.lower() != question.strip().lower():
                all_queries.append(v)
        return all_queries[:3]  # original + máx 2 variantes

    except Exception as e:
        print(f'[QueryExpander error] {e}')
        return [question]
