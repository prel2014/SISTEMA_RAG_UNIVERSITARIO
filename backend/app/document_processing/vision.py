import base64
import io

from PIL import Image


_VISION_PROMPT = (
    'Describe detalladamente el contenido de esta imagen en español. '
    'Si es una gráfica o diagrama, explica los datos, ejes y tendencias. '
    'Si es una tabla, transcribe sus valores. '
    'Si es un diagrama de flujo o arquitectura, describe la estructura y relaciones. '
    'Sé conciso pero completo.'
)


def describe_image(image_bytes: bytes, ollama_url: str, llm_model: str) -> str:
    """Describe an image using a multimodal LLM via Ollama.

    Normalizes the image (RGB, max 1024px), encodes as JPEG base64,
    and invokes ChatOllama with a multimodal HumanMessage.

    Returns the description string, or '' on any failure (silent).
    """
    try:
        from langchain_ollama import ChatOllama
        from langchain_core.messages import HumanMessage

        # Normalize: convert to RGB, resize to max 1024px on longest side
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        max_dim = 1024
        w, h = img.size
        if w > max_dim or h > max_dim:
            scale = max_dim / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        llm = ChatOllama(
            model=llm_model,
            base_url=ollama_url,
            temperature=0.0,
            num_ctx=1024,
        )
        message = HumanMessage(content=[
            {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
            {'type': 'text', 'text': _VISION_PROMPT},
        ])
        response = llm.invoke([message])
        return response.content.strip()

    except Exception as e:
        print(f'[Vision] Error al describir imagen: {e}')
        return ''
