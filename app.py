from flask import Flask, request, send_file
from rembg import remove, new_session
import io
import os
from PIL import Image

# Configuração de pasta temporária para a IA baixar o modelo
os.environ['U2NET_HOME'] = '/tmp/.u2net'

app = Flask(__name__)

@app.route('/')
def index():
    # Abre o arquivo index.html que você vai criar no Space
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/remover-fundo', methods=['POST'])
def remover_fundo():
    try:
        if 'image' not in request.files:
            return "Nenhuma imagem enviada", 400
            
        file = request.files['image']
        input_image = Image.open(file.stream).convert("RGB")
        
        # Usa a sessão u2netp (lite) para ser rápido e economizar RAM
        output_image = remove(input_image, session=new_session("u2netp"))
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Porta 7860 é a padrão do Hugging Face Spaces
    app.run(host='0.0.0.0', port=7860)
