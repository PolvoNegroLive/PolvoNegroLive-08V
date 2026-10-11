 <p align="center">
  <img src="Imagem/logo.png" width="220" alt="Logotipo oficial do Polvo Negro Live">
</p>

<h1 align="center">🐙 Polvo Negro Live V08</h1>

<p align="center">
  <strong>Captura, processamento e transmissão de áudio e vídeo para Windows, com foco em modularidade e computadores com recursos limitados.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plataforma-Windows%2010%2F11-blue" alt="Windows 10 e 11">
  <img src="https://img.shields.io/badge/Processamento-FFmpeg-green" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Interface-Python%20%2B%20Tkinter-orange" alt="Python e Tkinter">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow" alt="Em desenvolvimento">
</p>

---

## 📌 Sobre o projeto

O **Polvo Negro Live** é um projeto desenvolvido por **Diêgo Botelho Pereira** para facilitar a captura, o processamento e a transmissão de áudio e vídeo em computadores Windows.

A proposta é oferecer uma alternativa modular para transmissões ao vivo, considerando também computadores com recursos limitados e usuários que precisam de uma solução adaptável.

O sistema utiliza Python para a aplicação e o FFmpeg para tarefas de processamento de mídia, conforme os recursos implementados no código.

O projeto está em desenvolvimento contínuo. A disponibilidade e a estabilidade das funcionalidades dependem da versão, dos dispositivos utilizados e dos testes realizados.

## 🖥️ Interface do programa

A seguir estão as quatro imagens horizontais destinadas à apresentação das áreas do aplicativo.

### 1. Painel principal

Tela principal do Polvo Negro Live.

<p align="center">
  <img src="Imagem/painel-principal.png" width="100%" alt="Captura real do painel principal do Polvo Negro Live">
</p>

### 2. Configurações

Área destinada às configurações do aplicativo.

<p align="center">
  <img src="Imagem/painel-configuracoes.png" width="100%" alt="Captura real da área de configurações do Polvo Negro Live">
</p>

### 3. Transmissão

Área de gerenciamento das opções e dos destinos de transmissão.

<p align="center">
  <img src="Imagem/painel-transmissao.png" width="100%" alt="Captura real da área de transmissão do Polvo Negro Live">
</p>

### 4. Diagnóstico

Área destinada às informações técnicas, aos registros e ao diagnóstico de possíveis problemas.

<p align="center">
  <img src="Imagem/painel-diagnostico.png" width="100%" alt="Captura real da área de diagnóstico do Polvo Negro Live">
</p>

> As imagens devem representar as telas reais do programa. Os títulos acima descrevem a finalidade pretendida de cada imagem; ajuste-os se o conteúdo visual for diferente.

## 🎯 Objetivos

- Oferecer uma alternativa modular para captura e transmissão ao vivo.
- Permitir a utilização de câmeras e placas de captura USB compatíveis.
- Utilizar o FFmpeg para processamento de áudio e vídeo.
- Organizar transmissões para diferentes destinos compatíveis com RTMP/RTMPS.
- Facilitar a identificação de falhas de conexão e transmissão.
- Buscar um funcionamento eficiente em computadores modestos.
- Manter uma estrutura organizada para manutenção e evolução do sistema.

## ⚙️ Recursos do sistema

Conforme a implementação existente, o projeto pode incluir:

- **Captura de vídeo:** integração com dispositivos compatíveis com DirectShow.
- **Captura de áudio:** utilização de dispositivos de áudio compatíveis.
- **Processamento de mídia:** utilização do FFmpeg.
- **Perfis de transmissão:** organização de formatos horizontais e verticais.
- **Destinos de streaming:** gerenciamento de envios RTMP/RTMPS.
- **Reconexão:** tentativas de recuperação de conexões interrompidas.
- **Diagnóstico:** verificações de conectividade e publicação.
- **Logs:** registros para auxiliar na investigação de erros.
- **Interface gráfica:** painel desenvolvido com Python e Tkinter.
- **Configurações locais:** armazenamento de preferências e parâmetros.

A presença de cada recurso deve ser confirmada no código e na documentação da versão publicada.

## 🧩 Arquitetura conceitual

O fluxo geral do sistema pode ser representado desta forma:

```text
┌────────────────────────────────┐
│ Câmera / Placa de captura USB  │
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

O diagrama é conceitual. A implementação real pode apresentar diferenças conforme a arquitetura e os recursos presentes no código.

## 💻 Requisitos

### Sistema operacional

- Windows 10 ou Windows 11, preferencialmente de 64 bits.
- Drivers compatíveis com os dispositivos de áudio e vídeo.
- Permissões adequadas para acessar câmeras, placas de captura e arquivos.

### Dependências

- Python 3.10 ou superior, quando executado pelo código-fonte.
- FFmpeg de 64 bits, instalado ou configurado conforme a documentação.
- Tcl/Tk para a interface gráfica baseada em Tkinter.
- Pillow, quando necessário para ferramentas específicas de imagens.

A inclusão dessas dependências no executável ou instalador depende do processo de distribuição implementado pelo projeto.

## 🚀 Como executar

Os comandos a seguir pressupõem que os respectivos arquivos existam na raiz do repositório.

### 1. Baixar o projeto

```bash
git clone https://github.com/PolvoNegroLive/PolvoNegroLive-01V.git
cd PolvoNegroLive-01V
```

### 2. Verificar o computador

No Windows, execute o arquivo:

```text
VERIFICAR_PC.bat
```

### 3. Iniciar o aplicativo

Execute:

```text
INICIAR_POLVO_NEGRO_LIVE.bat
```

### 4. Criar o executável

Se o processo de empacotamento estiver configurado, execute:

```text
CRIAR_EXE.bat
```

Se ocorrer algum erro, consulte as mensagens do terminal e a documentação técnica do projeto.

## 📁 Estrutura do projeto

A organização visual definida para o README é:

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

Os diretórios `docs/`, `scripts/`, `tests/` e `tools/` devem ser mantidos conforme a estrutura real do repositório. O exemplo não exige criar pastas que ainda não existam.

### Organização das imagens

A pasta `Imagem/` reúne os recursos visuais usados na apresentação do projeto:

| Arquivo | Finalidade |
|---|---|
| `logo.png` | Logotipo oficial |
| `painel-principal.png` | Tela principal |
| `painel-configuracoes.png` | Tela de configurações |
| `painel-transmissao.png` | Tela de transmissão |
| `painel-diagnostico.png` | Tela de diagnóstico |

Os nomes e os caminhos precisam corresponder exatamente aos arquivos enviados ao GitHub, incluindo letras maiúsculas e minúsculas.

Se o programa utilizar o logotipo por um caminho diferente, preserve a compatibilidade do aplicativo ao organizar os arquivos.

## 🧪 Testes e validação

Se os testes automatizados estiverem configurados, execute:

```bash
python -m unittest discover -s tests -v
```

Caso exista um script próprio de testes, utilize as instruções fornecidas pelo projeto.

Entre os pontos importantes para validação estão:

- Inicialização do programa.
- Carregamento da interface.
- Localização dos recursos visuais.
- Disponibilidade do FFmpeg.
- Detecção dos dispositivos de captura.
- Configuração dos destinos de transmissão.
- Funcionamento dos logs e diagnósticos.
- Persistência e proteção das configurações.
- Geração do executável ou instalador.
- Testes reais de captura e transmissão no Windows.

A aprovação de testes automatizados não garante, por si só, que todos os dispositivos e destinos de streaming funcionarão corretamente.

## 🔐 Segurança e privacidade

Para proteger o usuário e o projeto:

- Não publique chaves de transmissão, senhas ou tokens.
- Não envie arquivos de configuração que contenham credenciais.
- Evite registrar chaves completas nos logs.
- Proteja as configurações locais conforme os mecanismos disponíveis.
- Verifique os arquivos antes de enviar alterações ao repositório.
- Remova dados pessoais e informações sensíveis de capturas de tela.

Consulte `docs/SECURITY.md` se esse arquivo existir no repositório.

## 📚 Documentação complementar

A documentação pode incluir:

- `docs/ARQUITETURA.md` — arquitetura e funcionamento interno.
- `docs/SECURITY.md` — segurança e proteção das configurações.
- `docs/CHANGELOG.md` — histórico de alterações.
- `docs/CONTRIBUTING.md` — orientações para contribuições.

Os arquivos devem ser vinculados aos seus caminhos reais. Não mantenha links para documentos inexistentes.

## 🗺️ Estado atual e limitações

O Polvo Negro Live V08 está em desenvolvimento. O funcionamento pode variar de acordo com o hardware, os drivers, as versões das dependências e as configurações de transmissão.

Os seguintes pontos merecem validação em ambiente Windows real:

- Captura DirectShow.
- Compatibilidade dos dispositivos de áudio e vídeo.
- Proteção de credenciais.
- Geração e execução do executável ou instalador.
- Transmissão real para destinos RTMP/RTMPS.
- Desempenho em computadores com recursos limitados.

A descrição deste README não substitui a verificação do código nem os resultados dos testes.

## 🤝 Contribuições

Contribuições para melhorar a estabilidade, a compatibilidade, o desempenho e a documentação são bem-vindas.

Ao modificar o projeto:

1. Preserve os recursos que já funcionam.
2. Evite dependências desnecessárias.
3. Atualize os caminhos dos recursos quando houver alterações.
4. Atualize a documentação correspondente.
5. Execute os testes disponíveis.
6. Registre as limitações que permanecerem.

## 📄 Licença

A licença deve corresponder à licença efetivamente escolhida pelo responsável pelo projeto. Se ainda não houver uma licença definida, ela deverá ser estabelecida antes de declarar condições específicas de uso, modificação ou redistribuição.

## 👨‍💻 Autor

**Diêgo Botelho Pereira**

**Projeto:** Polvo Negro Live V08

**Repositório:** [PolvoNegroLive-01V](https://github.com/PolvoNegroLive/PolvoNegroLive-01V)

---

<p align="center">
  <strong>🐙 Polvo Negro Live</strong><br>
  <em>Uma proposta modular de captura e transmissão para Windows.</em>
</p>
