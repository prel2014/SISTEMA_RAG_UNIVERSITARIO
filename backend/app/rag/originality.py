import json

from app.db import call_fn, get_conn_raw, put_conn_raw
from app.document_processing.processor import get_processor
from app.document_processing.chunker import chunk_text
from app.rag.embeddings import get_embeddings
import psycopg2.extras


BATCH_SIZE = 32


def _plagiarism_level_for_score(max_score):
    """Nivel de similitud de un chunk individual."""
    if max_score >= 0.85:
        return 'very_high'
    elif max_score >= 0.65:
        return 'high'
    elif max_score >= 0.50:
        return 'moderate'
    return 'low'


def _global_plagiarism_level(plagiarism_pct):
    """Nivel global a partir de % de plagiarismo (100 - originality_score)."""
    if plagiarism_pct >= 85:
        return 'very_high'
    elif plagiarism_pct >= 65:
        return 'high'
    elif plagiarism_pct >= 50:
        return 'moderate'
    return 'low'


def _analyze_with_llm(doc_title, sample_pairs, app):
    """Pide al LLM que identifique temas académicos en común entre los fragmentos."""
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage

    # Top 3 pairs por score descendente
    top_pairs = sorted(sample_pairs, key=lambda p: p['score'], reverse=True)[:3]

    thesis_samples = '\n\n'.join(
        f'[Fragmento {i+1}]: {p["thesis_text"]}' for i, p in enumerate(top_pairs)
    )
    doc_samples = '\n\n'.join(
        f'[Fragmento {i+1}]: {p["doc_content"]}' for i, p in enumerate(top_pairs)
    )

    system_msg = SystemMessage(content=(
        'Eres un evaluador académico. Analiza los fragmentos proporcionados y responde '
        'ÚNICAMENTE con un objeto JSON válido en español, sin markdown ni texto adicional.'
    ))
    human_msg = HumanMessage(content=(
        f'TESIS EN EVALUACIÓN (fragmentos más similares):\n{thesis_samples}\n\n'
        f'DOCUMENTO DE REFERENCIA: "{doc_title}"\n'
        f'Fragmentos similares:\n{doc_samples}\n\n'
        'Analiza los fragmentos e identifica coincidencias académicas. '
        'Devuelve SOLO este JSON sin markdown:\n'
        '{'
        '"common_themes": ["tema1", "tema2"], '
        '"technologies": ["tech1", "tech2"], '
        '"methods": ["metodo1", "metodo2"], '
        '"approach": "Una oración sobre el enfoque compartido.", '
        '"problem_overlap": "Una oración: ¿resuelven el mismo problema completo o partes distintas?", '
        '"analysis": "2-3 oraciones de análisis general de la coincidencia académica."'
        '}'
    ))

    llm = ChatOllama(
        model=app.config.get('LLM_MODEL', 'gemma3:4b'),
        base_url=app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
        temperature=0.1,
        num_ctx=2048,
    )

    response = llm.invoke([system_msg, human_msg])
    content = response.content.strip()

    # Intento 1: JSON directo
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Intento 2: bloque entre triple backticks
    if '```' in content:
        start = content.find('```') + 3
        # saltar "json" si está justo después
        if content[start:start+4].lower() == 'json':
            start += 4
        end = content.find('```', start)
        if end != -1:
            try:
                return json.loads(content[start:end].strip())
            except json.JSONDecodeError:
                pass

    # Fallback gracioso
    return {'common_themes': [], 'technologies': [], 'methods': [], 'approach': '', 'problem_overlap': '', 'analysis': content[:300]}


def run_originality_check(check_id, app):
    conn = get_conn_raw()
    try:
        _run(check_id, conn, app)
    finally:
        put_conn_raw(conn)


def _run(check_id, conn, app):
    try:
        record = call_fn('fn_get_thesis_check', (check_id,), fetch_one=True, conn=conn)
        if not record:
            raise ValueError(f'Verificacion no encontrada: {check_id}')

        threshold = float(record['score_threshold'])
        file_path = record['file_path']
        file_type = record['file_type']
        top_k_per_chunk = app.config.get('ORIGINALITY_TOP_K_PER_CHUNK', 3)

        call_fn('fn_update_thesis_check_status', (check_id, 'processing'), conn=conn)

        # 1. Extract text
        processor = get_processor(file_type)
        pages = processor.extract_text(file_path)

        # 2. Chunk text
        chunks = []
        for page_data in pages:
            for text in chunk_text(page_data['content']):
                if len(text.strip()) >= 50:
                    chunks.append({'text': text, 'page': page_data.get('page', 1)})

        if not chunks:
            raise ValueError('No se generaron chunks de la tesis.')

        texts = [c['text'] for c in chunks]
        total_chunks = len(texts)

        # 3. Embed in batches
        embeddings_model = get_embeddings()
        all_embeddings = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            all_embeddings.extend(embeddings_model.embed_documents(batch))

        # 4. Compare each chunk against indexed documents
        # Accumulate per document_id: max_score, list of scores, pages_hit set, chunk_hits, sample_pairs
        doc_stats = {}  # doc_id -> {title, category_id, scores[], pages_hit set, chunk_hits, sample_pairs[]}
        flagged_chunks = 0

        for idx, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
            results = call_fn(
                'fn_search_similar',
                (embedding, top_k_per_chunk, 0.35, '', True),
                fetch_all=True,
                conn=conn
            )
            if not results:
                continue

            top_result = results[0]
            top_score = float(top_result['score'])

            if top_score >= threshold:
                flagged_chunks += 1

            for row in results:
                doc_id = row['document_id']
                score = float(row['score'])
                page = int(row['page']) if row['page'] else 1
                title = row['title']
                category_id = row.get('category_id') or ''

                if doc_id not in doc_stats:
                    doc_stats[doc_id] = {
                        'title': title,
                        'category_id': category_id,
                        'scores': [],
                        'pages_hit': set(),
                        'chunk_hits': 0,
                        'sample_pairs': [],
                    }

                doc_stats[doc_id]['scores'].append(score)
                doc_stats[doc_id]['pages_hit'].add(page)
                doc_stats[doc_id]['chunk_hits'] += 1

                # Track sample pairs for LLM analysis (keep top-5 by score)
                pair = {
                    'thesis_text': chunk['text'][:400],
                    'doc_content': str(row.get('content', ''))[:400],
                    'score': score,
                }
                pairs = doc_stats[doc_id]['sample_pairs']
                if len(pairs) < 5:
                    pairs.append(pair)
                elif score > min(p['score'] for p in pairs):
                    pairs.sort(key=lambda p: p['score'])
                    pairs[0] = pair

        # 5. Calculate originality score
        originality_score = round(100 - (flagged_chunks / total_chunks * 100), 2)
        plagiarism_pct = 100 - originality_score
        level = _global_plagiarism_level(plagiarism_pct)

        # 6. Build matches_summary
        doc_list = []
        for doc_id, stats in doc_stats.items():
            scores = stats['scores']
            max_score = round(max(scores), 3)
            avg_score = round(sum(scores) / len(scores), 3)
            similarity_pct = round(stats['chunk_hits'] / total_chunks * 100, 2)
            doc_list.append({
                'document_id': doc_id,
                'title': stats['title'],
                'category_id': stats['category_id'],
                'max_score': max_score,
                'avg_score': avg_score,
                'chunk_hits': stats['chunk_hits'],
                'similarity_pct': similarity_pct,
                'pages_hit': sorted(stats['pages_hit']),
                'risk_level': _plagiarism_level_for_score(max_score),
                'common_themes': [],
                'technologies': [],
                'methods': [],
                'approach': '',
                'problem_overlap': '',
                'llm_analysis': '',
            })

        # Sort by similarity_pct desc, keep top 20
        doc_list.sort(key=lambda x: x['similarity_pct'], reverse=True)
        doc_list = doc_list[:20]

        # 7. LLM comparative analysis for top-N documents above minimum similarity
        max_llm_docs = app.config.get('ORIGINALITY_MAX_LLM_DOCS', 5)
        min_sim_pct = app.config.get('ORIGINALITY_MIN_SIM_FOR_LLM', 5.0)

        for doc_entry in doc_list[:max_llm_docs]:
            if doc_entry['similarity_pct'] >= min_sim_pct:
                pairs = doc_stats[doc_entry['document_id']].get('sample_pairs', [])
                if pairs:
                    try:
                        result = _analyze_with_llm(doc_entry['title'], pairs, app)
                        doc_entry['common_themes']   = result.get('common_themes', [])
                        doc_entry['technologies']    = result.get('technologies', [])
                        doc_entry['methods']         = result.get('methods', [])
                        doc_entry['approach']        = result.get('approach', '')
                        doc_entry['problem_overlap'] = result.get('problem_overlap', '')
                        doc_entry['llm_analysis']    = result.get('analysis', '')
                    except Exception as e:
                        print(f'[LLM analysis error] {e}')
                        doc_entry['common_themes']   = []
                        doc_entry['technologies']    = []
                        doc_entry['methods']         = []
                        doc_entry['approach']        = ''
                        doc_entry['problem_overlap'] = ''
                        doc_entry['llm_analysis']    = ''

        matches_summary = {
            'total_documents_matched': len(doc_stats),
            'documents': doc_list,
        }

        call_fn('fn_update_thesis_check_status', (
            check_id,
            'completed',
            None,
            originality_score,
            level,
            total_chunks,
            flagged_chunks,
            psycopg2.extras.Json(matches_summary),
        ), conn=conn)

        print(f'[Originality] check_id={check_id} score={originality_score} level={level} '
              f'chunks={total_chunks} flagged={flagged_chunks}')

    except Exception as e:
        call_fn('fn_update_thesis_check_status', (
            check_id, 'failed', str(e)
        ), conn=conn)
        print(f'[Originality error] check_id={check_id}: {e}')
        raise
