<p align="center"><img src="docs/img/logo.png" width="280" alt="Polvo Negro Live"></p>

# 🐙 Polvo Negro Live (V08)

**Sistema modular de captura, processamento e transmissão de áudio e vídeo para Windows 10/11, pensado para computadores modestos.**

Câmera ou placa de captura USB (DirectShow) → FFmpeg → envio independente para vários destinos RTMP/RTMPS (YouTube, TikTok, Restream ou servidor próprio).

Desenvolvido por **Diêgo Botelho Pereira**. Projeto em desenvolvimento: veja as [limitações conhecidas](#-estado-atual-e-limitações).

> 🖼️ A imagem abaixo é uma **arte conceitual** de apresentação, não uma captura de tela real do programa.

![Arte conceitual do Polvo Negro Live](docs/img/arte-conceitual.png)

## 🎯 Objetivo
Oferecer uma alternativa mais enxuta a softwares de streaming tradicionais, abrindo a câmera **uma vez**, codificando por perfil e enviando para cada destino de forma independente. O objetivo é reduzir trabalho duplicado; o consumo real depende do processador, da memória, do encoder, da câmera e da internet. Ainda não há medições comparativas com outros programas.

## ✨ Recursos implementados (conforme o código)
- Captura de vídeo e áudio via DirectShow (câmeras e placas USB).
- Codificação com FFmpeg, perfis de saída 16:9 e 9:16.
- Múltiplos destinos RTMP/RTMPS, cada um em seu próprio processo: se um cair, os outros continuam.
- Reconexão automática (espera de 5, 10, 20, 40 e 60 s; suspende após 8 falhas, com botão REINICIAR).
- Servidor de backup (failover) por destino.
- Validação antes de iniciar (FPS acima da câmera, bitrate absurdo, chave duplicada, URL/porta, áudio ausente).
- Controle Qualidade ↔ Desempenho e teste de configuração de 10 s.
- Teste de conexão por etapas: URL → DNS → TCP → TLS → publicação.
- Logs separados (engine, encoder, rede, erros e um por destino), com chaves mascaradas.
- Chaves protegidas com DPAPI do Windows; configurações em `%APPDATA%\PolvoNegroLive`, com migração das versões V04–V07.
- Painel gráfico (Tkinter) com 7 páginas: Início, Captura, Destinos, Qualidade, Diagnóstico, Logs e Configurações.

## ⚙️ Arquitetura
```text
CÂMERA / PLACA USB → ENCODER (1 FFmpeg por perfil) → HUB local (fila por tempo)
        → 1 processo de envio por destino (-c copy → RTMP/RTMPS)
```
Detalhes em [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## 💻 Requisitos
- Windows 10 ou 11 de 64 bits.
- **Python 3.10+ com Tcl/Tk** ([python.org](https://www.python.org/downloads/), marque "tcl/tk and IDLE" na instalação).
- **FFmpeg 64 bits** no PATH, ou em `ffmpeg\bin\ffmpeg.exe` ao lado do programa. O FFmpeg **não vem incluído** neste repositório; baixe de [ffmpeg.org](https://ffmpeg.org/download.html) e confira a licença da build escolhida.
- Não há dependências Python externas para rodar o programa (`Pillow` só é usado em `tools/make_assets.py`).

## 🚀 Como usar no Windows
1. Baixe o ZIP em **[Releases](../../releases)** (ou use *Code → Download ZIP*) e extraia **toda** a pasta.
2. Dê dois cliques em `VERIFICAR_PC.bat`: ele confere Python, Tkinter e FFmpeg e **não instala nada**.
3. Dê dois cliques em `INICIAR_POLVO_NEGRO_LIVE.bat` para abrir o painel.
   Para ver mensagens de erro no CMD, rode na pasta: `python POLVO_NEGRO_LIVE.py`
4. **Captura:** escolha vídeo e áudio e clique em *Testar câmera*.
5. **Destinos:** informe servidor e **a chave de cada plataforma** (uma chave por destino). Use *Testar conexão*; fora de uma live no ar, use também *Testar publicação*.
6. **Qualidade:** ajuste, aplique e rode *Testar configuração (10 s)*.
7. **Início → Iniciar live.**

## 🧪 Testes
```bat
scripts\TESTES.bat
```
ou `python -m unittest discover -s tests -v`.

Situação verificada: os 13 testes automatizados (1 ignorado) passam em **Linux com Python 3.12** (ambiente de revisão). **Ainda não verificado em Windows real:** captura DirectShow, DPAPI, geração do instalador (PyInstaller/Inno Setup) e transmissão com contas reais.

## 🔐 Segurança
- Nunca publique chaves de transmissão, logs ou a pasta `%APPDATA%\PolvoNegroLive`.
- Leia [SECURITY.md](SECURITY.md).

## 🛠️ Instalador (opcional)
`CRIAR_EXE.bat` usa PyInstaller + Inno Setup 6. **Esses scripts ainda não foram testados em Windows.**

## ⚠️ Estado atual e limitações
- Projeto em desenvolvimento; funciona como alternativa em evolução, não como substituto completo de outros softwares.
- Desempenho depende do hardware; não há garantia de funcionar em qualquer computador.
- Plataformas e encoders aceitos dependem do que o FFmpeg instalado oferece.

## 📜 Histórico
Veja o [CHANGELOG.md](CHANGELOG.md).

## 🤝 Contribuir
Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licença
**A definir pelo autor.** Até existir um arquivo `LICENSE`, todos os direitos permanecem reservados ao autor.

## 👨‍💻 Autor
**Diêgo Botelho Pereira**
