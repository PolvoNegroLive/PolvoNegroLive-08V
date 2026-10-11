# Segurança

## Chaves de transmissão
- Nunca publique chaves de transmissão (YouTube, TikTok, Restream etc.) em issues, prints, logs ou pull requests.
- O programa guarda as chaves em `%APPDATA%\PolvoNegroLive`, protegidas por DPAPI do Windows. Essa pasta nunca deve ser enviada ao repositório.
- Os logs mascaram as chaves, mas processos externos (FFmpeg) recebem a chave na linha de comando; outros programas na mesma máquina podem, em teoria, enxergá-la.
- Se uma chave vazar, **gere outra** na plataforma imediatamente.

## Reportar uma vulnerabilidade
Abra uma issue **sem detalhes sensíveis** pedindo contato privado, ou use "Security → Report a vulnerability" do GitHub, se estiver habilitado.
