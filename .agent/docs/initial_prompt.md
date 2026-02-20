# PROMPT DE DESENVOLVIMENTO DE SOFTWARE: LiveCaptionArchiver

## PERFIL

Atue como um Arquiteto de Software Sênior especialista em Python, Visão Computacional (OCR) e Arquitetura Desktop (GUI). Você é meticuloso com Clean Code, padrões MVC e tratamento de exceções.

## OBJETIVO

Criar um aplicativo Desktop para Windows (extensível para Cross-platform) chamado "LiveCaptionArchiver".
O objetivo do app é capturar legendas em tempo real (especificamente do Windows Live Captions), processar as correções de texto que ocorrem ao vivo e salvar o histórico consolidado em um arquivo `.txt` timestamped.

## PRINCIPAIS DESAFIOS & SOLUÇÕES

1. **Volatilidade da Legenda:** A legenda muda (ex: "hello" -> "Hello world"). O app não pode gravar linha por linha; ele deve manter um "buffer" e só gravar no disco quando a frase estiver "estabilizada" ou finalizada.
2. **Performance:** O OCR deve ser rápido. Usaremos `mss` para captura de tela (screen grab) de alto desempenho.
3. **Usabilidade:** O usuário precisa definir visualmente ONDE está a legenda na tela.

## STACK TECNOLÓGICA

- **Linguagem:** Python 3.10+
- **GUI:** PyQt6 (Padrão MVC estrito).
- **OCR:** Tesseract OCR (via `pytesseract`).
- **Captura de Tela:** `mss` (Ultra fast cross-platform screenshot).
- **Processamento de Imagem:** `opencv-python` (Para pré-processar a imagem antes do OCR: grayscale, threshold).
- **Lógica de Texto:** `difflib` (Nativo) para comparação de similaridade de strings.

## SETUP DO AMBIENTE (Instruções para o Agente)

Gere um arquivo `requirements.txt` contendo:
`PyQt6`, `pytesseract`, `mss`, `opencv-python`, `numpy`.

_Nota Crítica:_ Adicione comentários no código instruindo o usuário a instalar o binário do Tesseract no Windows e adicionar ao PATH, ou configurar o caminho manualmente no código.

## ARQUITETURA (MVC)

### 1. MODEL (Lógica de Negócios)

Crie uma classe `CaptionStabilizer` que contenha a lógica inteligente:

- Atributos: `current_buffer` (frase sendo formada), `last_commit_time`.
- Método `process_new_text(raw_text)`:
  - Compare `raw_text` com `current_buffer` usando `difflib.SequenceMatcher`.
  - **Regra de Estabilização:**
    - Se a similaridade for > 60% (é a mesma frase sendo corrigida): Atualize `current_buffer` com a versão mais longa/recente.
    - Se a similaridade for baixa (é uma nova frase): Faça "Commit" do `current_buffer` no arquivo de texto e inicie um novo buffer.
    - Se `raw_text` estiver vazio por X segundos: Faça "Commit" (silêncio na fala).

Crie uma classe `FileManager`:

- Cria um arquivo `captions_YYYY-MM-DD_HH-MM.txt` ao iniciar.
- Método `append_text(text)`: Escreve a linha com timestamp no arquivo e dá flush imediato.

### 2. VIEW (Interface Gráfica)

Crie duas janelas:

1. **MainControlWindow:**
   - Botão "Selecionar Área de Captura".
   - Botão "Iniciar Gravação" / "Parar Gravação".
   - Área de Log (TextEdit) mostrando o que está sendo gravado em tempo real.
   - Status bar indicando se o Tesseract foi encontrado.

2. **OverlaySelector (Snipping Tool style):**
   - Uma janela semitransparente com borda vermelha que o usuário pode redimensionar e arrastar.
   - Serve para definir as coordenadas (x, y, width, height) que o OCR vai ler.

### 3. CONTROLLER (Orquestração)

- Use `QThread` ou `QRunnable` para rodar o loop de OCR (`OCRWorker`). **Jamais** rode o OCR na thread principal da GUI para não travar o app.
- O `OCRWorker` deve:
  1. Capturar a região definida pelo `OverlaySelector` usando `mss`.
  2. Converter para escala de cinza e aplicar binarização (OpenCV) para melhorar a leitura do Tesseract.
  3. Extrair texto.
  4. Enviar sinal com o texto para o Model processar.

## IMPLEMENTAÇÃO PASSO A PASSO

### PASSO 1: Estrutura e Utilitários

- Crie a estrutura de pastas.
- Implemente o `CaptionStabilizer` (O cérebro do app). Teste a lógica de comparação de strings isoladamente.

### PASSO 2: Interface (View)

- Implemente a `MainControlWindow` com PyQt6.
- Implemente o `OverlaySelector`. Ele deve ficar "Always on Top" (`Qt.WindowStaysOnTopHint`) até a seleção ser confirmada.

### PASSO 3: O Worker de OCR

- Implemente a thread que captura a tela e roda o Tesseract.
- Garanta tratamento de erro caso o Tesseract não esteja instalado (mostre um popup amigável).

### PASSO 4: Integração

- Conecte os botões da View ao Controller.
- Conecte os sinais do Worker (texto detectado) para atualizar a View (Log) e o Model (Arquivo).

## REGRAS DE NEGÓCIO CRÍTICAS

1. **Deduplicação Inteligente:** O Live Captions repete muito texto enquanto ajusta. O `CaptionStabilizer` é a prioridade número 1. Ele não pode gravar "Hello" e depois "Hello World". Ele deve esperar e salvar apenas "Hello World".
2. **Tratamento de Arquivo:** O arquivo deve ser aberto em modo `utf-8`. Use `file.flush()` após cada escrita para garantir que, se o app fechar abruptamente, os dados estejam salvos.
3. **Robustez do OCR:** Pré-processe a imagem. As legendas do Windows geralmente são texto branco sobre fundo preto. Inverta as cores se necessário ou use thresholding do OpenCV para garantir contraste máximo.

## LOOP DE TESTE E AUTO-CORREÇÃO (Instruções para o Agente)

1. Ao finalizar o código, crie um script de teste unitário (`test_stabilizer.py`) que simule a entrada de texto picotado:
   - Entrada simulada: ["Ola", "Ola tudo", "Ola tudo bem.", "Hoje vamos", "Hoje vamos programar"]
   - Saída esperada no arquivo:
     - "Ola tudo bem."
     - "Hoje vamos programar"
2. Se o teste falhar (duplicar linhas ou perder correções), refatore a classe `CaptionStabilizer` antes de me entregar o código final.

## RESTRIÇÕES

- NÃO use `pyautogui` para captura de tela (é lento). Use `mss`.
- NÃO coloque toda a lógica em um único arquivo `.py`. Separe em `main.py`, `ui.py`, `core.py`.
- NÃO esqueça de tratar o erro `TesseractNotFoundError`. O app não pode crashar se o usuário não tiver o binário instalado; ele deve avisar.

Gere o código completo, modularizado e pronto para rodar.
