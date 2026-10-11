 <p align="center">
  <img src="Imagem/logo.png" width="220" alt="Logo oficial do Polvo Negro Live">
</p>

<h1 align="center">🐙 Polvo Negro Live V08</h1>

<p align="center">
  <strong>Captura, processamento e transmissão de áudio e vídeo para computadores Windows, incluindo máquinas com recursos limitados.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plataforma-Windows%2010%2F11-blue" alt="Plataforma Windows">
  <img src="https://img.shields.io/badge/Processamento-FFmpeg-green" alt="Processamento FFmpeg">
  <img src="https://img.shields.io/badge/Interface-Python%20%2B%20Tkinter-orange" alt="Interface Python e Tkinter">
  <img src="https://img.shields.io/badge/Projeto-Em%20desenvolvimento-yellow" alt="Projeto em desenvolvimento">
</p>

---

## 📌 Sobre o projeto

O **Polvo Negro Live** é um sistema modular desenvolvido por **Diêgo Botelho Pereira**, com o objetivo de facilitar a captura, o processamento e a transmissão de áudio e vídeo em computadores Windows.

A proposta é oferecer uma alternativa leve e modular para transmissões ao vivo, especialmente para usuários que enfrentam limitações de hardware ou dificuldades com programas de transmissão mais pesados.

O sistema utiliza ferramentas como Python e FFmpeg para organizar a captura de dispositivos de vídeo e áudio, o processamento dos sinais e o envio para destinos compatíveis com RTMP ou RTMPS.

O projeto está em desenvolvimento contínuo. Os recursos disponíveis devem ser considerados conforme o código e os testes realizados em cada versão.

## 🖼️ Identidade visual

A identidade visual do Polvo Negro Live deve manter o logotipo oficial do aplicativo separado das artes promocionais e das imagens conceituais.

### Logo oficial

<p align="center">
  <img src="Imagem/logo.png" width="180" alt="Logotipo oficial do Polvo Negro Live">
</p>

### Arte de apresentação

A imagem abaixo é uma arte conceitual de apresentação do projeto. Ela não representa necessariamente uma captura de tela real da interface.

<p align="center">
  <img src="Imagem/arte-conceitual.png" width="850" alt="Arte conceitual de apresentação do Polvo Negro Live">
</p>

> **Importante:** os caminhos das imagens acima devem corresponder aos arquivos reais existentes no repositório. Se os nomes ou as pastas forem diferentes, ajuste os caminhos para os arquivos corretos. Não crie imagens fictícias para preencher espaços reservados.

---

## 🎯 Objetivos

- Oferecer uma alternativa modular para captura e transmissão ao vivo.
- Permitir o uso de câmeras e placas de captura USB compatíveis.
- Utilizar o FFmpeg para processamento de áudio e vídeo.
- Organizar transmissões para diferentes destinos de streaming.
- Facilitar o diagnóstico de problemas de conexão e transmissão.
- Reduzir a complexidade de uso em computadores modestos.
- Manter uma estrutura de projeto que permita manutenção e evolução.

## ⚙️ Recursos do sistema

Conforme implementados no código do projeto, os recursos podem incluir:

- **Captura de vídeo:** integração com dispositivos compatíveis com DirectShow.
- **Captura de áudio:** utilização de dispositivos de áudio compatíveis.
- **Processamento:** utilização do FFmpeg para codificação e manipulação de áudio e vídeo.
- **Formatos de transmissão:** suporte planejado ou implementado para formatos horizontais e verticais.
- **Destinos independentes:** organização de processos de envio para destinos RTMP/RTMPS.
- **Reconexão automática:** tentativas de recuperação de conexões interrompidas.
- **Diagnóstico:** verificações de conectividade e possíveis falhas de transmissão.
- **Registros de execução:** logs para auxiliar na identificação de problemas.
- **Interface gráfica:** painel desenvolvido com Python e Tkinter.
- **Configurações:** armazenamento local de preferências e parâmetros do aplicativo.

> A disponibilidade de cada recurso depende da versão atual do código. Consulte a documentação e os testes antes de considerar uma função concluída.

## 🧩 Como funciona

O fluxo geral de processamento foi concebido para organizar as etapas de captura, codificação e transmissão:

```text
┌──────────────────────────────┐
│ Câmera ou placa de captura   │
│ USB / dispositivos de áudio  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Captura e processamento      │
│ FFmpeg                       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Gerenciamento dos fluxos     │
│ e perfis de transmissão      │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│ Destino RTMP │ │ Destino RTMPS│
└──────────────┘ └──────────────┘
```

O diagrama apresenta a arquitetura conceitual. A implementação efetiva, a quantidade de processos e o funcionamento de cada etapa devem ser confirmados no código da versão utilizada.

## 💻 Requisitos

### Sistema operacional

- Windows 10 ou Windows 11, preferencialmente em 64 bits.
- Permissões adequadas para executar os scripts e acessar os dispositivos.
- Drivers compatíveis com a câmera, placa de captura e dispositivos de áudio.

### Dependências

- Python 3.10 ou superior, quando executado pelo código-fonte.
- FFmpeg de 64 bits, disponível no sistema ou configurado conforme a documentação.
- Tcl/Tk, necessário para a interface gráfica Tkinter.
- Pillow, quando exigido pelas ferramentas de geração ou preparação de imagens.

> O FFmpeg e outras dependências externas não devem ser considerados incluídos no programa sem confirmação dos arquivos de distribuição.

## 🚀 Como iniciar

Os nomes e a disponibilidade dos arquivos abaixo devem ser conferidos no repositório.

### 1. Obter o projeto

Baixe ou clone o repositório:

```bash
git clone https://github.com/PolvoNegroLive/PolvoNegroLive-01V.git
cd PolvoNegroLive-01V
```

### 2. Verificar o computador

Se o arquivo estiver disponível, execute:

```text
VERIFICAR_PC.bat
```

Esse script deve ser utilizado conforme as instruções implementadas no projeto.

### 3. Iniciar o aplicativo

Se o arquivo estiver disponível, execute:

```text
INICIAR_POLVO_NEGRO_LIVE.bat
```

### 4. Criar o executável

Caso o processo de empacotamento esteja configurado, utilize:

```text
CRIAR_EXE.bat
```

Os scripts podem depender da instalação do Python, do FFmpeg e de outras ferramentas. Consulte as mensagens apresentadas no terminal em caso de erro.

## 🛠️ Estrutura do projeto

Uma estrutura organizada facilita a manutenção do código, a distribuição e a contribuição de outras pessoas.

```text
PolvoNegroLive-01V/
├── Imagem/
│   ├── logo.png
│   ├── arte-conceitual.png
│   ├── icones/
│   ├── apresentacao/
│   └── painel/
├── docs/
│   ├── ARQUITETURA.md
│   ├── SECURITY.md
│   ├── CHANGELOG.md
│   └── CONTRIBUTING.md
├── scripts/
├── tests/
├── tools/
├── README.md
├── VERIFICAR_PC.bat
├── INICIAR_POLVO_NEGRO_LIVE.bat
└── CRIAR_EXE.bat
```

> Esta é uma estrutura de referência, não uma declaração de que todos esses arquivos e diretórios já existem. Preserve os arquivos reais do projeto e adapte a documentação à estrutura efetivamente presente no repositório.

### Organização das imagens

A pasta principal `Imagem/` deve concentrar os recursos visuais do projeto:

- **Logo oficial:** imagem usada como identidade visual do aplicativo.
- **Ícones:** elementos gráficos usados na interface.
- **Apresentação:** capas e artes promocionais.
- **Painel:** imagens reais da interface, quando disponíveis.
- **Outros:** recursos visuais auxiliares.

Ao mover imagens, atualize os caminhos usados pelo código, pelo README, pelos scripts e pelo empacotamento do aplicativo. Não remova arquivos necessários à execução.

## 🧪 Testes e validação

Os testes devem ser executados antes de considerar uma alteração concluída.

Se o projeto possuir a pasta de testes configurada, utilize:

```bash
python -m unittest discover -s tests -v
```

Se existir um script específico para testes no Windows, siga as instruções correspondentes, por exemplo:

```text
scripts\TESTES.bat
```

### O que precisa ser validado

- Inicialização do programa.
- Carregamento da interface gráfica.
- Localização das imagens e dos recursos visuais.
- Disponibilidade do FFmpeg.
- Detecção dos dispositivos de captura.
- Configuração dos destinos de transmissão.
- Funcionamento dos logs e diagnósticos.
- Persistência e proteção das configurações.
- Geração do executável, quando aplicável.
- Compatibilidade com o Windows de destino.

Testes automatizados não substituem os testes reais de captura e transmissão em um computador Windows.

## 🔐 Segurança e privacidade

A segurança das configurações e das credenciais é essencial em qualquer aplicativo de transmissão.

Recomendações para o desenvolvimento e a distribuição:

- Não publicar chaves de transmissão, senhas, tokens ou credenciais.
- Não incluir arquivos pessoais ou logs com dados sensíveis no repositório.
- Não registrar chaves completas em mensagens de erro.
- Proteger as configurações locais de acordo com os recursos disponíveis no sistema operacional.
- Verificar as permissões e o conteúdo dos arquivos antes de publicar alterações.
- Manter as instruções de segurança atualizadas.

Consulte [`docs/SECURITY.md`](docs/SECURITY.md), caso esse arquivo exista no repositório.

## 📚 Documentação

A documentação complementar pode incluir:

- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — organização e funcionamento interno.
- [`docs/SECURITY.md`](docs/SECURITY.md) — segurança e proteção de configurações.
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — histórico de alterações.
- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — orientações para contribuição.

Os links acima pressupõem que os arquivos existam nesses caminhos. Ajuste-os se a documentação estiver organizada de outra forma.

## 🗺️ Estado atual e limitações

O Polvo Negro Live é um projeto em desenvolvimento. A estabilidade e a compatibilidade podem variar conforme o hardware, os drivers, a versão do FFmpeg e a configuração dos destinos de transmissão.

Algumas funcionalidades precisam ser verificadas em ambiente Windows real, principalmente:

- Captura DirectShow.
- Compatibilidade dos dispositivos de áudio e vídeo.
- Proteção de credenciais no Windows.
- Geração e execução do instalador ou executável.
- Transmissão real para destinos RTMP/RTMPS.
- Desempenho em computadores com recursos limitados.

Não considere uma funcionalidade concluída apenas porque está descrita neste README. A implementação e os resultados dos testes devem ser a referência.

## 🤝 Contribuições

Contribuições que melhorem a estabilidade, a compatibilidade, a documentação, a interface e o desempenho são bem-vindas.

Antes de propor alterações:

1. Analise a arquitetura atual.
2. Preserve os recursos que já funcionam.
3. Evite dependências desnecessárias.
4. Atualize a documentação quando houver mudanças.
5. Execute os testes disponíveis.
6. Informe limitações que ainda não foram resolvidas.

Consulte as orientações de contribuição do projeto, caso estejam disponíveis.

## 📄 Licença

A licença do projeto deve ser definida pelo responsável pelo repositório.

Até que exista um arquivo de licença válido, não presuma que o código esteja liberado para redistribuição ou uso irrestrito. Caso a licença já esteja definida, informe aqui o nome correto e vincule o arquivo correspondente.

## 👨‍💻 Autor

**Diêgo Botelho Pereira**

Projeto: **Polvo Negro Live V08**

Repositório oficial: [PolvoNegroLive-01V no GitHub](https://github.com/PolvoNegroLive/PolvoNegroLive-01V)

---

<p align="center">
  🐙 <strong>Polvo Negro Live</strong><br>
  <em>Transmissão modular, acessível e pensada para diferentes configurações de computador.</em>
</p>
