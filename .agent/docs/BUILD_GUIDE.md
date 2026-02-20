# Guia de Build — LiveCaptionArchiver

## 📋 Visão Geral

O LiveCaptionArchiver pode ser distribuído como um **instalador auto-suficiente** (`LL.exe`). O usuário final **NÃO precisa instalar Python** nem nenhuma outra dependência.

## 🏗️ Pipeline de Build

```
Código Fonte (Python)
        │
        ▼
  PyInstaller (--onedir)
  Empacota Python + libs
        │
        ▼
  dist/LiveCaptionArchiver/
  (pasta com .exe + DLLs)
        │
        ▼
  Inno Setup (ISCC)
  Cria instalador wizard
        │
        ▼
  dist/LL.exe
  (Instalador final)
```

## ⚡ Build Rápido (1 Comando)

```batch
.agent\scripts\build_installer.bat
```

Isso faz **tudo automaticamente**:

1. Cria/usa venv de build
2. Instala dependências + PyInstaller
3. Compila o app
4. Gera o instalador `dist/LL.exe`

## 📋 Pré-requisitos para Build

### Obrigatórios

- **Python 3.8+** instalado e no PATH
- **Inno Setup 6** instalado ([download](https://jrsoftware.org/isdl.php))

### Recomendados

- Conexão com internet (para baixar dependências na primeira vez)
- ~2GB de espaço livre (para venv + build artifacts)

## 🔧 Build Manual (Passo a Passo)

### Passo 1: Ambiente Virtual

```powershell
python -m venv build_env
.\build_env\Scripts\activate
```

### Passo 2: Dependências

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

### Passo 3: Compilar com PyInstaller

```powershell
python -m PyInstaller `
    --name=LiveCaptionArchiver `
    --onedir `
    --windowed `
    --noconfirm `
    --clean `
    --add-data "src;src" `
    --hidden-import=PyQt6 `
    --hidden-import=easyocr `
    --hidden-import=mss `
    --hidden-import=cv2 `
    --hidden-import=numpy `
    --collect-all=easyocr `
    --collect-all=PyQt6 `
    --collect-all=mss `
    src\main.py
```

#### Parâmetros Importantes

| Parâmetro         | Propósito                                           |
| :---------------- | :-------------------------------------------------- |
| `--onedir`        | Pasta com .exe + DLLs (mais rápido que `--onefile`) |
| `--windowed`      | Sem console preto ao abrir                          |
| `--collect-all`   | Inclui todos os assets das bibliotecas              |
| `--hidden-import` | Importações dinâmicas que o PyInstaller não detecta |

### Passo 4: Gerar Instalador

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .agent\scripts\installer.iss
```

### Resultado

```
dist/
├── LiveCaptionArchiver/          # App compilado (pasta)
│   ├── LiveCaptionArchiver.exe   # Executável principal
│   └── _internal/                # Binários e libs
└── LL.exe                        # INSTALADOR FINAL
```

## 🔄 Atualizar Versão

1. Edite `src/__version__.py`:

```python
__version__ = "1.1.0"  # Nova versão
```

2. Recompile:

```batch
.agent\scripts\build_installer.bat
```

O Inno Setup lê a versão automaticamente do executável compilado.

## 🐛 Troubleshooting

### PyInstaller falha com "ModuleNotFoundError"

- Adicione `--hidden-import=MODULO` ao comando
- Ou `--collect-all=PACOTE` para pacotes com muitos sub-módulos

### Inno Setup não encontrado

- Instale de: https://jrsoftware.org/isdl.php
- Verifique se está em `C:\Program Files (x86)\Inno Setup 6\`

### Build muito grande (~500MB+)

- EasyOCR + PyTorch são grandes. Para reduzir:
  - Use `--exclude-module torch.cuda` se não precisar de GPU
  - Use venv limpo para evitar incluir pacotes desnecessários

### Executável não abre

- Rode pelo terminal para ver erros: `dist\LiveCaptionArchiver\LiveCaptionArchiver.exe`
- Verifique se `src/` foi incluído como data
