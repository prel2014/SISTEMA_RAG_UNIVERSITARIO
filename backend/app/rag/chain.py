from langchain_ollama import ChatOllama
from flask import current_app
from app.rag.retriever import retrieve_context
from app.rag.prompts import rag_prompt


def _get_llm(streaming=False):
    return ChatOllama(
        model=current_app.config['LLM_MODEL'],
        base_url=current_app.config['OLLAMA_BASE_URL'],
        temperature=current_app.config.get('RAG_TEMPERATURE', 0.3),
        num_ctx=current_app.config.get('RAG_NUM_CTX', 4096),
        streaming=streaming,
    )


def get_rag_response(question, category_id=None):
    context, sources = retrieve_context(question, category_id=category_id)

    if not context:
        return {
            'answer': 'No encontre informacion relevante sobre tu pregunta en los documentos disponibles. '
                      'Te sugiero consultar directamente con la oficina correspondiente de la UPAO '
                      'o reformular tu pregunta.',
            'sources': [],
        }

    llm = _get_llm(streaming=False)
    prompt_text = rag_prompt.format(context=context, question=question)
    response = llm.invoke(prompt_text)

    return {
        'answer': response.content,
        'sources': sources,
    }


def get_rag_response_stream(question, category_id=None):
    context, sources = retrieve_context(question, category_id=category_id)

    if not context:
        yield {
            'type': 'token',
            'content': 'No encontre informacion relevante sobre tu pregunta en los documentos disponibles. '
                       'Te sugiero consultar directamente con la oficina correspondiente de la UPAO '
                       'o reformular tu pregunta.'
        }
        yield {'type': 'sources', 'sources': []}
        return

    # Send sources first
    yield {'type': 'sources', 'sources': sources}

    # Stream LLM response
    llm = _get_llm(streaming=True)
    prompt_text = rag_prompt.format(context=context, question=question)

    for chunk in llm.stream(prompt_text):
        if chunk.content:
            yield {'type': 'token', 'content': chunk.content}
