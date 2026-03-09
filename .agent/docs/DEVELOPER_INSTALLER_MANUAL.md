# Manual do Desenvolvedor: Gerando o Instalador do LiveCaptionArchiver

Este guia foi criado para o mantenedor e desenvolvedores do projeto entenderem e realizarem a criação de pacotes de instalação completos (`LL.exe`).

## 1. Como o Instalador Funciona?

O instalador é gerado graças a uma junção de **dois processos sequenciais**:

1. **PyInstaller**: Cuida de todo o mundo do Python, transformando os módulos (PyQt6, OpenCV, MSS) num simples binário (usando `--onedir`). Ele dispensa o usuário de ter que instalar o Python na máquina.
2. **Inno Setup (ISCC)**: Pega a pasta binária compilada (`\dist\LiveCaptionArchiver`), adiciona os avisos de licença, cria os atalhos do Windows (Área de Trabalho, Menu Iniciar) e compacta de forma agressiva tudo num arquivo único, o `LL.exe`.

> **Nota sobre Dependências de Execução**: A engine principal de inferência, o modelo do **EasyOCR**, não é baixada durante a instalação para economizar espaço do arquivo de setup. Nós delegamos a tarefa para que o próprio aplicativo faça o download na primeira vez que for executado via interface gráfica (_OCRWorker.install_dependencies_).

## 2. A Mágica num Só Comando

Você não precisa gerenciar os processos isoladamente. Criou-se o arquivo `.agent\scripts\build_installer.bat`.
Quando você o executa, ele varre as fases abaixo magicamente:

1. Detecta o caminho real do projeto.
2. Cria ou usa o ambiente virtual (`build_env`) na sua raiz.
3. Instala os módulos base a partir do `requirements.txt` (garantindo as depedências antes de compilar). Se falhar a instalação generalizada, aciona um _fallback_ pip automático que garante o OpenCV, MSS, EasyOCR e PyQt6.
4. Gera a construção do PyInstaller varrendo todas as referências `--hidden-import` (evitando falha do OCR não ser encontrado).
5. Chama o Compiler do Inno Setup em `Program Files` contra o arquivo `.agent\scripts\installer.iss` e, ao cruzar, extrai o pacote `dist\LL.exe`.

### Comando de Execução Rápida do Build:

Use o Powershell ou CMD:

```bat
.agent\scripts\build_installer.bat
```

## 3. Preparando seu Ambiente para Gerar o Instalador

Para criar o instalador na sua máquina dev, você só precisa de:

- Python **3.8+** adicionado ao PATH.
- Inno Setup **V6** (Baixado do site da [JrSoftware](https://jrsoftware.org/isdl.php)) - Instalado em `C:\Program Files (x86)\Inno Setup 6\`.

## 4. Analisando as Atualizações e Migração de Rotas

Se um usuário já tiver o aplicativo e for instalar novamente as pastas do `%APPDATA%/LiveCaptionArchiver/` (que contêm as capturas e os logs de sessões via modulo `src.utils.paths.py`) **não serão apagados**, permitindo a conservação dos históricos, repetições de sessão, e textos salvos, além das configurações (`user_settings.json`).

Se precisar fazer o upgrade de versão, apenas mude em `__version__.py`. O InnoSetup faz a leitura da Versão Executável ao rodar.

## 5. Boas Práticas ao Contribuir e Modificar o App

Na hora que for codar, certifique-se de manter os preceitos de **prevenção de travamentos** que aplicamos. O Worker de OCR roda independente (`QThread`), com limitação inteligente baseada em delta `time.time()`. Em nossos testes na suite `test_stabilizer`, verificamos os recortes sem vazamentos de memória da conversão Array NumPy (Tesseract/OCR).

- A lógica `CaptionStabilizer` protege re-escrição imediata, gerando o commit em arquivo apenas quando um silêncio contusivo acontece.
- Se for criar uma dependência nova em `requirements.txt`, coloque ela também nos logs de hidden imports nas diretrizes listadas no bat `build_installer.bat`, para não faltar `.pyd/DLL` na arquitetura Windows.

Fim das diretrizes de empacotamento. Trabalhe com segurança.
