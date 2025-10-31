from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import downloader_logic
import datetime

app = Flask(__name__)
CORS(app) 

download_history = []

@app.route('/api/validate-playlist', methods=['POST'])
def handle_validate():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL não fornecida."}), 400

    playlist_url = data['url']
    print(f"[API] Validando URL: {playlist_url}")

    playlist_info, error = downloader_logic.get_valid_playlist_info(playlist_url)

    if error:
        return jsonify({"error": error}), 400

    video_list = []
    for entry in playlist_info.get('entries', []):
        if entry and entry.get('id'):
            video_list.append({
                "id": entry.get('id'),
                "title": entry.get('title', 'Título desconhecido')
            })

    return jsonify({
        "playlist_title": playlist_info.get('title', 'Playlist Desconhecida'),
        "videos": video_list
    }), 200

@app.route('/api/download-selected', methods=['POST'])
def handle_download():
    data = request.get_json()
    if not data or 'format' not in data or 'videos' not in data:
        return jsonify({"error": "Dados inválidos. Envie 'format' e 'videos'."}), 400

    format_key = data['format']
    videos_to_download = data['videos'] 

    print(f"[API] Recebida requisição para baixar {len(videos_to_download)} vídeos em {format_key}")

    download_folder = "audio_downloads" if format_key == 'mp3' else "video_downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    base_options = downloader_logic.get_format_options(format_key, download_folder)
    playlist_info = { "entries": videos_to_download }

    successes, failures = downloader_logic.start_download_loop(playlist_info, base_options)

    # --- NOVO: Adiciona downloads bem-sucedidos ao histórico ---
    current_time = datetime.datetime.now().isoformat()
    for success_info in successes: # successes já contém o title e filename
        download_history.append({
            "title": success_info,
            "format": format_key,
            "timestamp": current_time,
            "filename": None, # Nome do arquivo para download direto
            "folder": download_folder # Pasta onde está o arquivo
        })
    print(f"Histórico de downloads atualizado: {len(download_history)} itens.")
    # --- FIM NOVO ---

    print(f"[API] Enviando resposta para o frontend.")
    return jsonify({
        "message": "Download concluído.",
        "total_success": len(successes),
        "total_failures": len(failures),
        "failures_list": failures
    }), 200


# --- NOVA ROTA: Retorna o histórico de downloads ---
@app.route('/api/get-downloads', methods=['GET'])
def get_downloads_history():
    # Retorna o histórico, ordenado do mais recente para o mais antigo
    sorted_history = sorted(download_history, key=lambda x: x['timestamp'], reverse=True)
    return jsonify({"downloads": sorted_history}), 200

# --- NOVA ROTA: Para servir os arquivos baixados (opcional, mas útil) ---
@app.route('/downloads/<folder>/<filename>', methods=['GET'])
def serve_downloaded_file(folder, filename):
    # Garante que apenas as pastas "audio_downloads" ou "video_downloads" sejam acessadas
    if folder not in ["audio_downloads", "video_downloads"]:
        return "Acesso negado.", 403
    return send_from_directory(folder, filename, as_attachment=True)
# --- FIM NOVO ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)