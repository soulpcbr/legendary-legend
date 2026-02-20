# LiveCaptionArchiver

Aplicativo Desktop para capturar, estabilizar e arquivar legendas em tempo real. Utiliza **EasyOCR** (com suporte a GPU/CPU e instalação automática de modelos) e algoritmos de estabilização inteligente de texto.

## Funcionalidades

- **Captura de Tela:** Selecione qualquer área da tela para ler legendas.
- **OCR Integrado:** Utiliza EasyOCR. **Não requer instalação externa.** Os modelos são baixados automaticamente na primeira execução.
- **Estabilização Inteligente:** Evita repetição de frases e "flicker" de legendas.
- **Exportação:** Salva o histórico em arquivo `.txt` com timestamps precisos.

## Instalação — Usuário Final

Baixe o **`LL.exe`** da página de Releases e execute. O instalador:

- Permite escolher a pasta de instalação
- Cria atalhos no Desktop e Menu Iniciar (opcional)
- Instala, repara ou atualiza automaticamente
- **NÃO requer Python instalado**

## Instalação — Desenvolvimento

```bash
git clone https://github.com/soulpcbr/legendary-legend.git
cd legendary-legend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Organização do Projeto

```
legendary-legend/
├── src/                 # Código fonte (MVC: core/ ui/ workers/ utils/)
├── tests/               # Testes unitários
├── .agent/              # Central de configuração, docs e scripts
│   ├── config/          # Configurações do agente AI
│   ├── docs/            # 📚 Documentação completa
│   ├── instructions/    # Instruções para agentes AI
│   ├── scripts/         # Scripts de build (build_installer.bat, installer.iss)
│   ├── skills/          # Biblioteca de skills AI
│   ├── temp/            # Temporários
│   └── workflows/       # Automações
├── captions/            # Legendas capturadas (dados do usuário)
├── logs/                # Logs de execução
├── requirements.txt
├── LICENSE
└── README.md
```

> Para documentação detalhada e organização completa, veja [`.agent/docs/PROJECT_OVERVIEW.md`](.agent/docs/PROJECT_OVERVIEW.md).

## Build do Instalador

```batch
.agent\scripts\build_installer.bat
```

Gera `dist/LL.exe` — instalador auto-suficiente.

## Documentação

| Documento                                                    | Descrição                                                       |
| :----------------------------------------------------------- | :-------------------------------------------------------------- |
| [Visão Geral e Organização](.agent/docs/PROJECT_OVERVIEW.md) | **★ Referência canônica** — estrutura, arquitetura, organização |
| [Guia de Build](.agent/docs/BUILD_GUIDE.md)                  | Como compilar o projeto e gerar LL.exe                          |
| [Guia do Instalador](.agent/docs/INSTALLER_GUIDE.md)         | Funcionalidades e uso do instalador                             |
| [Manual de Uso](.agent/docs/MANUAL_DE_USO.md)                | Guia para o usuário final                                       |

## Testes

```bash
python -m unittest tests/test_stabilizer.py
python -m unittest tests/test_stabilizer_extended.py
```

## Licença

MIT — Veja [LICENSE](LICENSE).
