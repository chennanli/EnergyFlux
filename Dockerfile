FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/appuser \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

COPY requirements.txt pyproject.toml runtime.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN adduser --disabled-password --gecos "" appuser

COPY .streamlit/ .streamlit/
COPY stage1_5_wwtp_dc/ stage1_5_wwtp_dc/
COPY knowledge_vault/ knowledge_vault/
COPY wiki/ wiki/
COPY logo.svg README.md index.html ./

RUN chown -R appuser:appuser /app /home/appuser
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).read()" || exit 1

CMD ["streamlit", "run", "stage1_5_wwtp_dc/apps/blog2_genai_app_v2.py", "--server.address=0.0.0.0", "--server.port=8501"]
