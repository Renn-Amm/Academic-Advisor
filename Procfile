web: uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
release: alembic -c backend/alembic.ini upgrade head
