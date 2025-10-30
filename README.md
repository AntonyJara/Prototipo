# Asistente Pedagógico - Generador de Competencias

Aplicación web para generar automáticamente competencias, criterios de evaluación y estándares de aprendizaje usando IA.

## Características

- Generación automática de competencias según ciclo y área
- Criterios de evaluación contextualizados
- Descarga directa en formato Word
- Interfaz intuitiva para docentes

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
pip install -r requirements.txt
```

## Uso Local

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Despliegue en Render

1. Sube este repositorio a GitHub
2. Ve a https://render.com
3. Crea un nuevo servicio web
4. Conecta tu repositorio de GitHub
5. Configura:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Agregar variable de entorno: `OPENAI_API_KEY` con tu clave de OpenAI

## Variables de Entorno

Necesitas configurar:
- `OPENAI_API_KEY`: Tu clave de API de OpenAI

## Licencia

Proyecto educativo - Uso libre
