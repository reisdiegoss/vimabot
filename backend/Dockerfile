# =============================================================================
# VimaBOT SaaS - Dockerfile do Backend
# =============================================================================
# Imagem otimizada para o servidor FastAPI assíncrono.
# Usa Python 3.11 slim para reduzir o tamanho da imagem final.
#
# Build: docker build -t vimabot-backend ./backend
# Run:   docker run -p 8000:8000 --env-file .env vimabot-backend
# =============================================================================

# --- Estágio Base ---
FROM python:3.11-slim AS base

# Evita prompts interativos durante instalação de pacotes
ENV DEBIAN_FRONTEND=noninteractive \
    # Impede que o Python gere arquivos .pyc (desnecessários no container)
    PYTHONDONTWRITEBYTECODE=1 \
    # Desabilita o buffer de saída para logs aparecerem em tempo real
    PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# --- Estágio de Dependências ---
# Copia apenas o requirements.txt primeiro para aproveitar cache do Docker
# Se as dependências não mudaram, esta camada é reutilizada
COPY requirements.txt .

# Instala as dependências Python sem cache para reduzir tamanho
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Estágio da Aplicação ---
# Copia o código-fonte da aplicação
COPY ./app ./app

# Expõe a porta padrão do uvicorn
EXPOSE 8000

# Comando padrão para iniciar o servidor em produção
# Em desenvolvimento, o docker-compose.yml sobrescreve com --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
