from flask import Flask, request, send_file
from rembg import remove, new_session
import io
import os
from PIL import Image, ImageEnhance

os.environ['U2NET_HOME'] = '/tmp/.u2net'
app = Flask(__name__)

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/remover-fundo', methods=['POST'])
def remover_fundo():
    try:
        file = request.files['image']
        color = request.form.get('color', 'transparent')
        
        input_image = Image.open(file.stream).convert("RGBA")
        output_image = remove(input_image, session=new_session("u2netp"))
        
        if color != 'transparent':
            # Cria um fundo da cor selecionada
            background = Image.new("RGBA", output_image.size, color)
            background.paste(output_image, (0, 0), output_image)
            output_image = background

        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
