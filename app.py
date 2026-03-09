from flask import Flask, request, send_file, render_template_string
from rembg import remove, new_session
import io
import os
from PIL import Image

# --- CONFIGURAÇÕES DE AMBIENTE ---
# Pasta temporária com permissão de escrita na Render
os.environ['U2NET_HOME'] = '/tmp/.u2net'

app = Flask(__name__)

# --- INTERFACE PREMIUM (MANTIDA) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RemoverTab Pro | Niltinhoda25</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f1a; color: #cbd5e1; overflow-x: hidden; margin: 0; }
        #intro-overlay { position: fixed; inset: 0; background: #0b0f1a; z-index: 9999; display: flex; align-items: center; justify-content: center; }
        #logo-intro { font-size: 4rem; font-weight: 900; color: white; letter-spacing: -2px; }
        .anim-logo { animation: fadeOut 1s ease forwards; animation-delay: 2.5s; }
        @keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
        .checkerboard { background-image: linear-gradient(45deg, #f8fafc 25%, transparent 25%), linear-gradient(-45deg, #f8fafc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f8fafc 75%), linear-gradient(-45deg, transparent 75%, #f8fafc 75%); background-size: 20px 20px; background-color: #ffffff; }
        .btn-premium { transition: all 0.3s ease; cursor: pointer; border-radius: 1rem; padding: 12px; font-weight: 900; }
        .btn-premium:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3); }
        .loader-ring { width: 40px; height: 40px; border: 3px solid transparent; border-top-color: #10b981; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        canvas { max-width: 100%; max-height: 60vh; border-radius: 1rem; }
    </style>
</head>
<body class="min-h-screen bg-[#0b0f1a]">
    <div id="intro-overlay" class="anim-logo">
        <div id="logo-intro">Remover<span class="text-emerald-500">Tab</span></div>
    </div>

    <nav class="border-b border-slate-800 bg-[#0b0f1a]/80 backdrop-blur-xl h-20 flex items-center sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 w-full flex justify-between items-center">
            <div class="flex items-center gap-2">
                <div class="bg-emerald-500 p-1.5 rounded-lg text-white font-bold text-sm">RT</div>
                <span class="text-xl font-black text-white uppercase tracking-tighter">Remover<span class="text-emerald-500">Tab</span></span>
            </div>
            <div class="text-right"><p class="text-[9px] font-black text-slate-500 uppercase">Editor VIP</p><p class="text-xs font-black text-emerald-400">PRO</p></div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 pt-12">
        <div id="editorTools" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 hidden animate__animated animate__fadeIn">
            <div class="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50">
                <label class="text-[10px] font-black text-emerald-400 uppercase block mb-2">Borracha (Tamanho)</label>
                <input type="range" id="tamanhoBorracha" min="5" max="100" value="25" class="w-full accent-emerald-500">
            </div>
            <button onclick="baixarImagem()" class="btn-premium bg-emerald-600 text-white uppercase text-xs">Salvar PNG</button>
        </div>

        <div id="dropZone" class="bg-slate-800/20 border-2 border-dashed border-slate-700 rounded-[2.5rem] p-16 text-center cursor-pointer relative group hover:border-emerald-500 transition-all">
            <input type="file" id="fileInput" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 z-10 cursor-pointer">
            <div id="uploadPlaceholder">
                <h2 class="text-2xl font-black text-white uppercase">Escolha a Foto</h2>
                <p class="text-slate-500 text-xs font-bold uppercase tracking-widest">Remoção Profissional</p>
            </div>
            <div id="loading" class="hidden flex flex-col items-center"><div class="loader-ring mb-4"></div><p class="text-emerald-400 font-black animate-pulse text-xs uppercase">Processando IA...</p></div>
        </div>

        <div id="canvasArea" class="hidden animate__animated animate__zoomIn mt-8">
            <div class="checkerboard rounded-3xl p-1 border-8 border-slate-900 flex justify-center overflow-hidden"><canvas id="mainCanvas"></canvas></div>
        </div>
    </main>

    <script>
        const canvas = document.getElementById('mainCanvas'), ctx = canvas.getContext('2d');
        let img = new Image(), isDrawing = false, brushSize = 25;

        document.getElementById('tamanhoBorracha').oninput = (e) => brushSize = e.target.value;

        document.getElementById('fileInput').onchange = async (e) => {
            const file = e.target.files[0]; if (!file) return;
            document.getElementById('uploadPlaceholder').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');
            
            const formData = new FormData(); formData.append('image', file);
            try {
                const response = await fetch('/remover-fundo', { method: 'POST', body: formData });
                if (!response.ok) throw new Error("Erro na memória");
                const blob = await response.blob();
                img.src = URL.createObjectURL(blob);
                img.onload = () => {
                    canvas.width = img.width; canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    document.getElementById('dropZone').classList.add('hidden');
                    document.getElementById('editorTools').classList.remove('hidden');
                    document.getElementById('canvasArea').classList.remove('hidden');
                    document.getElementById('loading').classList.add('hidden');
                };
            } catch (err) {
                alert("Servidor sobrecarregado. Tente uma imagem menor.");
                location.reload();
            }
        };

        canvas.onmousedown = (e) => { isDrawing = true; paint(e); };
        window.onmouseup = () => isDrawing = false;
        canvas.onmousemove = (e) => { if (isDrawing) paint(e); };

        function paint(e) {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (canvas.height / rect.height);
            ctx.globalCompositeOperation = 'destination-out'; ctx.beginPath();
            ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2); ctx.fill();
        }

        function baixarImagem() {
            const link = document.createElement('a');
            link.download = 'remover-tab-pro.png';
            link.href = canvas.toDataURL();
            link.click();
        }
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
        # Reduzimos um pouco a qualidade na entrada para economizar RAM
        input_image = Image.open(file.stream).convert("RGB")
        
        # Carregamos a sessão leve u2netp apenas durante a execução
        # Isso evita que o servidor fique com 500MB ocupados parado
        output_image = remove(input_image, session=new_session("u2netp"))
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro de Memória na Render", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
