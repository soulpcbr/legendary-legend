# Manual de Uso - LiveCaptionArchiver

## 🚀 Visão Geral

O **LiveCaptionArchiver** é uma ferramenta profissional para arquivar legendas em tempo real do Windows. Ele resolve o problema de "texto picotado" usando um algoritmo inteligente que espera a frase se estabilizar antes de salvar.

---

## 🛠️ Instalação

### 1. Pré-requisito Obrigatório: Tesseract OCR

Este software usa um motor de OCR industrial. Ele **precisa** ser instalado no Windows.

1. Baixe o instalador: [tesseract-ocr-w64-setup-v5.x.x.exe](https://github.com/UB-Mannheim/tesseract/wiki)
2. Durante a instalação, anote onde foi instalado (Geralmente `C:\Program Files\Tesseract-OCR`).
3. **CRÍTICO:** Adicione este caminho ao **PATH** do Windows.
   - _Como verificar?_ Abra um terminal e digite `tesseract --version`. Se aparecer a versão, está tudo certo.

### 2. Instalar Dependências

Abra o terminal na pasta do projeto e rode:

```powershell
pip install -r requirements.txt
```

---

## ▶️ Como Usar

### Passo 1: Iniciar

Execute o comando:

```powershell
python src/main.py
```

### Passo 2: Configurar a Captura

1. Abra o **Windows Live Captions** (Win + Ctrl + L) ou o vídeo/legenda que deseja gravar.
2. No App, clique em **"Selecionar Região"**.
3. Uma janela com borda vermelha e fundo transparente vai aparecer.
4. Arraste e redimensione essa janela para cobrir **exatamente** a área onde o texto aparece.
5. Pressione **ENTER** para confirmar.

### Passo 3: Gravar

1. Clique em **"Iniciar Gravação"**.
2. O Status Bar mudará para "Gravando...".
3. Acompanhe no Log. Note que ele não grava tudo instantaneamente? Isso é o **Estabilizador** funcionando. Ele espera a frase terminar para salvar.

### Passo 4: Configurações Avançadas

- **Timeout Silêncio:** Tempo sem texto novo para considerar a frase encerrada.
- **Auto-Ajuste:** Se ativado, o app aprende a velocidade da fala e ajusta o timeout sozinho (ótimo para palestrantes rápidos).
- **Inverter Cores:** Use se a legenda for **Texto Branco em Fundo Preto** (muito comum). Isso ajuda o OCR a ler melhor.

---

## 📂 Onde ficam os arquivos?

Os arquivos de texto (`.txt`) são salvos automaticamente na pasta `captions/` do projeto com o nome:
`captions_AAAA-MM-DD_HH-MM.txt`

Cada linha do arquivo possui um Timestamp preciso.

---

## 🐛 Solução de Problemas

**Erro: "Tesseract Não Encontrado"**

- Você instalou o Tesseract?
- Reiniciou o computador/terminal após instalar?
- Adicionou ao PATH?

**Erro: O texto está saindo errado/estranho**

- A região selecionada pega _apenas_ o texto? Evite bordas ou imagens de fundo.
- Tente marcar/desmarcar a opção **"Inverter Cores"**.
- O texto está muito pequeno? Tente aumentar a fonte da legenda no Windows.
