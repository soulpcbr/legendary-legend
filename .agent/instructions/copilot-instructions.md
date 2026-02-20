# Instruções para Agentes AI — LiveCaptionArchiver (Legendary Legend)

**Objetivo:** Contexto inequívoco para o desenvolvimento do **LiveCaptionArchiver**, um aplicativo Desktop para Windows que arquiva legendas em tempo real com correção inteligente.

## ✅ Checklist Rápido (Executar antes de qualquer ação)

- [ ] **Ambiente:** O `venv` está ativo? As dependências (`requirements.txt`) estão instaladas?
- [ ] **EasyOCR:** O módulo está acessível? Modelos serão baixados automaticamente.
- [ ] **Threading:** O OCR está rodando em uma `QThread` separada? **NUNCA** bloquear a GUI.
- [ ] **MVC:** O código respeita a separação Model-View-Controller?
- [ ] **Testes:** Rodei `test_stabilizer.py` para garantir que a lógica de dedup não quebrou?

---

## 1) Stack e Tecnologias

| Componente    | Tecnologia      | Obs                                       |
| :------------ | :-------------- | :---------------------------------------- |
| **Linguagem** | Python 3.10+    | Tipagem estrita recomendada (`typing`).   |
| **GUI**       | PyQt6           | Padrão MVC.                               |
| **OCR**       | EasyOCR         | Sem dependência externa de binários.      |
| **Captura**   | `mss`           | Ultra fast cross-platform screenshot.     |
| **Img Proc**  | `opencv-python` | Pré-processamento (binarização/inversão). |
| **Lógica**    | `difflib`       | Comparação de similaridade de strings.    |

---

## 2) Arquitetura (MVC Estrito)

### 2.1 Model (Lógica de Negócios)

- **Classe:** `CaptionStabilizer` (Cérebro do app).
- **Responsabilidade:** Receber texto bruto, estabilizar frases, e decidir quando salvar no disco.
- **Classe:** `FileManager` (IO).
- **Responsabilidade:** Gerenciar arquivo `.txt` com flush imediato.
- **Classe:** `SettingsManager` (Configurações).
- **Responsabilidade:** Persistir e carregar configurações do usuário.
- **Classe:** `UsageLogger` (Logs detalhados).

### 2.2 View (Interface Gráfica)

- **Janela Principal (`MainControlWindow`):** Controles (Start/Stop), Logs, Status, Configurações.
- **Overlay (`OverlaySelector`):** Janela transparente/redimensionável ("Always on Top") para definir a região de captura (ROI).

### 2.3 Controller (Orquestração)

- **Controller (`LiveCaptionApp`):** Classe principal em `main.py` que orquestra tudo.
- **Worker (`OCRWorker`):** Thread dedicada que usa `mss` para capturar a tela e EasyOCR para extrair texto.
- **Fluxo:** `OCRWorker` -> Sinal `text_detected` -> `Controller` -> `CaptionStabilizer` -> `Update View`.

---

## 3) Regras de Negócio Críticas

### 3.1 Estabilização de Legenda

O Live Captions do Windows reescreve a frase enquanto ela é falada.

- **NÃO GRAVAR** linha por linha imediatamente.
- **BUFFER:** Manter um buffer da frase atual.
- **LÓGICA:** Se o novo texto tem > 60% de similaridade com o buffer, atualize o buffer. Se for diferente, commita o buffer anterior e inicia um novo.

### 3.2 Performance e Threading

- O OCR é pesado. Deve rodar em `QThread` ou `QRunnable`.
- A captura de tela deve ser feita com `mss` (mais rápido que pyautogui).
- Pré-processamento de imagem: Converter para escala de cinza e aplicar thresholding é **obrigatório** para precisão em legendas brancas/fundo preto.

### 3.3 Tratamento de Erros

- Verificar se EasyOCR está operacional na inicialização.
- Se não estiver, exibir popup amigável e não crashar.
- Salvar arquivos com encoding `utf-8`.

---

## 4) Organização de Arquivos

```
/
├── src/
│   ├── main.py             # Entry point + Controller
│   ├── __version__.py      # Versão centralizada
│   ├── core/
│   │   ├── stabilizer.py   # Lógica de buffer
│   │   ├── file_manager.py # I/O de arquivos
│   │   ├── settings_manager.py
│   │   └── usage_logger.py
│   ├── ui/
│   │   ├── main_window.py  # Janela principal
│   │   └── overlay.py      # Seleção de região
│   ├── workers/
│   │   └── ocr_worker.py   # Thread de captura/OCR
│   └── utils/
│       └── image_processing.py
├── tests/
│   ├── test_stabilizer.py
│   └── test_stabilizer_extended.py
├── .agent/                  # Central de configuração AI
│   ├── config/              # Configs do agente
│   ├── docs/                # Documentação completa
│   ├── instructions/        # Este arquivo
│   ├── scripts/             # Scripts de build e instalação
│   ├── skills/              # Biblioteca de skills
│   ├── temp/                # Temporários
│   └── workflows/           # Automações
└── requirements.txt
```

---

## 5) Build e Distribuição

- **Gerar Instalador:** `.agent\scripts\build_installer.bat`
- **Saída:** `dist\LL.exe` (instalador auto-suficiente)
- **Docs:** Ver `.agent\docs\BUILD_GUIDE.md` e `.agent\docs\INSTALLER_GUIDE.md`

---

## 6) Comandos Úteis

- **Rodar App:** `python src/main.py`
- **Rodar Testes:** `python -m unittest tests/test_stabilizer.py`
- **Instalar Deps:** `pip install -r requirements.txt`
- **Build Instalador:** `.agent\scripts\build_installer.bat`

---

> **Lembre-se:** Este projeto deve ser robusto. O usuário vai deixá-lo rodando por horas. Memory leaks ou travamentos da GUI são inaceitáveis.
