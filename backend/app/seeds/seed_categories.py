from app.db import call_fn


CATEGORIES = [
    {
        'name': 'Reglamentos',
        'slug': 'reglamentos',
        'description': 'Reglamentos academicos, disciplinarios y administrativos',
        'icon': 'gavel',
        'color': '#1E3A5F',
    },
    {
        'name': 'Tramites',
        'slug': 'tramites',
        'description': 'Procedimientos administrativos y tramites universitarios',
        'icon': 'description',
        'color': '#2E7D32',
    },
    {
        'name': 'Becas y Beneficios',
        'slug': 'becas-y-beneficios',
        'description': 'Informacion sobre becas, descuentos y beneficios estudiantiles',
        'icon': 'school',
        'color': '#F57F17',
    },
    {
        'name': 'Calendario Academico',
        'slug': 'calendario-academico',
        'description': 'Fechas importantes, periodos academicos y cronogramas',
        'icon': 'calendar_today',
        'color': '#C62828',
    },
    {
        'name': 'Silabos',
        'slug': 'silabos',
        'description': 'Planes de estudio, silabos y mallas curriculares',
        'icon': 'menu_book',
        'color': '#6A1B9A',
    },
    {
        'name': 'Investigacion',
        'slug': 'investigacion',
        'description': 'Tesis, publicaciones, lineas de investigacion',
        'icon': 'science',
        'color': '#00838F',
    },
    {
        'name': 'Admision',
        'slug': 'admision',
        'description': 'Requisitos de admision, procesos y modalidades de ingreso',
        'icon': 'how_to_reg',
        'color': '#E65100',
    },
    {
        'name': 'Bienestar Universitario',
        'slug': 'bienestar-universitario',
        'description': 'Servicios de salud, psicologia, deportes y bienestar',
        'icon': 'favorite',
        'color': '#AD1457',
    },
]


def seed_categories():
    for cat in CATEGORIES:
        created = call_fn('fn_seed_category', (
            cat['name'], cat['slug'], cat['description'], cat['icon'], cat['color']
        ), fetch_one=True)

        if created and created['fn_seed_category']:
            print(f"Categoria creada: {cat['name']}")
        else:
            print(f"Categoria ya existe: {cat['name']}")
