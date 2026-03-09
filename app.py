from flask import Flask, request, send_file, render_template_string
from rembg import remove, new_session
import io
import os
from PIL import Image

# Configuração de pasta temporária para a IA
os.environ['U2NET_HOME'] = '/tmp/.u2net'

app = Flask(__name__)

# Sua Interface Premium (Neon/Glassmorphism)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RemoverTab Pro | Niltinhoda25</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        body { background-color: #0b0f1a; color: #cbd5e1; font-family: sans-serif; }
        .checkerboard { background-size: 20px 20px; background-image: linear-gradient(45deg, #f0f0f0 25%, transparent 25%), linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f0f0f0 75%), linear-gradient(-45deg, transparent 75%, #f0f0f0 75%); background-color: white; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-2xl mx-auto bg-slate-800/50 p-8 rounded-3xl border border-slate-700 backdrop-blur-md">
        <h1 class="text-3xl font-black text-white mb-6">REMOVER<span class="text-emerald-500">TAB</span> PRO</h1>
        
        <input type="file" id="fileInput" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-500 file:text-white hover:file:bg-emerald-600 mb-6">
        
        <div id="loading" class="hidden text-emerald-400 animate-pulse mb-4">Processando imagem com IA...</div>
        
        <canvas id="mainCanvas" class="w-full rounded-lg hidden border-4 border-slate-900 checkerboard"></canvas>
        
        <button id="downloadBtn" class="hidden mt-6 w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl transition-all">BAIXAR PNG</button>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const canvas = document.getElementById('mainCanvas');
        const ctx = canvas.getContext('2d');

        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            document.getElementById('loading').classList.remove('hidden');
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/remover-fundo', { method: 'POST', body: formData });
            const blob = await response.blob();
            const img = new Image();
            img.src = URL.createObjectURL(blob);
            img.onload = () => {
                canvas.width = img.width; canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                canvas.classList.remove('hidden');
                document.getElementById('downloadBtn').classList.remove('hidden');
                document.getElementById('loading').classList.add('hidden');
            };
        };

        document.getElementById('downloadBtn').onclick = () => {
            const link = document.createElement('a');
            link.download = 'remover-tab-pro.png';
            link.href = canvas.toDataURL();
            link.click();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/remover-fundo', methods=['POST'])
def remover_fundo():
    try:
        file = request.files['image']
        input_image = Image.open(file.stream).convert("RGB")
        # Usando a sessão leve para garantir velocidade e economia de RAM
        output_image = remove(input_image, session=new_session("u2netp"))
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Porta 7860 é obrigatória para o Hugging Face Spaces
    app.run(host='0.0.0.0', port=7860)
