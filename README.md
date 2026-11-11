<h1 align="center">Asura's Wrath — port nativo para PC</h1>

<p align="center"><i>Asura's Wrath (Xbox 360) — port nativo para PC por recompilação estática (Otavix Engine 360). Gera a partir da sua .iso.</i></p>

<p align="center">
  <a href="https://github.com/otavix010/asuras-wrath-pc/commits/main"><img alt="Última atualização" src="https://img.shields.io/github/last-commit/otavix010/asuras-wrath-pc?label=%C3%BAltima%20atualiza%C3%A7%C3%A3o"></a>
  <a href="LICENSE"><img alt="Licença" src="https://img.shields.io/github/license/otavix010/asuras-wrath-pc?label=licen%C3%A7a"></a>
  <a href="https://github.com/otavix010/otavix-launcher/releases/latest"><img alt="Baixar o Otavix Launcher" src="https://img.shields.io/badge/Otavix%20Launcher-baixar-b00020"></a>
  <img alt="Windows 10/11" src="https://img.shields.io/badge/Windows-10%2F11-0078d4">
  <img alt="Linux: não suportado no momento" src="https://img.shields.io/badge/Linux-n%C3%A3o%20suportado-lightgrey">
</p>

<p align="center">
  <a href="#o-que-o-port-acrescenta">O que o port acrescenta</a> ·
  <a href="#estado-dos-testes">Estado dos testes</a> ·
  <a href="#plataformas">Plataformas</a> ·
  <a href="#requisitos">Requisitos</a> ·
  <a href="#desempenho-medido">Desempenho</a> ·
  <a href="#perguntas-frequentes">Perguntas frequentes</a> ·
  <a href="#gerar-à-mão-sem-o-launcher">Gerar à mão (sem o launcher)</a> ·
  <a href="#opções">Opções</a> ·
  <a href="#como-funciona">Como funciona</a>
</p>

> [!IMPORTANT]
> **Para jogar, baixe o [Otavix Launcher](https://github.com/otavix010/otavix-launcher/releases/latest).** Ele baixa este port, pede a sua `.iso`, gera o jogo no seu PC e o mantém atualizado. Para relatar um problema ou pedir algo, use **"Reportar problema"** na página do jogo no launcher: o relatório já vai com o log e as configurações, e é por ele que as correções saem mais rápido.
>
> **To play, download the [Otavix Launcher](https://github.com/otavix010/otavix-launcher/releases/latest).** It downloads this port, asks for your `.iso`, makes the game on your PC and keeps it updated. To report a problem or ask for something, use **"Report a problem"** on the game's page in the launcher: the report carries the log and the settings, and that is how fixes come out fastest.

Port do **Asura's Wrath** (Xbox 360) por **recompilação estática**: o código PowerPC do jogo é traduzido para C++ e compilado como um programa de Windows. Não há emulador de CPU rodando o jogo. A parte gráfica usa o runtime da **Otavix Engine 360**, derivado do ReXGlue e do [Xenia](https://xenia.jp) (veja os Créditos).

**Nada do jogo vem neste repositório.** O port é gerado no seu PC a partir da sua própria cópia (a imagem `.iso` do disco). O código traduzido também é gerado aí e nunca é distribuído.

O runtime é a **Otavix Engine 360 1.0.0** (privada): o gerador baixa o pacote pronto do servidor do launcher e confere o SHA-256. Ela descende do ReXGlue e do Xenia (BSD-3, veja os Créditos) e traz o AMD FidelityFX e as correções do port; os avisos de licença vão no pacote.

O jeito mais fácil de jogar é pelo [Otavix Launcher](https://github.com/otavix010/otavix-launcher), que baixa este port, pede a sua `.iso`, gera tudo e cuida das opções.

![Luta com BURST](docs/jogo.jpg)

## O que o port acrescenta

| | Xbox 360 | Port |
|--|--|--|
| Taxa de quadros | 30 fps | 30, **60**, 120 ou 144 fps (quadros reais) |
| Resolução interna | 720p | 720p, **1440p** ou 4K |
| Ampliação para a tela | — | AMD FSR 1, AMD CAS, FSR 3 temporal (experimental) ou bilinear, com nitidez ajustável |
| Anti-aliasing | o do jogo | o do jogo, mais FXAA opcional |
| Filtro anisotrópico | o do jogo | até 16x |
| Contador de fps | — | opcional, no canto da tela |

DLSS e XeSS não entram: os dois precisam de vetores de movimento, que os jogos de Xbox 360 não fornecem. O ganho de nitidez vem da resolução interna (supersampling de verdade), e a fluidez vem dos fps reais.

| Tela de título | Asura |
|---|---|
| ![Tela de título](docs/cena1.jpg) | ![Asura](docs/cena2.jpg) |

## Estado dos testes

- Episódios 1, 2 e 3 completos, com as QTEs, os contra-ataques e o tiro feitos pelo controle roteirizado e pelo leitor de avisos da tela (`scripts/qte.py`).
- Em 2x (1440p), com os render targets por ROV (o padrão dele em placas NVIDIA): 60 fps cravados nas lutas com a GPU em 45% (RTX 5080), 120 fps nas lutas (média 118,6) e 3x (4K) a 60 (média 59,5). Pelo caminho RTV, o mesmo trecho pedia 76% a 99% da GPU e caía para 48-54 fps; a imagem é a mesma nos dois.
- Som, saves e a troca de episódios funcionam.

## Plataformas

| | **Windows** | **Linux / SteamOS** |
|---|---|---|
| Situação | **funciona** (este port) | **não suportado e não testado** |
| Vídeo | Direct3D 12 (o Agility SDK vai ao lado do exe) | o runtime só tem o caminho D3D12 no Windows |
| Como jogar | pelo launcher, ou `gerar.ps1` e `jogar.cmd` | só o port de *God of War: Ascension* tem versão Linux (beta) por enquanto |

## Requisitos

- **Windows 10/11 64 bits** e GPU com **Direct3D 12**.
- **CPU x86-64 com SSE4.1.** AVX não é obrigatório: o gerador compila no seu PC com `-march=native` e usa o que o processador tiver.
- **Visual Studio 2022 Build Tools** com "Desenvolvimento para desktop com C++" e "C++ CMake tools for Windows" (o launcher confere).
- **A sua `.iso`** do *Asura's Wrath* (Asura's Wrath (World)).
- **Memória:** o mínimo exato não foi medido. Um cuidado medido: a compilação completa com 16 jobs chegou a ~35 GB de memória comprometida; o gerador limita os jobs (`-Jobs 4` é seguro).
- **Disco:** não medido com precisão: a `.iso`, mais as ferramentas (a engine, ~14 MB, e o Clang portátil) e a pasta de compilação.

## Desempenho medido

FPS de jogo. **Só colocamos o que foi medido**, e com **um jogo só rodando** (com outra carga junto, o desempenho pode cair bastante). Foram medidos no runtime anterior; na engine 1.0.0 a saída da GPU saiu **idêntica quadro a quadro** nos 4 ports e o boot não falhou, mas os FPS **ainda não foram remedidos**.

| Máquina | CPU | GPU | FPS |
|---|---|---|---|
| **PC 1** | Ryzen 7 9800X3D | RTX 5080 | 2x (1440p): **60 cravados** nas lutas (GPU em 45%); **120**: média 118,6 nas lutas e ~119 no Episódio 2 inteiro; 3x (4K) a 60 (média 59,5). Pelo caminho RTV cai para 48–54 |
| **PC 2** | Core i5-11400F | RX 9060 XT | não medido |
| **Notebook** | Core i5-10300H (4/8) | GTX 1650 | não medido |
| **Portátil** | Legion Go S (Linux) | Radeon 780M | não suportado |

DLSS e XeSS não existem para estes jogos (o Xbox 360 não fornece vetores de movimento); o FSR e o CAS atuam só na saída.

## Problemas conhecidos

- **DLC não suportada** (report 1092, em espera: faltam os pacotes para testar).
- A 120 fps, os QTEs de apertar rápido podem ficar mais difíceis.
- Tom esverdeado em algumas cenas (report 307): falta trazer uma correção do Xenia Canary.

## Gerar à mão (sem o launcher)

Precisa do **Visual Studio 2022 Build Tools** com "Desenvolvimento para desktop com C++" e "C++ CMake tools for Windows". O gerador baixa o resto: a Otavix Engine 360 e o Clang (LLVM) portátil, numa pasta `_ferramentas` ao lado do port.

```powershell
.\gerar.ps1 -Iso "D:\Jogos\Asura's Wrath (World).iso"
.\jogar.cmd
```

O port foi feito a partir do **Asura's Wrath (World)**. O gerador confere o `default.xex` da sua `.iso` (SHA-1 `bcaec56eabad135071ee879b4bbcc6aa1e3362b8`) e avisa se for outra versão.

## Opções

Ficam em `asuraswrath.toml` ao lado do executável, ou no arquivo indicado pela variável `PORT_OPCOES`. O launcher grava em `opcoes.toml`. Cada uma também vale na linha de comando (`--fps 120`) ou como variável de ambiente (`REX_FPS=120`).

| Opção | Valores | Padrão |
|--|--|--|
| `fps` | 30, 60, 120, 144 | 60 |
| `resolution_scale` | 1 (720p), 2 (1440p), 3 (4K) | 2 |
| `filtro` | `fsr`, `cas`, `fsr3` (temporal, experimental), `bilinear` | `fsr` |
| `nitidez` | 0 a 100 | 70 |
| `swap_post_effect` | `none`, `fxaa`, `fxaa_extreme` | `none` |
| `anisotropic_override` | -1 (o do jogo), 3 (4x), 4 (8x), 5 (16x) | 5 |
| `fullscreen` | `true`, `false` | `true` |
| `monitor` | 0 (padrão), 1, 2... | 0 |
| `mostrar_fps` | `true`, `false` | `false` |
| `volume` | 0 a 100 | 100 |
| `alvos` | `auto`, `rov`, `rtv`: como a EDRAM é imitada; `auto` usa o caminho medido melhor para o jogo | `auto` |
| `vibration` | `true`, `false` | `true` |
| `zona_morta_esquerda`, `zona_morta_direita` | 0 a 50 (%) | 0 |
| `user_language` | 1 inglês, 3 alemão, 4 francês, 5 espanhol, 6 italiano, 2 japonês | 1 |
| `iso` | caminho da `.iso` | — |

## Perguntas frequentes

**Este repositório tem o jogo?** Não. Você precisa da sua cópia (a imagem `.iso` do disco); o gerador monta o port no seu PC.

**Roda no Linux ou no SteamOS?** Ainda não: só o port de *God of War: Ascension* tem versão Linux (beta). Este roda no Windows.

**Saiu atualização. O que acontece com o jogo e os saves?** Atualize pelo launcher: ele refaz a tradução e a compilação uma vez (o gerador guarda a versão do runtime em `out\gerar\sdk.txt`). O jogo e os saves ficam.

**A `.iso` está danificada ou cortada.** O port agora recusa a imagem e diz o motivo no log, em vez de fechar.

**Onde relato um problema?** No launcher, em **"Reportar problema"** na página do jogo.

## Como funciona

- `config/funcoes.toml`: as funções que a análise estática não acha sozinha (chamadas só por ponteiro). `config/ganchos.toml`: os ganchos no código do jogo. `config/jogo.txt`: a versão do jogo que o gerador confere.
- `src/frame_rate.h`: os dois pontos que prendem o jogo em 30 fps viram uma opção. O intervalo de apresentação de 2 vblanks passa a 1, e o teto de tick do motor fica sem limite. Acima de 60, o vblank do console emulado também acelera.
- `src/port/`: a base comum dos ports de Xbox 360 (a mesma em todos).
- `src/port/input_lock.h`: corrige uma corrida na entrada de controles do runtime. A lista de controles é refeita a cada leitura sem trava, e a leitura do controle num thread junto com a vibração em outro corrompia o heap.
- `src/port/port_options.h`: as opções de imagem e os padrões do port.
- `src/port/fps_overlay.h`: o contador, que conta cada quadro entregue à GPU.
- `src/port/crash_log.h`: em caso de falha, grava `falha.log` com a pilha. `scripts/pilha.py` dá nome aos quadros.
- O app também lê a `.iso` direto (`iso`). As caixas de mensagem do sistema, que só aceitam teclado e mouse, são respondidas com o botão padrão (`headless`).

Para desenvolver: `build.cmd` compila; `scripts/rodar.py` roda numa janela com prints, o fps de cada segundo e um controle roteirizado (`PORT_PAD`; para começar um jogo novo: `--pad 45:START,58:A,64:A,67:A,70:UP,72.5:A`); `scripts/tecla.py` aperta botões no jogo em execução.

## Créditos

- [ReXGlue SDK](https://github.com/rexglue/rexglue-sdk): recompilador estático e runtime de Xbox 360 (BSD-3).
- [Xenia](https://github.com/xenia-project/xenia): o emulador em que o runtime se baseia (BSD-3).
- boma, em [xenia-canary/game-patches](https://github.com/xenia-canary/game-patches): achou onde o jogo trava os 30 fps.

Asura's Wrath é marca da Capcom. Este projeto não tem relação com a Capcom nem com a Microsoft.

## Licença

O código deste repositório está sob a licença MIT (`LICENSE`). O SDK e o runtime têm a licença própria deles (BSD-3).
