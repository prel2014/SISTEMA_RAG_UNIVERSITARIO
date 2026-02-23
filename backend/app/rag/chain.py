from langchain_ollama import ChatOllama
from flask import current_app
from app.rag.retriever import retrieve_context
from app.rag.prompts import rag_prompt, reflection_prompt, suggestion_prompt


def _get_llm(streaming=False):
    return ChatOllama(
        model=current_app.config['LLM_MODEL'],
        base_url=current_app.config['OLLAMA_BASE_URL'],
        temperature=current_app.config.get('RAG_TEMPERATURE', 0.3),
        num_ctx=current_app.config.get('RAG_NUM_CTX', 4096),
        streaming=streaming,
    )


def _format_history(conversation_history):
    if not conversation_history:
        return ''
    lines = ['HISTORIAL PREVIO:']
    for msg in conversation_history:
        prefix = 'Usuario' if msg['role'] == 'user' else 'Asistente'
        lines.append(f"{prefix}: {msg['content'][:300]}")
    lines.append('')
    return '\n'.join(lines) + '\n'


def _generate_suggestions(question: str) -> str:
    """Llama al LLM (temp=0.0, no streaming) para generar sugerencias adaptadas."""
    llm = ChatOllama(
        model=current_app.config['LLM_MODEL'],
        base_url=current_app.config['OLLAMA_BASE_URL'],
        temperature=0.0,
        num_ctx=current_app.config.get('RAG_NUM_CTX', 4096),
    )
    chain = suggestion_prompt | llm
    result = chain.invoke({'question': question})
    return result.content


def _check_relevance(context: str, question: str) -> str:
    """Self-RAG: devuelve 'SUFICIENTE', 'PARCIAL' o 'INSUFICIENTE'."""
    llm = ChatOllama(
        model=current_app.config['LLM_MODEL'],
        base_url=current_app.config['OLLAMA_BASE_URL'],
        temperature=0.0,
        num_ctx=1024,
    )
    chain = reflection_prompt | llm
    result = chain.invoke({'question': question, 'context': context[:3000]})
    verdict = result.content.strip().upper()
    if 'SUFICIENTE' in verdict:
        return 'SUFICIENTE'
    if 'PARCIAL' in verdict:
        return 'PARCIAL'
    return 'INSUFICIENTE'


def get_rag_response(question, category_id=None, conversation_history=None):
    context, sources = retrieve_context(question, category_id=category_id)

    if not context:
        return {'answer': _generate_suggestions(question), 'sources': []}

    # Optional Self-RAG reflection
    if current_app.config.get('RAG_ENABLE_REFLECTION', False):
        verdict = _check_relevance(context, question)
        if verdict == 'INSUFICIENTE':
            return {'answer': _generate_suggestions(question), 'sources': []}
        # PARCIAL: continue — LLM will note limitations using available context

    llm = _get_llm(streaming=False)
    chain = rag_prompt | llm
    response = chain.invoke({
        'context': context,
        'question': question,
        'history': _format_history(conversation_history),
    })

    return {
        'answer': response.content,
        'sources': sources,
    }


def get_rag_response_stream(question, category_id=None, conversation_history=None):
    context, sources = retrieve_context(question, category_id=category_id)

    if not context:
        yield {'type': 'sources', 'sources': []}
        yield {'type': 'token', 'content': _generate_suggestions(question)}
        return

    # Optional Self-RAG reflection
    if current_app.config.get('RAG_ENABLE_REFLECTION', False):
        verdict = _check_relevance(context, question)
        if verdict == 'INSUFICIENTE':
            yield {'type': 'sources', 'sources': []}
            yield {'type': 'token', 'content': _generate_suggestions(question)}
            return

    # Sources always before tokens
    yield {'type': 'sources', 'sources': sources}

    llm = _get_llm(streaming=True)
    chain = rag_prompt | llm

    for chunk in chain.stream({
        'context': context,
        'question': question,
        'history': _format_history(conversation_history),
    }):
        if chunk.content:
            yield {'type': 'token', 'content': chunk.content}
