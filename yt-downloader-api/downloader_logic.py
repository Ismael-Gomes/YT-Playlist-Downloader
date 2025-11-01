import yt_dlp
import os
import time

# --- OPÇÕES GLOBAIS DE REDE PARA EVITAR BLOQUEIO ---
# Estas opções são cruciais para o deploy em servidores de produção (Render)
PRODUCTION_NETWORK_OPTS = {
    'retries': 3,                 # Tenta novamente em caso de falha de rede
    'socket_timeout': 10,         # Timeout de conexão mais curto para falhar rápido
    'no_warnings': True,
    'ignoreerrors': True,         # Ignora erros em vídeos individuais (útil em playlists)
    'http_chunk_size': 10485760,  # Otimiza o tamanho do chunk para download
    'geo_bypass': True,           # Tenta evitar bloqueios geográficos
    'noprogress': True,           # Remove a barra de progresso (reduz a saída do log)
}

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

    # Opções básicas do formato
    base_options = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'logtostderr': False,
        'merge_output_format': 'mp4', # Necessário para o postprocessor do MP4
    }
    
    if format_choice == 'mp3':
        format_opts = {
            'format': 'bestaudio/best',
            'postprocessors': postprocessor_mp3,
        }
    elif format_choice == 'mp4':
        format_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': postprocessor_mp4,
        }
    else:
        return None
        
    # Combina as opções do formato com as opções de rede de produção
    return {**base_options, **format_opts, **PRODUCTION_NETWORK_OPTS}


def get_valid_playlist_info(playlist_url):
    """
    Valida uma URL de playlist e retorna as informações dela.
    Retorna (info_dict, error_message)
    """
    ydl_info_opts = {
        'extract_info': True,
        'noplaylist': False,
        'ignoreerrors': True,
        'logtostderr': False,
        'skip_download': True, 
        'quiet': True,        
        'noprogress': True,   
        'logtostderr': False, 
        'no_warnings': True,
        'dump_single_json': True,  # Força a extração de info sem processar o arquivo individualmente
        'flat_playlist': True,

        **PRODUCTION_NETWORK_OPTS
    }

    # Combina as opções de info com as de rede
    final_info_opts = {**ydl_info_opts, **PRODUCTION_NETWORK_OPTS}

    print(f"[API_LOGIC] Validando URL: {playlist_url}")
    
    try:
        with yt_dlp.YoutubeDL(final_info_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
        
        # O yt-dlp pode retornar um vídeo único mesmo se for uma playlist, então verificamos 'entries'
        if 'entries' in info and info['entries']:
            print(f"[API_LOGIC] Playlist '{info.get('title')}' validada.")
            return info, None 
        
        else:
            return None, "A URL fornecida é de um vídeo único, não uma playlist, ou está bloqueada."

    except Exception as e:
        print(f"[API_LOGIC] Erro ao processar URL: {e}")
        return None, f"Erro ao processar a URL. O YouTube pode estar bloqueando a requisição do servidor. (Erro: {e})"


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

    # Aumentar o timeout e a resiliência no loop de download
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

        # Clonamos as opções base que já contém as otimizações de rede
        video_opts = base_ydl_opts.copy()

        sucesso = False
        # Tentaremos 3 vezes antes de desistir
        for attempt in range(1, 4): 
            try:
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    ydl.download([video_url_para_baixar])
                
                print(f"[API_LOGIC] [{index}/{total_videos}] Sucesso: {video_title}")
                sucesso = True
                break 
            except yt_dlp.utils.DownloadError as e:
                # O bloqueio por login/CAPTCHA geralmente gera um DownloadError
                if "Sign in to confirm you’re not a bot" in str(e):
                    print(f"[API_LOGIC] Bloqueio do YouTube detectado para '{video_title}'. Abortando tentativas.")
                    break # Se for bloqueio, tentar mais vezes não adianta
                
                print(f"[API_LOGIC] Erro na tentativa {attempt} para '{video_title}': {e}")
                time.sleep(3) # Pausa para tentar novamente
            except Exception as e:
                print(f"[API_LOGIC] Erro genérico na tentativa {attempt} para '{video_title}': {e}")
                time.sleep(3) 
        
        if sucesso:
            successes.append(video_title)
        else:
            # Informamos se a falha foi por bloqueio
            if not sucesso and attempt >= 3:
                failures.append(f"{video_title} (Falha de Download/Rede)")
            else:
                 failures.append(f"{video_title} (Bloqueado/Indisponível)")
    
    print("[API_LOGIC] Fim do processo de download.")
    return (successes, failures)