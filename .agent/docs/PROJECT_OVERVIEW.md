# LiveCaptionArchiver — Visão Geral e Organização do Projeto

> **Documento canônico.** Esta é a referência definitiva sobre a estrutura, organização e arquitetura do projeto. Última atualização: 2026-02-20.

---

## 📋 Descrição

O **LiveCaptionArchiver** é um aplicativo Desktop para Windows que captura, estabiliza e arquiva legendas em tempo real. Ele utiliza **EasyOCR** (com suporte a GPU/CPU e instalação automática de modelos) e algoritmos de estabilização de texto proprietários.

## 🎯 Problema que Resolve

O Windows Live Captions (e outras fontes de legendas ao vivo) reescreve as frases enquanto são faladas:

- Frame 1: `"Olá"`
- Frame 2: `"Olá, tudo"`
- Frame 3: `"Olá, tudo bem?"`

O app **NÃO** grava cada variação. Ele espera a frase se estabilizar e salva apenas a versão final e consolidada.

---

## 🔧 Stack Tecnológica

| Componente | Tecnologia    | Propósito                                   |
| :--------- | :------------ | :------------------------------------------ |
| Linguagem  | Python 3.10+  | Core da aplicação                           |
| GUI        | PyQt6         | Interface gráfica MVC                       |
| OCR        | EasyOCR       | Reconhecimento de texto (sem deps externas) |
| Captura    | mss           | Screenshot ultrarrápido                     |
| Imagem     | opencv-python | Pré-processamento (binarização/inversão)    |
| Lógica     | difflib       | Comparação de similaridade de strings       |
| Dados      | numpy         | Manipulação de arrays de imagem             |

---

## 🏗️ Arquitetura (MVC Estrito)

```
src/
├── main.py                # Entry point + Controller principal (LiveCaptionApp)
├── __init__.py
├── __version__.py          # Versão centralizada (ex: "1.0.0")
│
├── core/                   # MODEL — Lógica de Negócios
│   ├── __init__.py
│   ├── stabilizer.py       # CaptionStabilizer — cérebro do app, buffer + dedup
│   ├── file_manager.py     # FileManager — gravação de .txt com flush imediato
│   ├── settings_manager.py # SettingsManager — persistência de configs (JSON)
│   └── usage_logger.py     # UsageLogger — log detalhado de uso
│
├── ui/                     # VIEW — Interface Gráfica (PyQt6)
│   ├── __init__.py
│   ├── main_window.py      # MainControlWindow — janela principal com controles
│   └── overlay.py          # OverlaySelector — seleção de região da tela
│
├── workers/                # CONTROLLER — Threads de Trabalho
│   ├── __init__.py
│   └── ocr_worker.py       # OCRWorker — captura de tela + OCR em QThread
│
└── utils/                  # UTILITÁRIOS
    ├── __init__.py
    └── image_processing.py # Pré-processamento de imagem para OCR
```

### Fluxo de Dados

```
┌─────────────┐    captura     ┌───────────┐    texto bruto    ┌──────────────────┐
│   mss       │ ─────────────► │ OCRWorker │ ────────────────► │ CaptionStabilizer│
│ (screenshot)│                │ (QThread) │    sinal Qt       │ (buffer + dedup) │
└─────────────┘                └───────────┘                   └────────┬─────────┘
                                                                       │
                                                               frase estável
                                                                       │
                                                                       ▼
                                ┌───────────┐                  ┌──────────────────┐
                                │    GUI    │ ◄──── atualiza ── │   FileManager    │
                                │ (MainWin) │    log em tempo   │  (.txt + flush)  │
                                └───────────┘      real         └──────────────────┘
```

---

## 📁 Organização Completa de Pastas

```
legendary-legend/                    # Raiz do repositório
│
├── src/                             # 🟢 CÓDIGO FONTE
│   ├── main.py                      #    Entry point + Controller principal
│   ├── __init__.py
│   ├── __version__.py               #    Versão centralizada
│   ├── core/                        #    Lógica de negócios (Model)
│   ├── ui/                          #    Interface gráfica (View)
│   ├── workers/                     #    Threads de trabalho (Controller)
│   └── utils/                       #    Funções utilitárias
│
├── tests/                           # 🧪 TESTES
│   ├── test_stabilizer.py           #    Testes do CaptionStabilizer
│   └── test_stabilizer_extended.py  #    Testes estendidos
│
├── .agent/                          # 🤖 CENTRAL DE CONFIGURAÇÃO E DOCUMENTAÇÃO
│   ├── config/                      #    Configurações do agente AI
│   │   ├── config.json              #    Modo, permissões, automação
│   │   └── PLESS_ENTER_*.md         #    Instruções de modo autônomo
│   │
│   ├── docs/                        #    📚 Documentação completa
│   │   ├── PROJECT_OVERVIEW.md      #    ★ Este arquivo — visão geral e organização
│   │   ├── BUILD_GUIDE.md           #    Como compilar o projeto
│   │   ├── INSTALLER_GUIDE.md       #    Como funciona o instalador LL.exe
│   │   ├── MANUAL_DE_USO.md         #    Manual para o usuário final
│   │   ├── MIGRATION_CHANGELOG.md   #    Histórico da reorganização
│   │   ├── initial_prompt.md        #    Prompt original de criação do projeto
│   │   └── *_legacy.md              #    Versões anteriores (referência)
│   │
│   ├── instructions/                #    📋 Instruções para agentes AI
│   │   └── copilot-instructions.md  #    Regras, stack, arquitetura, checklist
│   │
│   ├── scripts/                     #    ⚙️ Scripts de build e instalação
│   │   ├── build_installer.bat      #    ★ Script principal de build
│   │   ├── installer.iss            #    ★ Script Inno Setup do instalador
│   │   └── *_legacy.*               #    Versões anteriores (referência)
│   │
│   ├── skills/                      #    🧠 Biblioteca de Skills AI
│   │   ├── skills/                  #    228 skills organizadas por tema
│   │   ├── docs/                    #    Documentação das skills
│   │   ├── scripts/                 #    Scripts de gerenciamento
│   │   └── skills_index.json        #    Índice de todas as skills
│   │
│   ├── temp/                        #    🗑️ Arquivos temporários (gitignored)
│   │   └── .gitkeep
│   │
│   └── workflows/                   #    🔄 Workflows automatizados
│       └── .gitkeep
│
├── .github/                         # 🔗 Compatibilidade com tooling
│   └── copilot-instructions.md      #    Cópia espelho de .agent/instructions/
│
├── captions/                        # 💬 Dados do usuário — legendas capturadas
├── logs/                            # 📝 Logs de execução
│
├── dist/                            # 📦 Builds compilados (gitignored)
│   ├── LiveCaptionArchiver/         #    App compilado (PyInstaller --onedir)
│   └── LL.exe                       #    Instalador final
│
├── build/                           # 🔨 Artefatos de build (gitignored)
├── build_env/                       # 🐍 Virtualenv de build (gitignored)
│
├── .gitignore                       # Regras de ignore para Git
├── LICENSE                          # Licença MIT
├── README.md                        # README principal do repositório
├── requirements.txt                 # Dependências Python
└── user_settings.json               # Configurações salvas do usuário
```

---

## 📂 Detalhamento de Cada Pasta

### `src/` — Código Fonte

O coração do aplicativo. Organizado em MVC estrito:

| Subpasta   | Camada     | Responsabilidade                          |
| :--------- | :--------- | :---------------------------------------- |
| `core/`    | Model      | Lógica de negócios, dados, persistência   |
| `ui/`      | View       | Interface gráfica PyQt6                   |
| `workers/` | Controller | Threads de OCR, orquestração              |
| `utils/`   | Utilitário | Funções de suporte (processamento imagem) |

**Regras:**

- `core/` **nunca** importa de `ui/` ou `workers/`
- `ui/` **nunca** faz I/O de arquivo diretamente
- `workers/` comunica com `ui/` apenas via **sinais Qt**
- OCR **sempre** roda em `QThread` (nunca na thread principal)

### `tests/` — Testes

Testes unitários focados no `CaptionStabilizer`, o componente mais crítico:

| Arquivo                       | Cobertura                              |
| :---------------------------- | :------------------------------------- |
| `test_stabilizer.py`          | Deduplicação, buffer, commit, silêncio |
| `test_stabilizer_extended.py` | Casos edge e stress                    |

```bash
python -m unittest tests/test_stabilizer.py
python -m unittest tests/test_stabilizer_extended.py
```

### `.agent/` — Central de Configuração e Documentação

Ponto único para tudo que não é código-fonte do app. Está dividido em:

| Subpasta        | Conteúdo                                       |
| :-------------- | :--------------------------------------------- |
| `config/`       | Configuração do agente AI (modo, permissões)   |
| `docs/`         | Toda a documentação do projeto                 |
| `instructions/` | Instruções e contexto para agentes AI          |
| `scripts/`      | Scripts de build e instalação (.bat, .iss)     |
| `skills/`       | Biblioteca de skills AI (228 skills temáticas) |
| `temp/`         | Temporários do agente (gitignored)             |
| `workflows/`    | Workflows de automação                         |

### `.github/` — Compatibilidade

Mantida **apenas** para compatibilidade com tooling que espera encontrar `copilot-instructions.md` neste local. O arquivo é uma cópia espelho de `.agent/instructions/copilot-instructions.md`.

> **Regra:** Ao editar instruções, edite em `.agent/instructions/` e copie para `.github/`.

### `captions/` e `logs/` — Dados Runtime

- `captions/`: Arquivos `.txt` gerados pelo app (formato: `captions_YYYY-MM-DD_HH-MM.txt`)
- `logs/`: Logs de uso detalhados
- **Ambas são preservadas** na desinstalação pelo instalador LL.exe

### `dist/` e `build/` — Artefatos de Compilação

Gerados automaticamente e incluídos no `.gitignore`:

- `dist/LiveCaptionArchiver/`: Output do PyInstaller (--onedir)
- `dist/LL.exe`: Instalador final gerado pelo Inno Setup
- `build/`: Artefatos intermediários do PyInstaller

---

## ⚙️ Configurações do Usuário

Armazenadas em `user_settings.json` na raiz:

| Chave                           | Tipo    | Descrição                                      |
| :------------------------------ | :------ | :--------------------------------------------- |
| `capture_region`                | Object  | Coordenadas x, y, width, height                |
| `timeout_ms`                    | Number  | Tempo de silêncio para finalizar frase (ms)    |
| `auto_timeout`                  | Boolean | Auto-ajuste baseado na velocidade da fala      |
| `invert_colors`                 | Boolean | Inverter cores para melhor OCR em fundo escuro |
| `similarity_threshold`          | Float   | Limiar de similaridade (0.0 a 1.0)             |
| `min_update_interval`           | Number  | Intervalo mínimo entre updates (ms)            |
| `auto_recalc_interval`          | Number  | Intervalo de recálculo automático (s)          |
| `auto_smart_adjust`             | Boolean | Ajuste inteligente de parâmetros               |
| `jitter_detection_threshold`    | Number  | Limiar para detecção de jitter                 |
| `stability_detection_threshold` | Number  | Limiar para detecção de estabilidade           |
| `repetition_threshold`          | Float   | Limiar para detecção de repetição              |

---

## 🚀 Fluxo de Execução do App

1. `main.py` → Cria `LiveCaptionApp` (controller)
2. Inicializa: `SettingsManager` → `UsageLogger` → `CaptionStabilizer` → `FileManager`
3. Cria a GUI: `MainControlWindow` + `OverlaySelector`
4. Carrega configurações salvas do `user_settings.json`
5. Usuário seleciona a região da tela onde as legendas aparecem
6. Usuário clica "Iniciar Gravação"
7. `OCRWorker` (QThread separada) captura a região a cada ~100ms
8. Pré-processamento: grayscale → threshold → inversão (se configurado)
9. Texto detectado → `CaptionStabilizer.process_new_text()`
10. Se a frase estabilizou → `FileManager.append_text()` com timestamp
11. UI atualizada com log em tempo real
12. Configurações auto-ajustadas se `auto_smart_adjust` estiver ativo

---

## 📦 Build e Distribuição

### Comando Único

```batch
.agent\scripts\build_installer.bat
```

### Pipeline

```
Código Fonte (src/)
        │
        ▼
  PyInstaller (--onedir)        ← Empacota Python + todas as libs
        │
        ▼
  dist/LiveCaptionArchiver/     ← Pasta com .exe + DLLs
        │
        ▼
  Inno Setup (ISCC)             ← Cria wizard de instalação
        │
        ▼
  dist/LL.exe                   ← INSTALADOR FINAL (auto-suficiente)
```

### Saída

| Arquivo                     | Descrição                        |
| :-------------------------- | :------------------------------- |
| `dist/LiveCaptionArchiver/` | App compilado (roda diretamente) |
| `dist/LL.exe`               | Instalador para distribuição     |

Para mais detalhes, consulte:

- [BUILD_GUIDE.md](BUILD_GUIDE.md) — Pipeline detalhado e troubleshooting
- [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md) — Funcionalidades do instalador

---

## 📚 Índice da Documentação

| Documento                     | Localização                                   | Propósito                                  |
| :---------------------------- | :-------------------------------------------- | :----------------------------------------- |
| **Visão Geral e Organização** | `.agent/docs/PROJECT_OVERVIEW.md`             | ★ Este doc — referência canônica           |
| **Guia de Build**             | `.agent/docs/BUILD_GUIDE.md`                  | Como compilar e gerar LL.exe               |
| **Guia do Instalador**        | `.agent/docs/INSTALLER_GUIDE.md`              | Funcionalidades e uso do instalador        |
| **Manual de Uso**             | `.agent/docs/MANUAL_DE_USO.md`                | Guia para o usuário final                  |
| **Changelog de Migração**     | `.agent/docs/MIGRATION_CHANGELOG.md`          | Histórico da reorganização (2026-02-20)    |
| **Prompt Original**           | `.agent/docs/initial_prompt.md`               | Requisitos originais de criação do projeto |
| **Instruções AI**             | `.agent/instructions/copilot-instructions.md` | Contexto para agentes de código            |
| **README**                    | `README.md` (raiz)                            | Visão pública do repositório               |

---

## 🧪 Comandos Úteis

| Ação                  | Comando                                        |
| :-------------------- | :--------------------------------------------- |
| Rodar o app           | `python src/main.py`                           |
| Rodar testes          | `python -m unittest tests/test_stabilizer.py`  |
| Instalar dependências | `pip install -r requirements.txt`              |
| Gerar instalador      | `.agent\scripts\build_installer.bat`           |
| Criar venv de dev     | `python -m venv venv && venv\Scripts\activate` |
