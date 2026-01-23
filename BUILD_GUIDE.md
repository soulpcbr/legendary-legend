# Guia de Compilação (Build Guide)

Este guia descreve como transformar o projeto Python em um executável (`.exe`) para Windows usando o **PyInstaller**.

## 1. Preparação do Ambiente

Para gerar um executável otimizado, recomenda-se criar um ambiente virtual limpo e instalar apenas as versões de CPU do PyTorch (biblioteca usada pelo EasyOCR), caso não necessite de aceleração via placa de vídeo dedicada (o que economiza centenas de megabytes).

### Passo 1: Criar ambiente virtual

```powershell
python -m venv build_env
.\build_env\Scripts\activate
```

### Passo 2: Instalar dependências

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## 2. Gerar o Executável

Execute o seguinte comando na raiz do projeto (importante usar `--collect-all` para PyQt6 e mss):

```powershell
.\build_env\Scripts\python -m PyInstaller --noconfirm --onedir --windowed --name "LiveCaptionArchiver" --collect-all="PyQt6" --collect-all="mss" --hidden-import="pytesseract" src/main.py
```

### Explicação dos parâmetros:

- `--onedir`: Gera uma pasta contendo o .exe e as dependências (inicia mais rápido que `--onefile`).
- `--windowed`: Não abre a tela preta de console (terminal) ao iniciar.
- `--name "..."`: Nome do executável.
- `--collect-all="PyQt6"`: **CRÍTICO**. Força a inclusão de todos os arquivos do PyQt6. Sem isso, gera erro `ModuleNotFoundError`.
- `--collect-all="mss"`: Garante que a biblioteca de captura de tela esteja completa.

## 3. Resultado

O executável estará em:
`dist\LiveCaptionArchiver\LiveCaptionArchiver.exe`

Você pode zipar a pasta `LiveCaptionArchiver` dentro de `dist` e enviá-la para o usuário final.
