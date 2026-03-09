# Usa uma imagem oficial do Python estável
FROM python:3.11-slim

# Instala dependências do sistema para o OpenCV e IA
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Cria o diretório de trabalho
WORKDIR /app

# Copia os arquivos do seu projeto
COPY . .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria a pasta da IA com permissão total
RUN mkdir -p /.u2net && chmod 777 /.u2net
ENV U2NET_HOME=/.u2net

# Porta que o Hugging Face usa por padrão
EXPOSE 7860

# Comando para ligar o servidor gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
