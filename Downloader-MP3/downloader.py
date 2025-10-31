import yt_dlp
import sys
import os
import time

def get_format_options(format_choice, download_path):
    postprocessor_mp3 = [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
    
    postprocessor_mp4 = [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }]

    if format_choice == 'mp3':
        return {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': postprocessor_mp3,
        }
    elif format_choice == 'mp4':
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': postprocessor_mp4,
        }
    else:
        return None

def get_valid_playlist_info():
    ydl_info_opts = {
        'quiet': True,        
        'extract_info': True, 
        'noplaylist': False,  
        'ignoreerrors': True, 
        'no_warnings': True,  
        'logtostderr': False, 
    }

    while True:
        playlist_url = input("Cole a URL da playlist do YouTube e pressione Enter:\n> ")
        if not playlist_url:
            print("Nenhuma URL fornecida. Tente novamente.")
            continue

        print("Validando URL e buscando vídeos...")
        
        try:
            with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' in info and info['entries']:
                
                playlist_title = info.get('title', 'Playlist Desconhecida')
                total_videos = len(info['entries'])

                print(f"✅ Playlist encontrada: '{playlist_title}'")
                print(f"   Total de {total_videos} vídeos detectados.")
                print("   (O script tentará baixar todos os vídeos disponíveis).")
                print("-------------------------------------------------")
                
                return info
            
            else:
                print("❌ Erro: A URL fornecida é de um vídeo único, não uma playlist.")
                print("   Por favor, forneça a URL completa da *playlist*.")
                print("   (Ex: https://www.youtube.com/playlist?list=...)\n")

        except Exception as e:
            print(f"\n❌ Erro ao processar a URL: {e}")
            print("   Verifique se o link está correto e tente novamente.\n")

def ask_for_format():
    print("\nEm qual formato você deseja baixar?")
    print("  1. MP3 (Apenas Áudio)")
    print("  2. MP4 (Vídeo + Áudio)")
    
    choice = ""
    while choice not in ['1', '2']:
        choice = input("Digite 1 ou 2:\n> ")
    
    return 'mp3' if choice == '1' else 'mp4'

def start_download_loop(playlist_info, base_ydl_opts):
    videos_para_baixar = playlist_info['entries']
    total_videos = len(videos_para_baixar)
    
    print(f"\nIniciando o download de {total_videos} vídeos...")
    print("-------------------------------------------------")

    for index, video_entry in enumerate(videos_para_baixar, start=1):
        if not video_entry:
            print(f"[{index}/{total_videos}] Item pulado (vídeo removido ou entrada vazia).")
            print("-------------------------------------------------")
            continue
            
        video_id = video_entry.get('id')
        video_title = video_entry.get('title', 'Título desconhecido')

        if not video_id:
            print(f"[{index}/{total_videos}] Item pulado: '{video_title}' (Vídeo indisponível ou ID não encontrado).")
            print("-------------------------------------------------")
            continue

        video_url_para_baixar = f"https://www.youtube.com/watch?v={video_id}"
            
        print(f"[{index}/{total_videos}] Baixando: {video_title}...")

        video_opts = base_ydl_opts.copy()
        video_opts['quiet'] = True
        video_opts['noprogress'] = True

        sucesso = False
        for attempt in range(1, 4):
            try:
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    ydl.download([video_url_para_baixar])
                
                print(f"    ✅ Concluído com sucesso!!")
                sucesso = True
                break 

            except Exception as e:
                print(f"    ❌ Erro na tentativa {attempt}: {e}")
                if attempt < 3:
                    print("       ...tentando novamente em 3 segundos...")
                    time.sleep(3) 
        
        if not sucesso:
            print(f"    ❌ FALHA: Não foi possível baixar '{video_title}' após 3 tentativas.")
            print("       Pulando para o próximo vídeo...")
        
        print("-------------------------------------------------")

    print("🎉 Fim do processo! Todos os vídeos foram processados.")

if __name__ == "__main__":
    
    playlist_info = get_valid_playlist_info()
    format_key = ask_for_format()
    
    download_folder = "audio" if format_key == 'mp3' else "video"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    base_options = get_format_options(format_key, download_folder)
    
    if base_options:
        start_download_loop(playlist_info, base_options)
    else:
        print("Erro interno: Opção de formato inválida. Saindo.")