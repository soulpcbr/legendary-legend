# LiveCaptionArchiver

## Descrição
Aplicativo Desktop para capturar, estabilizar e arquivar legendas em tempo real. Utiliza **EasyOCR** (com suporte a GPU/CPU e instalação automática de modelos) e algoritmos de estabilização de texto.

## Funcionalidades

- **Captura de Tela:** Selecione qualquer área da tela para ler legendas.
- **OCR Integrado:** Utiliza EasyOCR. **Não é necessário instalar nada externamente.** O aplicativo verifica e baixa os modelos necessários automaticamente na primeira execução.
- **Estabilização Inteligente:** Evita repetição de frases e "flicker" de legendas.
- **Exportação:** Salva o histórico em arquivo de texto.

## Instalação (Desenvolvimento)

1.  Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Execução

```bash
python src/main.py
```

## Como Gerar o Executável (.exe)

Para criar uma versão standalone (executável) para Windows, consulte o arquivo [BUILD_GUIDE.md](BUILD_GUIDE.md).
