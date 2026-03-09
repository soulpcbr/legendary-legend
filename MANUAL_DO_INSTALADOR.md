# Manual do Instalador - LiveCaptionArchiver

Este é o guia prático e definitivo para criar o instalador `.exe` do **LiveCaptionArchiver** e as formas de compartilhamento com os seus usuários finais. Esqueça rodar mil comandos — agora tudo está automatizado no novo `.bat`.

---

## 🚀 1. O Que Você Precisa Ter Instalado no Computador

- [x] O **Python 3.8+** adicionado ao PATH do Windows. (Sem isso não é possível compilar nada).
- [x] O **Inno Setup (Versão 6)**, um software que cria instaladores para distribuições do Windows. Você o baixa [nesté link oficial (jrsoftware.org)](https://jrsoftware.org/isdl.php). Aceite as configurações padrão ao prosseguir com a instalação do app.

## 🔨 2. Como Fazer o Instalador (A Mágica)

Na pasta principal do projeto do `legendary-legend`, basta:

1. Dar dois cliques no arquivo:
   ▶️ **`GERAR_INSTALADOR.bat`**.

O que ele fará sozinho:

- Isolamento: criará a máquina virtual pra focar nas dependências (`build_env`);
- Download: instalará as bibliotecas requeridas como PyQt6, EasyOCR, libs;
- Empacotador (`PyInstaller`): transformando os arquivos Python em **bins do Windows executáveis** nativamente;
- Instalador (`InnoSetup`): juntando tudo, limpando sujeira, instalando atalhos e extraindo `LL.exe`.

> ⚠️ Todo o processo pode durar alguns minutos (geralmente entre **1 e 4 minutos**, pois os modelos e recursos das libs IA podem ser massivos para a compilação).

## 📦 3. Qual Arquivo Devo Enviar ao Meu Usuário?

O usuário final **só precisa ver e ter acesso a UM único arquivo**. A sua missão se concentra num único arquivo entregue ao seu consumidor final.

- Localize a nova pasta gerada **`dist\`** (dentro do repositório/raiz);
- Pegue o 👉 **`LL.exe`**.

**Basta encaminhar apenas o `LL.exe` aos seus usuários.**

> Ao clicarem duas vezes nele, ele gerará toda aquela janela convencional do _"Instalador Assistente (Wizard)_" com opção de Idioma da Interface, criar ícones na área de Trabalho e escolher onde salvar. Mágico, não é? 😊

## ⁉️ 4. O Sistema Pergunta Algo Sobre "SmartScreen"/"Protegido pelo Windows"?

Esse é o comportamento padrão do Microsoft Defender com softwares não-publicados comercialmente via Microsoft Verifier.
_Alerte aos seus usuários e consumidores:_ Se aparecer uma tela azul indicando **"O Windows protegeu o computador"**, peça que eles apenas cliquem em: **`Mais informações`** → **`Executar assim mesmo`**.

## 🔄 5. Lançou uma Versão Intergaláctica de Funcionalidades Novas (e agora)?

1. Apenas altere no arquivo `src\__version__.py` o novo número da release (Ex: `__version__ = "1.2.0"`).
2. Dê **dois cliques novamente em `GERAR_INSTALADOR.bat`**;
3. Resgate o **`LL.exe`** e suba para as nuvens de novo (Google drive/Releases/Discord, para compartilhar).

A arquitetura de Update já está montada. Ao instalarem de novo, e acharem a versão velha na máquina, eles **só farão Update Automático** - ele mantém o atalho do Iniciar/Mesa embutido e os Arquivos Textos/Log não serão deletados. Tudo prático! 🛡️

---

_Escrito pela Agência Antigravity. Boas criações e que venham muitas vendas/instalações do seu produto LiveCaptionArchiver!_
