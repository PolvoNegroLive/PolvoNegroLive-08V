# Arquitetura V08
| Módulo | Função |
|---|---|
| `app/paths.py` | pasta de dados, assets (compatível com PyInstaller) |
| `app/settings.py`, `migration.py`, `secrets.py` | configuração persistente, migração, chaves protegidas (DPAPI) |
| `app/validation.py`, `errors.py` | validação antes de iniciar; classificação de erros |
| `app/ffcmd.py` | montagem dos comandos FFmpeg (entrada dshow, filtros, encoders, sender) |
| `app/hub.py` | distribuidor em Python (fila por tempo, quadro-chave) |
| `app/streamer.py` | motor: encoder, senders, estados, backoff, failover, relatório |
| `app/devices.py`, `components.py`, `hardware.py` | dispositivos e modos reais, FFmpeg, CPU/RAM/GPU |
| `app/performance.py` | Qualidade↔Desempenho e teste de configuração |
| `app/conntest.py` | teste de conexão por etapas |
| `app/ui/*` | tema, diálogos e páginas do painel |
Decisões: sem MediaMTX; sem GPU por suposição (testar encoders); sem afinidade de CPU por padrão; biblioteca padrão apenas.
