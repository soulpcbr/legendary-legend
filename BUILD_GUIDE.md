# Guia de Compilação (Build Guide)

Este guia descreve como transformar o projeto Python em um executável (`.exe`) para Windows usando o **PyInstaller**.

## 1. Preparação do Ambiente

Para gerar um executável otimizado, recomenda-se criar um ambiente virtual limpo e instalar apenas as versões de CPU do PyTorch (biblioteca usada pelo EasyOCR), caso não necessite de aceleração via placa de vídeo dedicada (o que economiza centenas de megabytes).

### Passo 1: Criar ambiente virtual
```powershell
python -m venv build_env
.\build_env\Scripts\activate
```

### Passo 2: Instalar PyTorch (Versão CPU)
Isso garante que o executável não inclua drivers CUDA gigantescos.
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Passo 3: Instalar as outras dependências
```powershell
pip install -r requirements.txt
```
*Nota: O `requirements.txt` já inclui `pyinstaller` e `easyocr`.*

## 2. Gerar o Executável

Execute o seguinte comando na raiz do projeto:

```powershell
pyinstaller --noconfirm --onedir --windowed --name "LiveCaptionArchiver" --hidden-import="easyocr" --collect-all="easyocr" src/main.py
```

### Explicação dos parâmetros:
- `--onedir`: Gera uma pasta contendo o .exe e as dependências (inicia mais rápido que `--onefile`).
- `--windowed`: Não abre a tela preta de console (terminal) ao iniciar.
- `--name "..."`: Nome do executável.
- `--collect-all="easyocr"`: Garante que todos os arquivos internos do EasyOCR sejam copiados.

## 3. Resultado

O executável estará em:
`dist\LiveCaptionArchiver\LiveCaptionArchiver.exe`

Você pode zipar a pasta `LiveCaptionArchiver` dentro de `dist` e enviá-la para o usuário final.

## 4. Funcionamento no PC do Usuário

1. O usuário descompacta a pasta.
2. Abre o `LiveCaptionArchiver.exe`.
3. Na primeira execução, o programa detectará que não possui os modelos de OCR.
4. O usuário clica no botão "Instalar Dependências" na interface.
5. O programa baixa os modelos automaticamente para a pasta de usuário (`~/.EasyOCR`).
6. Após isso, o programa está pronto para uso.
