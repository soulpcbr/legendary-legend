# Guia do Instalador LL.exe — LiveCaptionArchiver

## 📋 O Que é o LL.exe?

O `LL.exe` é o instalador auto-suficiente do LiveCaptionArchiver. Ele contém **tudo** que o usuário final precisa para instalar e usar o aplicativo. Não é necessário instalar Python, pip, ou qualquer outra ferramenta.

## 🎯 Funcionalidades do Instalador

### Instalação

- ✅ Wizard moderno e intuitivo (Português BR / Inglês / Português PT)
- ✅ Escolha de pasta de instalação (padrão: `C:\Program Files\LiveCaptionArchiver`)
- ✅ Opção de criar atalho no **Desktop**
- ✅ Opção de criar atalho no **Menu Iniciar**
- ✅ Desinstalador incluído (adicionado ao "Programas e Recursos")
- ✅ Licença MIT exibida durante instalação
- ✅ Compressão LZMA máxima (arquivo menor)

### Atualização / Reparo

- ✅ O instalador detecta automaticamente se o app já está instalado
- ✅ Se já estiver instalado, o instalador entra em modo **Atualização/Reparo**
- ✅ Mantém os dados do usuário (pastas `captions/` e `logs/` não são removidas)
- ✅ Sobrescreve apenas os binários do aplicativo

### Desinstalação

- ✅ Desinstala completamente via "Programas e Recursos" do Windows
- ✅ **Preserva** as pastas `captions/` e `logs/` (dados do usuário)
- ✅ Fecha o app automaticamente antes de desinstalar

## 📦 Como Gerar o Instalador

### Método Rápido

```batch
.agent\scripts\build_installer.bat
```

### O que o script faz

1. Verifica Python no sistema
2. Cria virtualenv limpo para build
3. Instala dependências + PyInstaller
4. Compila o app (PyInstaller `--onedir`)
5. Gera o instalador com Inno Setup
6. Saída: `dist/LL.exe`

## 🖥️ Requisitos do Sistema do Usuário Final

| Requisito           | Detalhes                                                  |
| :------------------ | :-------------------------------------------------------- |
| Sistema Operacional | Windows 10/11 (64-bit)                                    |
| Espaço em Disco     | ~500MB (inclui modelos OCR)                               |
| RAM                 | 4GB mínimo, 8GB recomendado                               |
| Python              | **NÃO NECESSÁRIO**                                        |
| Internet            | Necessária na primeira execução (download de modelos OCR) |

## 🔄 Fluxo de Uso do Instalador

### Nova Instalação

1. Usuário executa `LL.exe`
2. Wizard mostra tela de boas-vindas
3. Exibe licença MIT
4. Permite escolher pasta de destino
5. Permite escolher atalhos (Desktop / Menu Iniciar)
6. Instala
7. Opcionalmente abre o app após instalação

### Atualização

1. Usuário executa `LL.exe` (nova versão)
2. Wizard detecta instalação existente
3. Mostra mensagem de "Atualização/Reparo"
4. Usa a mesma pasta da instalação anterior
5. Atualiza apenas os binários
6. Preserva captions e logs

### Desinstalação

1. Painel de Controle → Programas e Recursos → LiveCaptionArchiver → Desinstalar
2. Ou: Menu Iniciar → LiveCaptionArchiver → Desinstalar
3. Remove binários mas preserva dados do usuário

## 📁 Estrutura Após Instalação

```
C:\Program Files\LiveCaptionArchiver\
├── LiveCaptionArchiver.exe    # Executável principal
├── _internal/                 # Binários Python + libs
├── src/                       # Código fonte empacotado
├── captions/                  # Legendas salvas (preservado)
├── logs/                      # Logs de uso (preservado)
├── README.md                  # Documentação
└── LICENSE                    # Licença MIT
```

## 🛠️ Estrutura dos Scripts de Build

```
.agent/scripts/
├── build_installer.bat        # Script principal (EXECUTE ESTE)
├── installer.iss              # Script Inno Setup (instalador)
├── build_installer_legacy.bat # Legado (referência)
├── build_simple_legacy.bat    # Legado (referência)
├── installer_legacy.iss       # Legado (referência)
└── install_legacy.py          # Legado (referência)
```

## 🐛 Solução de Problemas

### "Windows protegeu seu PC" (SmartScreen)

- O .exe não é assinado digitalmente. Clique em "Mais informações" → "Executar assim mesmo"
- Para evitar isso, assine o .exe com um certificado de código

### Instalador não encontra versão anterior

- Verificar se o AppId `{E7A3B5C1-4D2F-48A0-9E67-1C3D5F8B2A94}` está correto
- Verificar registro: `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\`

### App não abre após instalação

- Verifique os logs em `{pasta_de_instalacao}\logs\`
- Execute pelo terminal para ver mensagens de erro
