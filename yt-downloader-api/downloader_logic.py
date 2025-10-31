import yt_dlp
import os
import time

def get_format_options(format_choice, download_path):
    """Retorna o dicionário de opções para o yt-dlp com base na escolha do formato."""
    
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

def get_valid_playlist_info(playlist_url):
    """
    Valida uma URL de playlist e retorna as informações dela.
    Retorna (info_dict, error_message)
    """
    ydl_info_opts = {
        'quiet': True,
        'extract_info': True,
        'noplaylist': False,
        'ignoreerrors': True,
        'no_warnings': True,
        'logtostderr': False,
    }

    print(f"[API_LOGIC] Validando URL: {playlist_url}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
        
        if 'entries' in info and info['entries']:
            print(f"[API_LOGIC] Playlist '{info.get('title')}' validada.")
            return info, None 
        
        else:
            return None, "A URL fornecida é de um vídeo único, não uma playlist."

    except Exception as e:
        print(f"[API_LOGIC] Erro ao processar URL: {e}")
        return None, f"Erro ao processar a URL: {e}"

def start_download_loop(playlist_info, base_ydl_opts):
    """
    Baixa os vídeos da playlist (função de biblioteca).
    Retorna uma tupla: (lista_sucessos, lista_falhas)
    """
    videos_para_baixar = playlist_info['entries']
    total_videos = len(videos_para_baixar)
    successes = []
    failures = []

    print(f"[API_LOGIC] Iniciando download de {total_videos} vídeos...")

    for index, video_entry in enumerate(videos_para_baixar, start=1):
        
        if not video_entry:
            print(f"[API_LOGIC] Item pulado (entrada vazia).")
            failures.append(f"Vídeo {index} (entrada vazia)")
            continue
            
        video_id = video_entry.get('id')
        video_title = video_entry.get('title', 'Título desconhecido')

        if not video_id:
            print(f"[API_LOGIC] Item pulado: '{video_title}' (ID não encontrado).")
            failures.append(f"{video_title} (ID não encontrado)")
            continue
        
        video_url_para_baixar = f"https://www.youtube.com/watch?v={video_id}"
            
        print(f"[API_LOGIC] [{index}/{total_videos}] Baixando: {video_title}...")

        video_opts = base_ydl_opts.copy()
        video_opts['quiet'] = True
        video_opts['noprogress'] = True

        sucesso = False
        for attempt in range(1, 4): 
            try:
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    ydl.download([video_url_para_baixar])
                
                print(f"[API_LOGIC] [{index}/{total_videos}] Sucesso: {video_title}")
                sucesso = True
                break 
            except Exception as e:
                print(f"[API_LOGIC] Erro na tentativa {attempt} para '{video_title}': {e}")
                time.sleep(3) 
        
        if sucesso:
            successes.append(video_title)
        else:
            print(f"[API_LOGIC] FALHA FINAL para '{video_title}'")
            failures.append(video_title)
    
    print("[API_LOGIC] Fim do processo de download.")
    return (successes, failures)