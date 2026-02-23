"""
Generador de infografía PDF – UPAO RAG
"""
import math
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black

# ── Paleta de colores ────────────────────────────────────────────────────────
UPAO_BLUE   = HexColor('#1E3A5F')
UPAO_RED    = HexColor('#C8102E')
MID_BLUE    = HexColor("#004359")
ACCENT      = HexColor('#3B82F6')
LIGHT_BLUE  = HexColor("#1272D1")
DARK_GRAY   = HexColor('#1F2937')
MED_GRAY    = HexColor('#6B7280')
GREEN       = HexColor('#059669')
LT_GREEN    = HexColor('#ECFDF5')
ORANGE      = HexColor('#D97706')
LT_ORANGE   = HexColor("#00CAFD")
PURPLE      = HexColor('#7C3AED')
LT_PURPLE   = HexColor("#FFFBF3")
TEAL        = HexColor('#0D9488')
LT_TEAL     = HexColor("#2779C6")
BORDER_BLUE = HexColor('#BFDBFE')
BORDER_GRN  = HexColor('#A7F3D0')
BORDER_PRP  = HexColor('#C4B5FD')


# ── Utilidades ───────────────────────────────────────────────────────────────
def rr(c, x, y, w, h, r, fill, stroke=None, sw=1.0):
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
        c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def arw(c, x1, y1, x2, y2, color, lw=1.5):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    a = math.atan2(y2 - y1, x2 - x1)
    al = 7
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - al * math.cos(a - 0.4), y2 - al * math.sin(a - 0.4))
    p.lineTo(x2 - al * math.cos(a + 0.4), y2 - al * math.sin(a + 0.4))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def sec_title(c, x, y, text, line_x2):
    c.setFillColor(UPAO_BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, text)
    c.setStrokeColor(UPAO_RED)
    c.setLineWidth(2)
    c.line(x, y - 5, line_x2, y - 5)


def centered_text(c, cx, y, text, font="Helvetica", size=8, color=white):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(cx, y, text)


def left_text(c, x, y, text, font="Helvetica", size=8, color=DARK_GRAY):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


# ── Generador principal ──────────────────────────────────────────────────────
def build():
    W, H = A4   # 595.27 × 841.89
    out = "C:/Users/prodriguezl1/Downloads/UPAO_RAG/upao_rag_infografia.pdf"
    cv = canvas.Canvas(out, pagesize=A4)

    # ══════════════════════════════════════════════════════════════════════════
    # HEADER  (842 → 737)
    # ══════════════════════════════════════════════════════════════════════════
    hh = 105
    cv.setFillColor(UPAO_BLUE)
    cv.rect(0, H - hh, W, hh, fill=1, stroke=0)

    # Círculos decorativos
    for (cx2, cy2, r2, alpha) in [(50, H-30, 58, '12'), (W-28, H-76, 64, '0E'), (170, H-95, 42, '09')]:
        cv.setFillColor(HexColor("#061594"))
        cv.circle(cx2, cy2, r2, fill=1, stroke=0)

    # Título
    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 30)
    cv.drawString(28, H - 46, "UPAO RAG")

    cv.setFont("Helvetica", 12)
    cv.drawString(28, H - 64, "Asistente Virtual Universitario con Inteligencia Artificial")

    # Badge rojo
    cv.setFillColor(UPAO_RED)
    cv.roundRect(28, H - 92, 198, 21, 4, fill=1, stroke=0)
    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(127, H - 86, "Retrieval-Augmented Generation (RAG)")

    # Texto derecha
    cv.setFillColor(HexColor('#FFFFFFCC'))
    cv.setFont("Helvetica-Bold", 10)
    cv.drawRightString(W - 20, H - 42, "Universidad Privada Antenor Orrego")
    cv.setFont("Helvetica", 9)
    cv.setFillColor(HexColor('#FFFFFF99'))
    cv.drawRightString(W - 20, H - 57, "Sistema de Gestion del Conocimiento")
    cv.drawRightString(W - 20, H - 70, "Institucional")

    # ══════════════════════════════════════════════════════════════════════════
    # BANDA DESCRIPCION  (737 → 687)
    # ══════════════════════════════════════════════════════════════════════════
    db_y = H - hh - 50
    cv.setFillColor(LIGHT_BLUE)
    cv.rect(0, db_y, W, 50, fill=1, stroke=0)
    cv.setFillColor(UPAO_RED)
    cv.rect(0, db_y, 4, 50, fill=1, stroke=0)   # acento lateral

    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 10)
    cv.drawString(18, db_y + 34, "Que es UPAO RAG?")
    cv.setFillColor(white)
    cv.setFont("Helvetica", 9)
    cv.drawString(18, db_y + 20, "Chatbot institucional basado en RAG que permite consultar documentos de UPAO en lenguaje natural,")
    cv.drawString(18, db_y + 8,  "con gestion de documentos, historial de conversaciones y verificacion de originalidad de tesis.")

    # ══════════════════════════════════════════════════════════════════════════
    # ARQUITECTURA DEL SISTEMA  (title=675, boxes bottom=577, h=85)
    # ══════════════════════════════════════════════════════════════════════════
    ARCH_TY = 675
    ARCH_BY = 577
    ARCH_H  = 85

    sec_title(cv, 18, ARCH_TY, "Arquitectura del Sistema", 200)

    arch_data = [
        ("Usuario",         "Estudiante\no docente",       HexColor("#000000")),
        ("Angular 18",      "Interfaz SPA\n:4200",          MID_BLUE),
        ("Flask API",       "REST API\n:5050",              ACCENT),
        ("RAG Pipeline",    "LangChain\n+ Ollama",         GREEN),
        ("PostgreSQL\n+ Qdrant", "Datos y\nvectores",      PURPLE),
    ]
    bw, n = 88, len(arch_data)
    bsp = (W - 36 - n * bw) / (n - 1)
    bx0 = 18

    for i, (title, desc, color) in enumerate(arch_data):
        bx = bx0 + i * (bw + bsp)
        rr(cv, bx, ARCH_BY, bw, ARCH_H, 6, color)

        # Highlight superior
        cv.setFillColor(HexColor('#FFFFFF22'))
        cv.roundRect(bx, ARCH_BY + ARCH_H - 22, bw, 22, 6, fill=1, stroke=0)
        cv.rect(bx, ARCH_BY + ARCH_H - 11, bw, 11, fill=1, stroke=0)

        cv.setFillColor(white)
        cv.setFont("Helvetica-Bold", 8.5)
        for j, ln in enumerate(title.split('\n')):
            cv.drawCentredString(bx + bw/2, ARCH_BY + ARCH_H - 14 - j * 10, ln)

        cv.setFont("Helvetica", 7.5)
        for j, ln in enumerate(desc.split('\n')):
            cv.drawCentredString(bx + bw/2, ARCH_BY + 22 - j * 11, ln)

        if i < n - 1:
            arw(cv, bx + bw + 2, ARCH_BY + ARCH_H / 2,
                bx + bw + bsp - 2, ARCH_BY + ARCH_H / 2, MED_GRAY)

    # ══════════════════════════════════════════════════════════════════════════
    # CARACTERÍSTICAS PRINCIPALES  (title=567, boxes bottom=425, h=130)
    # ══════════════════════════════════════════════════════════════════════════
    FEAT_TY = 567
    FEAT_BY = 425
    FEAT_H  = 130

    sec_title(cv, 18, FEAT_TY, "Caracteristicas Principales", 238)

    feat_data = [
        {
            "title":  "Chat Inteligente",
            "color":  HexColor("#000000"),
            "light":  HexColor('#EFF6FF'),
            "border": BORDER_BLUE,
            "items":  [
                "Consultas en lenguaje natural",
                "Respuestas con fuentes citadas",
                "Streaming de tokens en tiempo real",
                "Historial de conversaciones",
                "Filtro por categoria de documento",
            ],
        },
        {
            "title":  "Gestion de Documentos",
            "color":  GREEN,
            "light":  LT_GREEN,
            "border": BORDER_GRN,
            "items":  [
                "Carga individual y masiva (batch)",
                "PDF, DOCX, XLSX, TXT, Imagenes",
                "Procesamiento en segundo plano",
                "Auto-categorizacion con IA (LLM)",
                "OCR para imagenes escaneadas",
            ],
        },
        {
            "title":  "Verificacion de Originalidad",
            "color":  PURPLE,
            "light":  LT_PURPLE,
            "border": BORDER_PRP,
            "items":  [
                "Deteccion de similitudes via RAG",
                "Score de originalidad 0-100%",
                "Niveles: bajo / moderado / alto",
                "Analisis LLM de fragmentos comunes",
                "Reporte detallado por documento",
            ],
        },
    ]

    fw = (W - 36 - 2 * 10) / 3
    for i, feat in enumerate(feat_data):
        fx = 18 + i * (fw + 10)

        rr(cv, fx, FEAT_BY, fw, FEAT_H, 8, feat["light"], feat["border"], 1.0)

        # Barra superior
        rr(cv, fx, FEAT_BY + FEAT_H - 26, fw, 26, 8, feat["color"])
        cv.setFillColor(feat["color"])
        cv.rect(fx, FEAT_BY + FEAT_H - 13, fw, 13, fill=1, stroke=0)

        cv.setFillColor(white)
        cv.setFont("Helvetica-Bold", 9.5)
        cv.drawCentredString(fx + fw / 2, FEAT_BY + FEAT_H - 17, feat["title"])

        for j, pt in enumerate(feat["items"]):
            y_pt = FEAT_BY + FEAT_H - 40 - j * 16
            cv.setFillColor(feat["color"])
            cv.circle(fx + 10, y_pt + 3, 2.5, fill=1, stroke=0)
            cv.setFillColor(DARK_GRAY)
            cv.setFont("Helvetica", 8)
            cv.drawString(fx + 17, y_pt, pt)

    # ══════════════════════════════════════════════════════════════════════════
    # STACK TECNOLOGICO  (title=415, r0 bottom=365 h=38, r1 bottom=319 h=38)
    # ══════════════════════════════════════════════════════════════════════════
    TECH_TY = 415
    T_R0    = 365
    T_H     = 38
    T_GAP   = 8

    sec_title(cv, 18, TECH_TY, "Stack Tecnologico", 168)

    tech_rows = [
        [
            ("Python 3.11",       "Backend",      HexColor('#3776AB'), HexColor('#E8F4FF')),
            ("Flask",             "REST API",     HexColor('#222222'), HexColor('#F4F4F4')),
            ("Angular 18",        "Frontend",     HexColor('#DD0031'), HexColor('#FFF0F0')),
            ("PostgreSQL",        "Base de datos",HexColor('#336791'), HexColor('#EBF3FF')),
            ("Qdrant",            "Vector DB",    HexColor('#DC244C'), HexColor('#FFF0F3')),
        ],
        [
            ("Ollama",            "LLM local",    HexColor('#222222'), HexColor('#F4F4F4')),
            ("gemma3:4b",         "Modelo IA",    HexColor('#4285F4'), HexColor('#EFF6FF')),
            ("nomic-embed-text",  "Embeddings",   HexColor('#FF6B35'), HexColor('#FFF4F0')),
            ("LangChain",         "RAG Framework",HexColor('#1C7C54'), HexColor('#EDFDF5')),
            ("Tailwind CSS",      "UI Styles",    HexColor('#06B6D4'), HexColor('#F0FEFF')),
        ],
    ]

    tw = (W - 36 - 4 * 8) / 5
    for ri, row in enumerate(tech_rows):
        ty = T_R0 - ri * (T_H + T_GAP)
        for ci, (name, role, col, bg) in enumerate(row):
            tx = 18 + ci * (tw + 8)
            rr(cv, tx, ty, tw, T_H, 5, bg, col, 0.8)
            cv.setFillColor(col)
            cv.circle(tx + 11, ty + T_H / 2, 4.5, fill=1, stroke=0)
            cv.setFillColor(DARK_GRAY)
            cv.setFont("Helvetica-Bold", 8)
            cv.drawString(tx + 20, ty + T_H / 2 + 2, name)
            cv.setFillColor(MED_GRAY)
            cv.setFont("Helvetica", 7)
            cv.drawString(tx + 20, ty + T_H / 2 - 9, role)

    # ══════════════════════════════════════════════════════════════════════════
    # FLUJO RAG  (title=309, boxes bottom=222, h=75)
    # ══════════════════════════════════════════════════════════════════════════
    RAG_TY = 309
    RAG_BY = 222
    RAG_H  = 75

    sec_title(cv, 18, RAG_TY, "Flujo del Pipeline RAG", 215)

    rag_steps = [
        ("Pregunta",  "Usuario\nconsulta",        UPAO_BLUE),
        ("Embedding", "nomic-embed\n768 dims",     ACCENT),
        ("Busqueda",  "Qdrant\ncosine sim",        PURPLE),
        ("Contexto",  "Top-K\nfragmentos",         TEAL),
        ("LLM",       "gemma3:4b\nresponde",       GREEN),
        ("Respuesta", "SSE tokens\nal cliente",    UPAO_RED),
    ]

    rw = (W - 36 - 5 * 10) / 6
    rsp = 10
    rx0 = 18

    for i, (title, desc, color) in enumerate(rag_steps):
        rx = rx0 + i * (rw + rsp)
        rr(cv, rx, RAG_BY, rw, RAG_H, 5, color)

        # Badge número
        cv.setFillColor(HexColor('#FFFFFF30'))
        cv.circle(rx + 12, RAG_BY + RAG_H - 11, 9, fill=1, stroke=0)
        cv.setFillColor(white)
        cv.setFont("Helvetica-Bold", 9)
        cv.drawCentredString(rx + 12, RAG_BY + RAG_H - 14, str(i + 1))

        cv.setFont("Helvetica-Bold", 8)
        cv.drawCentredString(rx + rw / 2, RAG_BY + RAG_H - 27, title)

        cv.setFont("Helvetica", 7.5)
        for j, ln in enumerate(desc.split('\n')):
            cv.drawCentredString(rx + rw / 2, RAG_BY + 22 - j * 11, ln)

        if i < len(rag_steps) - 1:
            arw(cv, rx + rw + 2, RAG_BY + RAG_H / 2,
                rx + rw + rsp - 2, RAG_BY + RAG_H / 2, MED_GRAY)

    # ══════════════════════════════════════════════════════════════════════════
    # PARÁMETROS CLAVE  (title=212, boxes bottom=130, h=70)
    # ══════════════════════════════════════════════════════════════════════════
    MET_TY = 212
    MET_BY = 130
    MET_H  = 70

    sec_title(cv, 18, MET_TY, "Parametros Clave del Sistema", 230)

    metrics = [
        ("768 dims",    "Dimensiones\nde Embedding",  HexColor('#EFF6FF'), ACCENT),
        ("1 000 chars", "Tamano\nde Chunk",            LT_ORANGE,           ORANGE),
        ("0.35",        "Umbral\nde Busqueda",         LT_GREEN,            GREEN),
        ("0.70",        "Umbral\nde Plagio",           HexColor('#FFF0F3'), UPAO_RED),
        ("gemma3:4b",   "Modelo LLM\nlocal",           LT_PURPLE,           PURPLE),
    ]

    mw = (W - 36 - 4 * 10) / 5
    for i, (val, label, bg, color) in enumerate(metrics):
        mx = 18 + i * (mw + 10)
        rr(cv, mx, MET_BY, mw, MET_H, 6, bg, color, 1.5)
        cv.setFillColor(color)
        cv.setFont("Helvetica-Bold", 12)
        cv.drawCentredString(mx + mw / 2, MET_BY + MET_H - 24, val)
        cv.setFillColor(MED_GRAY)
        cv.setFont("Helvetica", 7.5)
        for j, ln in enumerate(label.split('\n')):
            cv.drawCentredString(mx + mw / 2, MET_BY + MET_H - 38 - j * 11, ln)

    # ══════════════════════════════════════════════════════════════════════════
    # ROLES Y ACCESO  (title=120, boxes bottom=55, h=55)
    # ══════════════════════════════════════════════════════════════════════════
    ROL_TY = 120
    ROL_BY = 55
    ROL_H  = 55

    sec_title(cv, 18, ROL_TY, "Roles y Acceso", 155)

    roles = [
        ("ESTUDIANTE",     "Inicia sesion con\ncorreo @upao.edu.pe",
         "Chat con documentos\ny historial",         ACCENT,  HexColor('#EFF6FF'), BORDER_BLUE),
        ("DOCENTE",        "Inicia sesion con\ncorreo @upao.edu.pe",
         "Chat + consulta\nde materiales",           TEAL,    LT_TEAL,             HexColor('#99F6E4')),
        ("ADMINISTRADOR",  "Creado via\nflask seed run",
         "Gestion completa:\nusuarios, docs, RAG",   GREEN,   LT_GREEN,            BORDER_GRN),
        ("SISTEMA (RAG)",  "Pipeline automatico\nen background",
         "Embedding, busqueda\nvectorial y LLM",     PURPLE,  LT_PURPLE,           BORDER_PRP),
    ]

    rw2 = (W - 36 - 3 * 10) / 4
    for i, (title, sub1, sub2, color, light, border) in enumerate(roles):
        rx2 = 18 + i * (rw2 + 10)
        rr(cv, rx2, ROL_BY, rw2, ROL_H, 6, light, border, 1.0)

        # Barra izquierda
        cv.setFillColor(color)
        cv.roundRect(rx2, ROL_BY, 4, ROL_H, 2, fill=1, stroke=0)

        cv.setFillColor(color)
        cv.setFont("Helvetica-Bold", 8)
        cv.drawString(rx2 + 10, ROL_BY + ROL_H - 14, title)

        cv.setFillColor(MED_GRAY)
        cv.setFont("Helvetica", 7)
        for j, ln in enumerate(sub1.split('\n')):
            cv.drawString(rx2 + 10, ROL_BY + ROL_H - 25 - j * 9, ln)

        cv.setFillColor(DARK_GRAY)
        cv.setFont("Helvetica", 7.5)
        for j, ln in enumerate(sub2.split('\n')):
            cv.drawString(rx2 + 10, ROL_BY + 20 - j * 10, ln)

    # ══════════════════════════════════════════════════════════════════════════
    # FOOTER  (0 → 35)
    # ══════════════════════════════════════════════════════════════════════════
    cv.setFillColor(UPAO_BLUE)
    cv.rect(0, 0, W, 35, fill=1, stroke=0)
    cv.setFillColor(UPAO_RED)
    cv.rect(0, 35, W, 3, fill=1, stroke=0)

    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(W / 2, 21, "Universidad Privada Antenor Orrego  •  UPAO RAG  •  Sistema de Gestion del Conocimiento Institucional")
    cv.setFillColor(HexColor('#FFFFFFAA'))
    cv.setFont("Helvetica", 7.5)
    cv.drawCentredString(W / 2, 9, "Flask • Angular 18 • PostgreSQL • Qdrant • Ollama • LangChain • Tailwind CSS")

    cv.save()
    return out


if __name__ == "__main__":
    path = build()
    print(f"Infografia generada: {path}")
