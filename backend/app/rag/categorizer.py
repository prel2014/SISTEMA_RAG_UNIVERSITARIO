import json


def auto_categorize(text_sample, title, categories, app):
    """
    Clasifica un documento en una categoría usando el LLM.
    Retorna el category_id detectado o None si no es posible clasificar.
    """
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage

    valid_ids = {cat['id'] for cat in categories}
    cat_list = '\n'.join(
        f"- ID: {cat['id']} | Nombre: {cat['name']}"
        + (f" | Descripción: {cat.get('description', '')}" if cat.get('description') else '')
        for cat in categories
    )

    system_msg = SystemMessage(content=(
        'Eres un clasificador de documentos académicos universitarios. '
        'Debes responder ÚNICAMENTE con un objeto JSON válido, sin markdown ni texto adicional.'
    ))
    human_msg = HumanMessage(content=(
        f'TÍTULO DEL DOCUMENTO: {title}\n\n'
        f'CONTENIDO (primeros 2000 caracteres):\n{text_sample}\n\n'
        f'CATEGORÍAS DISPONIBLES:\n{cat_list}\n\n'
        'Elige la categoría más adecuada para este documento. '
        'Si ninguna categoría aplica, usa "ninguna". '
        'Responde SOLO con este JSON:\n'
        '{"category_id": "<id exacto de la categoría o ninguna>"}'
    ))

    try:
        llm = ChatOllama(
            model=app.config.get('LLM_MODEL', 'gemma3:4b'),
            base_url=app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
            temperature=0.0,
            num_ctx=1024,
        )

        response = llm.invoke([system_msg, human_msg])
        content = response.content.strip()

        # Intento 1: JSON directo
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = None

        # Intento 2: bloque entre triple backticks
        if parsed is None and '```' in content:
            start = content.find('```') + 3
            if content[start:start + 4].lower() == 'json':
                start += 4
            end = content.find('```', start)
            if end != -1:
                try:
                    parsed = json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass

        if parsed is None:
            return None

        detected_id = parsed.get('category_id', '').strip()
        if detected_id and detected_id in valid_ids:
            print(f'[AutoCategorize] doc="{title}" -> category={detected_id}')
            return detected_id

        return None

    except Exception as e:
        print(f'[AutoCategorize error] {e}')
        return None
