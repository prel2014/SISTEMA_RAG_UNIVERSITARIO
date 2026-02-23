import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core")

from dotenv import load_dotenv
from pathlib import Path

# Cargar .env de la raíz del proyecto (un nivel arriba de backend/)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
