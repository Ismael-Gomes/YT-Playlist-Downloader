# YouTube Playlist Saver (Downloader)

Um script simples em Python para baixar playlists inteiras do YouTube nos formatos MP4 (vídeo) ou MP3 (apenas áudio).

## Funcionalidades

* Download de playlists completas (ou vídeos individuais) apenas colando a URL.
* Opção de escolher o formato de saída:
    * **MP4**: Vídeo + Áudio, na melhor qualidade disponível.
    * **MP3**: Apenas Áudio, extraído e convertido (192kbps).
* Organiza os arquivos baixados automaticamente em pastas (`/video` ou `/audio`).

## ⚠️ Pré-requisitos

Para que este script funcione, você **PRECISA** ter duas dependências externas instaladas em seu sistema:

### 1. Python 3

O script foi escrito em Python. Você pode baixá-lo em [python.org](https://www.python.org/).

### 2. FFmpeg (Crucial!)

O **FFmpeg** é essencial para converter os arquivos para MP3 e para juntar os arquivos de áudio e vídeo (que o YouTube armazena separadamente) em um único MP4.

O script **não funcionará** sem ele.

#### Instalação do FFmpeg (Rápido)

Escolha o comando correspondente ao seu sistema operacional:

* **No macOS (via Homebrew):**
    ```bash
    brew install ffmpeg
    ```

* **No Linux (Ubuntu/Debian):**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

* **No Linux (Fedora):**
    ```bash
    sudo dnf install ffmpeg
    ```

* **No Windows:**
    1.  Baixe a build "release-full" mais recente em: [gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
    2.  Descompacte o arquivo (ex: em `C:\ffmpeg`).
    3.  Adicione a pasta `bin` (ex: `C:\ffmpeg\bin`) ao `PATH` do seu sistema (Variáveis de Ambiente).

Para verificar se funcionou, abra um novo terminal e digite `ffmpeg -version`.

## Como Rodar o Projeto

1.  **Clone este repositório:**
    ```bash
    git clone [https://github.com/Ismael-Gomes/YT-Playlist-Downloader.git](https://github.com/Ismael-Gomes/YT-Playlist-Downloader.git)
    cd ~/YT-Playlist-Downloader
    ```

2.  **(Opcional, mas recomendado) Crie um Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # (No macOS/Linux)
    .\venv\Scripts\activate   # (No Windows)
    ```

3.  **Instale as dependências Python:**
    Abra seu terminal na pasta do projeto e rode:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o script:**
    ```bash
    cd ~/Downloader-MP3/MP4
    python downloader.py
    ```

5.  **Siga as instruções no terminal:**
    * Primeiro, cole a URL da playlist do YouTube.
    * Depois, escolha `1` para MP3 ou `2` para MP4.

Os arquivos começarão a ser baixados e serão salvos na pasta `/audio` ou `/video`, criadas no mesmo local onde o script foi executado.

## Aviso Legal

Este projeto deve ser usado apenas para fins pessoais e para baixar conteúdo que você tenha permissão para baixar (como seus próprios vídeos, conteúdo de domínio público ou creative commons). Baixar vídeos protegidos por direitos autorais pode violar os Termos de Serviço do YouTube.