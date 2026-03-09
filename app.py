from flask import Flask, request, send_file, render_template_string
from rembg import remove
import io
import os
from PIL import Image

# CONFIGURAÇÃO DE SEGURANÇA PARA IA NA RENDER
# Isso evita o erro de "permissão negada" ao baixar o modelo da IA
os.environ['U2NET_HOME'] = os.path.join(os.getcwd(), '.u2net')
if not os.path.exists('.u2net'):
    os.makedirs('.u2net')

app = Flask(__name__)

# --- SEU HTML PERSONALIZADO (MANTIDO IGUAL) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RemoverTab Pro | Reizinhoda25</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f1a; color: #cbd5e1; overflow-x: hidden; margin: 0; }
        #intro-overlay { position: fixed; inset: 0; background: #0b0f1a; z-index: 9999; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        #logo-intro { font-size: 4rem; font-weight: 900; color: white; position: relative; letter-spacing: -2px; z-index: 10; }
        .stickman { position: absolute; bottom: 40%; left: -100px; width: 60px; height: 80px; stroke: #10b981; stroke-width: 4; fill: none; z-index: 11; }
        @keyframes thief-run { 
            0% { left: -100px; transform: scaleX(1); } 
            45% { left: 50%; transform: translateX(-50%) scaleX(1); } 
            55% { left: 50%; transform: translateX(-50%) scaleX(-1); } 
            100% { left: 120%; transform: scaleX(-1); } 
        }
        @keyframes logo-stolen { 
            0%, 50% { transform: translateX(0); opacity: 1; } 
            100% { transform: translateX(100vw); opacity: 0; } 
        }
        .anim-thief { animation: thief-run 3s cubic-bezier(0.45, 0, 0.55, 1) forwards; }
        .anim-logo { animation: logo-stolen 3s cubic-bezier(0.45, 0, 0.55, 1) forwards; }
        .bg-gradient-glow { background: radial-gradient(circle at 50% -20%, #1e293b, #0b0f1a); }
        .checkerboard { background-image: linear-gradient(45deg, #f8fafc 25%, transparent 25%), linear-gradient(-45deg, #f8fafc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f8fafc 75%), linear-gradient(-45deg, transparent 75%, #f8fafc 75%); background-size: 20px 20px; background-color: #ffffff; }
        .btn-premium { transition: all 0.3s ease; cursor: pointer; border-radius: 1rem; padding: 12px; font-weight: 900; }
        .btn-premium:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3); }
        #cursor-preview { position: fixed; pointer-events: none; border: 2px solid #10b981; border-radius: 50%; transform: translate(-50%, -50%); display: none; z-index: 9998; }
        .loader-ring { width: 40px; height: 40px; border: 3px solid transparent; border-top-color: #10b981; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        canvas { max-width: 100%; max-height: 60vh; border-radius: 1rem; }
    </style>
</head>
<body class="min-h-screen bg-gradient-glow">
    <div id="intro-overlay">
        <div id="logo-intro" class="anim-logo uppercase text-center">Remover<span class="text-emerald-500">Tab</span></div>
        <svg class="stickman anim-thief" viewBox="0 0 100 100"><circle cx="50" cy="20" r="10" /><line x1="50" y1="30" x2="50" y2="60" /><line x1="50" y1="40" x2="30" y2="50" /><line x1="50" y1="40" x2="70" y2="50" /><line x1="50" y1="60" x2="35" y2="90" /><line x1="50" y1="60" x2="65" y2="90" /></svg>
    </div>
    <div id="cursor-preview"></div>
    <nav class="border-b border-slate-800 bg-[#0b0f1a]/80 backdrop-blur-xl h-20 flex items-center sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 w-full flex justify-between items-center">
            <div class="flex items-center gap-2">
                <div class="bg-emerald-500 p-1.5 rounded-lg text-white font-bold text-sm">RT</div>
                <span class="text-xl font-black text-white uppercase tracking-tighter">Remover<span class="text-emerald-500">Tab</span></span>
            </div>
            <div class="text-right"><p class="text-[9px] font-black text-slate-500 uppercase">Editor VIP</p><p class="text-xs font-black text-emerald-400">REIZINHODA25</p></div>
        </div>
    </nav>
    <main class="max-w-4xl mx-auto px-6 pt-12">
        <div id="editorTools" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 hidden animate__animated animate__fadeIn">
            <div class="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50">
                <label class="text-[10px] font-black text-emerald-400 uppercase block mb-2">Borracha</label>
                <input type="range" id="tamanhoBorracha" min="5" max="100" value="25" class="w-full accent-emerald-500">
            </div>
            <div class="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50">
                <label class="text-[10px] font-black text-blue-400 uppercase block mb-2">Ajustes</label>
                <input type="range" id="brilho" min="50" max="150" value="100" class="w-full accent-blue-500 h-1 mb-2">
                <input type="range" id="contraste" min="50" max="150" value="100" class="w-full accent-blue-500 h-1">
            </div>
            <button onclick="baixarImagem()" class="btn-premium bg-emerald-600 text-white uppercase text-xs">Salvar HD</button>
        </div>
        <div id="dropZone" class="bg-slate-800/20 border-2 border-dashed border-slate-700 rounded-[2.5rem] p-16 text-center cursor-pointer relative group hover:border-emerald-500 transition-all">
            <input type="file" id="fileInput" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 z-10 cursor-pointer">
            <div id="uploadPlaceholder">
                <div class="w-16 h-16 bg-emerald-500/20 rounded-2xl mx-auto mb-4 flex items-center justify-center text-emerald-500"><svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg></div>
                <h2 class="text-2xl font-black text-white uppercase">Escolha a Foto</h2>
                <p class="text-slate-500 text-xs font-bold">BY REIZINHODA25</p>
            </div>
            <div id="loading" class="hidden flex flex-col items-center"><div class="loader-ring mb-4"></div><p class="text-emerald-400 font-black animate-pulse text-xs uppercase">Processando IA...</p></div>
        </div>
        <div id="canvasArea" class="hidden animate__animated animate__zoomIn mt-8">
            <div class="checkerboard rounded-3xl p-1 border-8 border-slate-900 flex justify-center overflow-hidden"><canvas id="mainCanvas"></canvas></div>
        </div>
    </main>
    <script>
        window.addEventListener('load', () => {
            setTimeout(() => {
                const overlay = document.getElementById('intro-overlay');
                overlay.style.transition = 'opacity 0.5s';
                overlay.style.opacity = '0';
                setTimeout(() => overlay.style.display = 'none', 500);
            }, 2800);
        });
        const canvas = document.getElementById('mainCanvas'), ctx = canvas.getContext('2d'), cursor = document.getElementById('cursor-preview');
        let img = new Image(), isDrawing = false, brushSize = 25;
        document.getElementById('tamanhoBorracha').oninput = (e) => brushSize = e.target.value;
        document.getElementById('fileInput').onchange = async (e) => {
            const file = e.target.files[0]; if (!file) return;
            document.getElementById('uploadPlaceholder').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');
            const formData = new FormData(); formData.append('image', file);
            const response = await fetch('/remover-fundo', { method: 'POST', body: formData });
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
        };
        canvas.onmousedown = (e) => { isDrawing = true; paint(e); };
        window.onmouseup = () => isDrawing = false;
        canvas.onmousemove = (e) => {
            cursor.style.display = 'block'; cursor.style.left = e.clientX + 'px'; cursor.style.top = e.clientY + 'px';
            cursor.style.width = brushSize + 'px'; cursor.style.height = brushSize + 'px';
            if (isDrawing) paint(e);
        };
        function paint(e) {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (canvas.height / rect.height);
            ctx.globalCompositeOperation = 'destination-out'; ctx.beginPath();
            ctx.arc(x, y, (brushSize * (canvas.width / rect.width)) / 2, 0, Math.PI * 2); ctx.fill();
        }
        function baixarImagem() {
            const link = document.createElement('a');
            link.download = 'Reizinhoda25_Edit.png';
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
        input_image = Image.open(file.stream)
        # O rembg remove o fundo aqui
        output_image = remove(input_image)
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # PORTA DINÂMICA PARA A RENDER (CORRIGIDO)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
