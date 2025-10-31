import yt_dlp
import sys
import os

def get_format_options(format_choice, download_path):
    """Retorna o dicionário de opções para o yt-dlp com base na escolha do formato."""
    
    # Opções de Pós-processamento para MP3
    postprocessor_mp3 = [{
        'key': 'FFmpegExtractAudio',  # Informa que queremos extrair o áudio
        'preferredcodec': 'mp3',      # Define o formato de saída
        'preferredquality': '192',    # Define a qualidade (bitrate)
    }]
    
    # Opções de Pós-processamento para MP4
    # (Usamos 'bestvideo...' e o 'mergeoutputformat' para garantir que áudio e vídeo sejam unidos)
    postprocessor_mp4 = [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }]

    if format_choice == 'mp3':
        print("Configurando para baixar como MP3 (áudio)...")
        return {
            'format': 'bestaudio/best',  # Baixa apenas a melhor faixa de áudio
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), # Salva em /audio/Titulo.mp3
            'postprocessors': postprocessor_mp3,
            'ignoreerrors': True,  # Continua baixando outros vídeos da playlist se um falhar
            'noprogress': False,    # Mostrar progresso
        }
    elif format_choice == 'mp4':
        print("Configurando para baixar como MP4 (vídeo)...")
        return {
            # Baixa o melhor vídeo + melhor áudio e os junta
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), # Salva em /video/Titulo.mp4
            'postprocessors': postprocessor_mp4,
            'ignoreerrors': True,
            'noprogress': False,
        }
    else:
        return None

def download_playlist(url, ydl_opts):
    """Inicia o download usando as opções fornecidas."""
    
    print("\nIniciando o download... Isso pode demorar.")
    print("-------------------------------------------------")
    
    try:
        # Cria o objeto YoutubeDL com as opções
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Inicia o download da URL
            ydl.download([url])
            
        print("-------------------------------------------------")
        print(f"✅ Download concluído!")

    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Erro durante o download: {e}")
    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado: {e}")

# --- Início do Script ---
if __name__ == "__main__":
    
    # 1. Obter a URL da Playlist
    playlist_url = input("Cole a URL da playlist do YouTube e pressione Enter:\n> ")
    
    if not playlist_url:
        print("Nenhuma URL fornecida. Saindo.")
        sys.exit()

    # 2. Perguntar o formato
    print("\nEm qual formato você deseja baixar?")
    print("  1. MP3 (Apenas Áudio)")
    print("  2. MP4 (Vídeo + Áudio)")
    
    choice = ""
    while choice not in ['1', '2']:
        choice = input("Digite 1 ou 2:\n> ")

    format_key = 'mp3' if choice == '1' else 'mp4'
    
    # Cria pastas "audio" e "video" para organizar os downloads
    download_folder = "audio" if format_key == 'mp3' else "video"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # 3. Obter as opções corretas
    options = get_format_options(format_key, download_folder)
    
    if options:
        # 4. Iniciar o download
        download_playlist(playlist_url, options)
    else:
        print("Opção inválida. Saindo.")