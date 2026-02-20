# Changelog da Reorganização — 2026-02-20

## 📋 Resumo

Reorganização completa da estrutura do projeto, centralização de toda a documentação e configuração em `.agent/`, e criação de um novo sistema de build profissional para gerar o instalador `LL.exe`.

---

## 🗂️ Migração de Pastas

### Movido para `.agent/`

| Origem                                        | Destino                                        | Tipo                       |
| :-------------------------------------------- | :--------------------------------------------- | :------------------------- |
| `agent/MANUAL_DE_USO.md`                      | `.agent/docs/MANUAL_DE_USO.md`                 | Documentação               |
| `agent/initial_prompt.md`                     | `.agent/docs/initial_prompt.md`                | Documentação               |
| `.github/copilot-instructions.md`             | `.agent/instructions/copilot-instructions.md`  | Instruções AI (atualizado) |
| `.antigravity/config.json`                    | `.agent/config/config.json`                    | Configuração               |
| `.antigravity/PLESS_ENTER_AUTONOMOUS_MODE.md` | `.agent/config/PLESS_ENTER_AUTONOMOUS_MODE.md` | Configuração               |
| `.skills/` (inteiro)                          | `.agent/skills/`                               | Skills AI                  |
| `build_installer.bat`                         | `.agent/scripts/build_installer_legacy.bat`    | Legado                     |
| `build_simple.bat`                            | `.agent/scripts/build_simple_legacy.bat`       | Legado                     |
| `installer.iss`                               | `.agent/scripts/installer_legacy.iss`          | Legado                     |
| `install.py`                                  | `.agent/scripts/install_legacy.py`             | Legado                     |
| `BUILD_GUIDE.md`                              | `.agent/docs/BUILD_GUIDE_legacy.md`            | Legado                     |
| `README_INSTALLER.md`                         | `.agent/docs/README_INSTALLER_legacy.md`       | Legado                     |

### Pastas Removidas

| Pasta           | Motivo                              |
| :-------------- | :---------------------------------- |
| `agent/`        | Migrado para `.agent/docs/`         |
| `.github/`      | Migrado para `.agent/instructions/` |
| `.skills/`      | Migrado para `.agent/skills/`       |
| `.antigravity/` | Migrado para `.agent/config/`       |

### Arquivos Removidos da Raiz

| Arquivo                             | Motivo                                               |
| :---------------------------------- | :--------------------------------------------------- |
| `build_installer.bat`               | Substituído por `.agent/scripts/build_installer.bat` |
| `build_simple.bat`                  | Obsoleto (coberto pelo novo script)                  |
| `install.py`                        | Obsoleto (instalador agora é LL.exe via Inno Setup)  |
| `installer.iss`                     | Substituído por `.agent/scripts/installer.iss`       |
| `install_dependencies_template.bat` | Obsoleto (app não precisa de Python no destino)      |
| `LiveCaptionArchiver.spec`          | Gerado automaticamente pelo PyInstaller              |
| `LiveCaptionArchiver_v2.spec`       | Gerado automaticamente pelo PyInstaller              |
| `BUILD_GUIDE.md`                    | Movido para `.agent/docs/`                           |
| `README_INSTALLER.md`               | Fundido em `.agent/docs/INSTALLER_GUIDE.md`          |

---

## 🆕 Novos Arquivos Criados

| Arquivo                              | Propósito                                                              |
| :----------------------------------- | :--------------------------------------------------------------------- |
| `.agent/scripts/build_installer.bat` | **NOVO** — Script principal de build (venv + PyInstaller + Inno Setup) |
| `.agent/scripts/installer.iss`       | **NOVO** — Script Inno Setup profissional                              |
| `.agent/docs/PROJECT_OVERVIEW.md`    | Visão geral completa do projeto                                        |
| `.agent/docs/BUILD_GUIDE.md`         | Guia de build atualizado                                               |
| `.agent/docs/INSTALLER_GUIDE.md`     | Guia do instalador LL.exe                                              |
| `.agent/docs/MIGRATION_CHANGELOG.md` | Este arquivo                                                           |
| `.agent/temp/.gitkeep`               | Placeholder para pasta temporária                                      |
| `.agent/workflows/.gitkeep`          | Placeholder para workflows                                             |

---

## 🔄 Arquivos Atualizados

| Arquivo                                       | Mudanças                                                         |
| :-------------------------------------------- | :--------------------------------------------------------------- |
| `README.md`                                   | Atualizado com info do instalador e links para nova documentação |
| `.gitignore`                                  | Atualizado para incluir nova estrutura `.agent/temp/`            |
| `.agent/instructions/copilot-instructions.md` | Atualizado com arquitetura atual e referências corretas          |

---

## 📦 Novo Sistema de Build

### Antes (Legado)

- `build_installer.bat` na raiz → usava PyInstaller --onefile + Inno Setup
- Dependia de Python no sistema do usuário final
- Instalador gerava `LiveCaptionArchiver-Setup-v1.0.0.exe`
- Precisava instalar dependências Python no destino

### Agora (Novo)

- `.agent/scripts/build_installer.bat` → PyInstaller --onedir + Inno Setup melhorado
- **NÃO** depende de Python no sistema do usuário final
- Instalador gera `LL.exe` (nome curto e intuitivo)
- Auto-suficiente: tudo empacotado pela PyInstaller
- Suporta instalar / reparar / atualizar
- Wizard modernizado com Português BR
- Permissões flexíveis (admin ou usuário)
- Compressão LZMA ultra64

---

## 📁 Estrutura Final

```
legendary-legend/
├── .agent/                          # Central de configuração
│   ├── config/                      # Configs do agente AI
│   │   ├── config.json
│   │   └── PLESS_ENTER_AUTONOMOUS_MODE.md
│   ├── docs/                        # Documentação completa
│   │   ├── BUILD_GUIDE.md           # Guia de build (novo)
│   │   ├── INSTALLER_GUIDE.md       # Guia do instalador (novo)
│   │   ├── MANUAL_DE_USO.md         # Manual do usuário
│   │   ├── PROJECT_OVERVIEW.md      # Visão geral (novo)
│   │   ├── MIGRATION_CHANGELOG.md   # Este arquivo (novo)
│   │   ├── initial_prompt.md        # Prompt original
│   │   ├── *_legacy.md              # Versões legadas (referência)
│   ├── instructions/                # Instruções AI
│   │   └── copilot-instructions.md  # Instruções atualizadas
│   ├── scripts/                     # Scripts de build
│   │   ├── build_installer.bat      # Build principal (NOVO)
│   │   ├── installer.iss            # Inno Setup (NOVO)
│   │   └── *_legacy.*               # Versões legadas (referência)
│   ├── skills/                      # Biblioteca de skills AI
│   ├── temp/                        # Temporários (gitignored)
│   └── workflows/                   # Automações
├── src/                             # Código fonte
├── tests/                           # Testes
├── dist/                            # Builds (gitignored)
├── build/                           # Artefatos (gitignored)
├── captions/                        # Dados do usuário
├── logs/                            # Logs
├── requirements.txt
├── LICENSE
├── README.md
├── user_settings.json
└── .gitignore
```
