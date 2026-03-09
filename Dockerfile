# Usa Python 3.11 estável
FROM python:3.11-slim

# Instala pacotes do sistema (Corrigido para Debian Trixie/Hugging Face)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos do seu repositório
COPY . .

# Instala as dependências de IA
RUN pip install --no-cache-dir -r requirements.txt

# Configura permissões para a IA baixar o modelo
RUN mkdir -p /.u2net && chmod 777 /.u2net
ENV U2NET_HOME=/.u2net

# Porta padrão do Hugging Face
EXPOSE 7860

# Inicia o servidor profissional
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
