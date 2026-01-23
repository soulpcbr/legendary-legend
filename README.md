# LiveCaptionArchiver

## Descrição
Aplicativo Desktop para capturar, estabilizar e arquivar legendas em tempo real (ex: Windows Live Captions). Utiliza OCR (Tesseract) e algoritmos de comparação de texto para salvar apenas frases consolidadas.

## Requisitos Prévios (CRÍTICO)

Este aplicativo depende do **Tesseract OCR** para ler o texto da tela. O Tesseract **não** é uma biblioteca Python pura; ele é um programa externo que precisa estar instalado no seu sistema.

### Como instalar o Tesseract no Windows:

1.  **Baixe o instalador:**
    - Acesse: [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
    - Baixe a versão `tesseract-ocr-w64-setup-v5.x.x.exe` (64-bit).

2.  **Instale:**
    - Execute o instalador.
    - **IMPORTANTE:** Durante a instalação, pode haver uma opção para adicionar ao PATH, mas é recomendável fazer manualmente ou garantir que o aplicativo saiba onde está.
    - O caminho padrão geralmente é: `C:\Program Files\Tesseract-OCR`

3.  **Configuração no Sistema (PATH):**
    - Pressione `Win + S`, digite "Variáveis de Ambiente" e abra "Editar as variáveis de ambiente do sistema".
    - Clique em "Variáveis de Ambiente...".
    - Em "Variáveis do sistema" (parte de baixo), encontre a variável `Path` e clique em "Editar".
    - Clique em "Novo" e adicione o caminho da pasta onde instalou o Tesseract (ex: `C:\Program Files\Tesseract-OCR`).
    - Clique em OK em tudo.
    - Reinicie seu terminal ou IDE para que a alteração surta efeito.

## Instalação do Projeto

1.  Instale as dependências Python:
    ```bash
    pip install -r requirements.txt
    ```

## Execução

Execute o arquivo principal:

```bash
python src/main.py
```

## Funcionalidades

- **Captura de Tela Otimizada:** Usa `mss` para alta performance.
- **Estabilização de Texto:** Algoritmo inteligente que aguarda a frase "firmar" antes de salvar, evitando duplicatas parciais (ex: "Olá" -> "Olá mundo").
- **Timeout Dinâmico:** O tempo de silêncio para considerar uma frase finalizada pode ser ajustado automaticamente com base na velocidade da fala.
- **Sobreposição (Overlay):** Seleção visual da área da legenda na tela.
- **Tratamento de Imagem:** Opção para inverter cores e binarização automática para melhorar a precisão do OCR.
