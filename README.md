 <p align="center">
  <img src="Imagem/logo.png" width="220" alt="Logotipo oficial do Polvo Negro Live">
</p>

<h1 align="center">🐙 Polvo Negro Live</h1>

<p align="center">
  <strong>Sistema modular de captura, processamento e transmissão de áudio e vídeo para Windows, com foco em computadores com recursos limitados.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plataforma-Windows%2010%2F11-blue" alt="Windows 10 e 11">
  <img src="https://img.shields.io/badge/Processamento-FFmpeg-green" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Interface-Python%20%2B%20Tkinter-orange" alt="Python e Tkinter">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow" alt="Projeto em desenvolvimento">
</p>

---

## 📌 Sobre o projeto

O **Polvo Negro Live** é um projeto desenvolvido por **Diêgo Botelho Pereira**, com o objetivo de facilitar a captura, o processamento e a transmissão de áudio e vídeo em computadores Windows.

A proposta é oferecer uma solução modular e adaptável, inclusive para computadores com recursos limitados.

O sistema utiliza Python para a aplicação e FFmpeg para tarefas de processamento de mídia, de acordo com os recursos implementados no código.

O projeto continua em desenvolvimento. A disponibilidade e a estabilidade das funcionalidades dependem da implementação existente e dos testes realizados.

## 🖥️ Interface do programa

As imagens a seguir apresentam as principais áreas da interface. Os arquivos ficam organizados na pasta `Imagem/` do repositório.

### Painel principal

<p align="center">
  <img src="Imagem/painel-principal.png" width="100%" alt="Painel principal do Polvo Negro Live">
</p>

### Configurações

<p align="center">
  <img src="Imagem/painel-configuracoes.png" width="100%" alt="Painel de configurações do Polvo Negro Live">
</p>

### Transmissão

<p align="center">
  <img src="Imagem/painel-transmissao.png" width="100%" alt="Painel de transmissão do Polvo Negro Live">
</p>

### Diagnóstico

<p align="center">
  <img src="Imagem/painel-diagnostico.png" width="100%" alt="Painel de diagnóstico do Polvo Negro Live">
</p>

## 🖼️ Organização de imagens e fotografias

A pasta `Imagem/` é o diretório principal destinado aos recursos visuais do projeto.

Ela pode conter logotipos, fotografias, capturas de tela, ilustrações, artes de apresentação, ícones e outros arquivos de imagem.

### Formatos de arquivo

A organização dos arquivos não deve ficar limitada exclusivamente ao formato PNG. Conforme as ferramentas utilizadas e a finalidade do arquivo, podem ser armazenados formatos como:

- **PNG:** imagens com transparência e capturas de tela.
- **JPG e JPEG:** fotografias e imagens compactadas.
- **WEBP:** imagens compactadas para a web.
- **GIF:** imagens animadas ou estáticas.
- **BMP:** imagens bitmap.
- **TIFF e TIF:** imagens de alta qualidade.
- **SVG:** logotipos e gráficos vetoriais.
- **ICO:** ícones de aplicativos.
- **AVIF:** imagens modernas com compressão eficiente.
- **HEIC e HEIF:** fotografias de dispositivos compatíveis.
- **RAW e outros formatos de fotografia:** arquivos originais de câmeras, quando necessários.

A lista é ilustrativa, não uma garantia de que todos esses formatos serão exibidos pelo GitHub, abertos pelo aplicativo ou processados pelas ferramentas do projeto.

**Importante:** o repositório pode armazenar diferentes tipos de arquivo, mas a visualização direta no README depende do suporte do GitHub. A abertura e o processamento dentro do aplicativo dependem das bibliotecas e dos recursos implementados.

### Arquivos de referência

```text
Imagem/
├── logo.png
├── painel-principal.png
├── painel-configuracoes.png
├── painel-transmissao.png
└── painel-diagnostico.png
```

Esses são os nomes dos cinco arquivos principais de apresentação. Outros arquivos de imagem podem ser adicionados à mesma pasta sem que todos precisem ser renomeados para PNG.

O logotipo oficial usado pelo aplicativo deve continuar compatível com o caminho de arquivo utilizado pelo código.

## 🎯 Objetivos

- Facilitar a captura e a transmissão ao vivo.
- Permitir o uso de câmeras e placas de captura USB compatíveis.
- Utilizar o FFmpeg para processamento de áudio e vídeo.
- Organizar transmissões para destinos RTMP/RTMPS.
- Facilitar o diagnóstico de problemas de conexão.
- Buscar um funcionamento eficiente em computadores modestos.
- Manter o código e os recursos visuais organizados.

## ⚙️ Recursos do sistema

Conforme implementados no código, os recursos podem incluir:

- Captura de vídeo por dispositivos compatíveis com DirectShow.
- Captura de áudio por dispositivos compatíveis.
- Processamento de mídia com FFmpeg.
- Organização de perfis horizontais e verticais.
- Gerenciamento de destinos de streaming.
- Tentativas de reconexão.
- Diagnóstico de conectividade.
- Registros para investigação de erros.
- Interface gráfica desenvolvida com Python e Tkinter.
- Armazenamento local de configurações.

A presença de cada recurso deve ser confirmada na implementação atual.

## 🧩 Arquitetura conceitual

```text
┌────────────────────────────────┐
│ Câmera / placa de captura USB  │
│ Dispositivos de áudio          │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ Captura e processamento        │
│ FFmpeg                         │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ Gerenciamento dos fluxos       │
│ e perfis de transmissão        │
└───────────────┬────────────────┘
                │
          ┌─────┴─────┐
          ▼           ▼
┌───────────────┐ ┌───────────────┐
│ Destino RTMP  │ │ Destino RTMPS │
└───────────────┘ └───────────────┘
```

Este diagrama representa o fluxo conceitual. A arquitetura efetiva depende da implementação do programa.

## 💻 Requisitos

### Sistema operacional

- Windows 10 ou Windows 11, preferencialmente de 64 bits.
- Drivers compatíveis com os dispositivos utilizados.
- Permissões adequadas para acessar os dispositivos e arquivos.

### Dependências

- Python 3.10 ou superior, quando executado pelo código-fonte.
- FFmpeg de 64 bits, conforme a configuração do projeto.
- Tcl/Tk para a interface baseada em Tkinter.
- Pillow ou outras bibliotecas, quando exigidas pelos recursos implementados.

A inclusão dessas dependências no executável depende do processo de distribuição.

## 🚀 Como executar

Clone o repositório:

```bash
git clone https://github.com/PolvoNegroLive/PolvoNegroLive-01V.git
cd PolvoNegroLive-01V
```

Se os scripts correspondentes estiverem presentes, execute no Windows:

**Verificar o computador**

```text
VERIFICAR_PC.bat
```

**Iniciar o aplicativo**

```text
INICIAR_POLVO_NEGRO_LIVE.bat
```

**Criar o executável**

```text
CRIAR_EXE.bat
```

Os scripts e suas dependências devem ser conferidos no repositório antes da execução.

## 📁 Estrutura do projeto

```text
PolvoNegroLive-01V/
├── Imagem/
│   ├── logo.png
│   ├── painel-principal.png
│   ├── painel-configuracoes.png
│   ├── painel-transmissao.png
│   └── painel-diagnostico.png
├── docs/
├── scripts/
├── tests/
├── tools/
└── README.md
```

A estrutura é ilustrativa. Mantenha os diretórios e arquivos que realmente existem no projeto.

## 🧪 Testes e validação

Se os testes estiverem configurados, execute:

```bash
python -m unittest discover -s tests -v
```

Valide a inicialização, a interface, a localização das imagens, a disponibilidade do FFmpeg, a captura dos dispositivos, os destinos de transmissão e a geração do executável, quando aplicável.

Os testes automatizados não substituem a verificação real de captura e transmissão no Windows.

## 🔐 Segurança e privacidade

- Não publique chaves de transmissão, senhas ou tokens.
- Não inclua arquivos pessoais ou logs com dados sensíveis.
- Evite registrar credenciais completas nos logs.
- Preserve a proteção das configurações locais.
- Confira os arquivos antes de publicar alterações no repositório.

## 📚 Documentação complementar

Caso existam no repositório, consulte:

- `docs/ARQUITETURA.md` — arquitetura interna.
- `docs/SECURITY.md` — segurança.
- `docs/CHANGELOG.md` — histórico de alterações.
- `docs/CONTRIBUTING.md` — orientações para contribuições.

Mantenha os caminhos correspondentes aos arquivos reais.

## 🗺️ Estado atual e limitações

O Polvo Negro Live está em desenvolvimento. A compatibilidade pode variar conforme o hardware, os drivers, as dependências e os destinos de transmissão.

Os recursos devem ser considerados concluídos somente quando a implementação e os testes correspondentes confirmarem seu funcionamento.

## 🤝 Contribuições

Contribuições para melhorar a estabilidade, a compatibilidade, a documentação e o desempenho são bem-vindas.

Ao modificar o projeto:

1. Preserve os recursos existentes.
2. Evite dependências desnecessárias.
3. Atualize os caminhos dos arquivos quando necessário.
4. Atualize a documentação.
5. Execute os testes disponíveis.
6. Registre as limitações conhecidas.

## 📄 Licença

A licença deve corresponder àquela efetivamente definida pelo responsável pelo projeto. Não presuma permissões de redistribuição ou uso irrestrito sem uma licença aplicável.

## 👨‍💻 Autor

**Diêgo Botelho Pereira**

**Projeto:** Polvo Negro Live

**Repositório:** [PolvoNegroLive no GitHub](https://github.com/PolvoNegroLive/PolvoNegroLive-01V)

---

<p align="center">
  <strong>🐙 Polvo Negro Live</strong><br>
  <em>Captura e transmissão modular para Windows.</em>
</p>
