# Guia de Instalação - LiveCaptionArchiver

Este guia explica como criar o instalador do LiveCaptionArchiver para distribuição.

## Opções de Instalação

### Opção 1: Instalador Automático (Recomendado)

O instalador cria um executável `.exe` que qualquer pessoa pode executar para instalar o aplicativo.

#### Pré-requisitos para Criar o Instalador

1. **Python 3.8+** instalado
2. **PyInstaller** (instalado automaticamente pelo script)
3. **Inno Setup Compiler** (gratuito)
   - Download: https://jrsoftware.org/isdl.php
   - Instale a versão mais recente

#### Como Criar o Instalador

1. Abra o terminal na pasta do projeto
2. Execute:
   ```batch
   build_installer.bat
   ```

3. Aguarde a conclusão. O instalador será criado em:
   - `dist\LiveCaptionArchiver-Setup-v1.0.0.exe`

#### O que o Instalador Faz

- ✅ Instala o aplicativo em `C:\Program Files\LiveCaptionArchiver`
- ✅ Cria atalho no menu Iniciar
- ✅ Cria atalho na área de trabalho (opcional)
- ✅ Instala automaticamente as dependências Python
- ✅ Cria as pastas necessárias (`captions`, `logs`)
- ✅ Configura tudo automaticamente

### Opção 2: Script de Instalação Python

Para usuários que preferem instalação manual ou desenvolvimento:

1. Execute:
   ```batch
   python install.py
   ```

2. O script irá:
   - Criar ambiente virtual Python
   - Instalar todas as dependências
   - Copiar arquivos para `%USERPROFILE%\LiveCaptionArchiver`
   - Criar script de inicialização
   - Tentar criar atalho no menu Iniciar

### Opção 3: Executável Simples (Sem Instalador)

Para testes rápidos ou distribuição simples:

1. Execute:
   ```batch
   build_simple.bat
   ```

2. O executável será criado em:
   - `dist\LiveCaptionArchiver.exe`

**Nota:** Este executável contém tudo embutido, mas não cria atalhos ou instala dependências automaticamente.

## Estrutura de Arquivos

```
legendary-legend/
├── src/                    # Código fonte
├── install.py              # Script de instalação Python
├── installer.iss           # Script Inno Setup
├── build_installer.bat     # Script para criar instalador completo
├── build_simple.bat        # Script para criar apenas executável
└── requirements.txt        # Dependências Python
```

## Distribuição

### Para Distribuir o Instalador

1. Crie o instalador usando `build_installer.bat`
2. Distribua apenas o arquivo:
   - `dist\LiveCaptionArchiver-Setup-v1.0.0.exe`

### Requisitos do Sistema do Usuário Final

- **Windows 10/11** (64-bit)
- **Python 3.8+** (o instalador detecta e avisa se não estiver instalado)
- **Conexão com internet** (para baixar dependências na primeira execução)

## Solução de Problemas

### Erro: "Python não encontrado"

O instalador detecta automaticamente se Python está instalado. Se não estiver:
1. Baixe Python de https://www.python.org/downloads/
2. Instale Python 3.8 ou superior
3. Marque a opção "Add Python to PATH" durante a instalação
4. Execute o instalador novamente

### Erro: "Falha ao instalar dependências"

1. Verifique sua conexão com internet
2. Tente executar manualmente:
   ```batch
   cd "C:\Program Files\LiveCaptionArchiver"
   python -m pip install -r requirements.txt
   ```

### Erro: "Inno Setup não encontrado"

Se você só quer criar o executável (sem instalador):
- Use `build_simple.bat` em vez de `build_installer.bat`

## Atualização da Versão

Para atualizar a versão do aplicativo:

1. Edite `src/__version__.py`:
   ```python
   __version__ = "1.1.0"  # Nova versão
   ```

2. Edite `installer.iss`:
   ```iss
   #define AppVersion "1.1.0"
   ```

3. Recompile o instalador:
   ```batch
   build_installer.bat
   ```

## Notas Técnicas

- O instalador requer privilégios de administrador
- As pastas `captions` e `logs` não são removidas na desinstalação (para preservar dados)
- O instalador detecta automaticamente a versão do Python instalada
- Dependências são instaladas automaticamente na primeira execução
