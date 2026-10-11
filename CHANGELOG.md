# Changelog
## 8.0.0
* Novo painel escuro com 7 páginas e **logo clicável** (hover/pressionado/ao vivo, menu com botão direito, marca d'água).
* Dados em `%APPDATA%\PolvoNegroLive` com `schema` e migração (importa V04–V07) + backup automático. **Chaves protegidas (DPAPI).**
* **Validação antes de iniciar** (FPS acima da câmera, bitrate absurdo, chave/entrada duplicada, URL/porta, áudio ausente) com diálogo corrigir/usar mesmo assim.
* **Estados por destino** (IDLE/CONNECTING/CONNECTED/STREAMING/RECONNECTING/ERROR/STOPPING/STOPPED), backoff 5–60 s, suspensão e REINICIAR, failover para servidor de backup.
* **Hub com fila por tempo** (corrige a queda a bitrates altos), ressincronização no quadro-chave.
* **Classificação de erros** em 13 classes com explicação e ação; `errors.log` e um log por destino.
* Controle **Qualidade ↔ Desempenho**, reserva do Windows e **teste de configuração de 10 s**.
* Teste de conexão por etapas (URL → DNS → TCP → TLS → publicação).
* Correção do enquadramento "cortar" (proporção invertida, existia desde a V04).
* URL de backup do YouTube montada corretamente (`…/live2/CHAVE?backup=1`).
* Scripts de instalação (PyInstaller + Inno Setup) — NÃO TESTADOS no Windows.
