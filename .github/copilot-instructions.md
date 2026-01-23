# Instruções para Agentes (GitHub Copilot & Cursor) — LiveCaptionArchiver (Legendary Legend)

**Objetivo:** Contexto inequívoco para o desenvolvimento do **LiveCaptionArchiver**, um aplicativo Desktop para Windows que arquiva legendas em tempo real com correção inteligente.

## ✅ Checklist Rápido (Executar antes de qualquer ação)

- [ ] **Ambiente:** O `venv` está ativo? As dependências (`requirements.txt`) estão instaladas?
- [ ] **Tesseract:** O binário do Tesseract está acessível/configurado no PATH ou no script?
- [ ] **Threading:** O OCR está rodando em uma `QThread` separada? **NUNCA** bloquear a GUI.
- [ ] **MVC:** O código respeita a separação Model-View-Controller?
- [ ] **Testes:** Rodei `test_stabilizer.py` para garantir que a lógica de dedup não quebrou?

---

## 1) Stack e Tecnologias

| Componente | Tecnologia | Obs |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | Tipagem estrita recomendada (`typing`). |
| **GUI** | PyQt6 | Padrão MVC. |
| **OCR** | Tesseract (pytesseract) | Requer binário instalado no Windows. |
| **Captura** | `mss` | Ultra fast cross-platform screenshot. |
| **Img Proc** | `opencv-python` | Pré-processamento (binarização/inversão). |
| **Lógica** | `difflib` | Comparação de similaridade de strings. |

---

## 2) Arquitetura (MVC Estrito)

### 2.1 Model (Lógica de Negócios)
- **Classe:** `CaptionStabilizer` (Cérebro do app).
- **Responsabilidade:** Receber texto bruto, estabilizar frases (lidar com a volatilidade "hello" -> "Hello world"), e decidir quando salvar no disco.
- **Classe:** `FileManager` (IO).
- **Responsabilidade:** Gerenciar arquivo `.txt` com flush imediato.

### 2.2 View (Interface Gráfica)
- **Janela Principal (`MainControlWindow`):** Controles (Start/Stop), Logs, Status.
- **Overlay (`OverlaySelector`):** Janela transparente/redimensionável ("Always on Top") para definir a região de captura (ROI).

### 2.3 Controller (Orquestração)
- **Worker (`OCRWorker`):** Thread dedicada que usa `mss` para capturar a tela e `pytesseract` para extrair texto.
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
- Verificar se Tesseract está instalado na inicialização.
- Se não estiver, exibir popup amigável e não crashar.
- Salvar arquivos com encoding `utf-8`.

---

## 4) Organização de Arquivos

```
/
├── src/
│   ├── main.py           # Entry point
│   ├── model/
│   │   ├── stabilizer.py # Lógica de buffer
│   │   └── file_manager.py
│   ├── view/
│   │   ├── main_window.py
│   │   └── overlay.py
│   ├── controller/
│   │   └── ocr_worker.py # Thread de captura/OCR
│   └── utils/
│       └── image_proc.py # Funções OpenCV
├── tests/
│   └── test_stabilizer.py # Teste vital da lógica de texto
├── agent/                # Documentação, prompts, lixo de dev
├── .github/              # Configurações do Agente
└── requirements.txt
```

---

## 5) Comandos Úteis

- **Rodar App:** `python src/main.py`
- **Rodar Testes:** `python -m unittest tests/test_stabilizer.py`
- **Instalar Deps:** `pip install -r requirements.txt`

---

> **Lembre-se:** Este projeto deve ser robusto. O usuário vai deixá-lo rodando por horas. Memory leaks ou travamentos da GUI são inaceitáveis.
