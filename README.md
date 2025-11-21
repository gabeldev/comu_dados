# Projeto: Multiplexação e Demultiplexação de Áudio (AM)

Este repositório contém um exemplo didático de multiplexação e demultiplexação de sinais de áudio usando modulação AM (DSB-SC) em Python. O fluxo principal gera sinais de teste, realiza a multiplexação (modulação e soma de portadoras) e em seguida recupera cada canal com filtragem e demodulação.

## Estrutura do projeto

- `main.py`        : Script principal. Gera sinais de teste (`input1.wav`, `input2.wav`, `input3.wav`), executa o `MultiplexadorAudio` e depois o `Demultiplexador`.
- `multiplexador.py`: Classe `MultiplexadorAudio` — carrega/ajusta áudios, aplica filtro passa-baixa, realiza modulação e salva o arquivo `muxed_audio.wav` e arquivos base para comparação (`audio_A_base.wav`, ...).
- `demultiplexador.py`: Classe `Demultiplexador` — lê `muxed_audio.wav`, aplica filtros passa-banda, demodula, aplica passa-baixa e salva `demux_channel_*.wav`. Também contém funções de plotagem/comparação.

## Requisitos

- Python 3.8+ 
- Pacotes Python:
  - numpy
  - soundfile
  - matplotlib
  - scipy

## Instalação rápida

1. Criar e ativar um ambiente virtual (opcional, recomendado):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

## Como executar

O `main.py` já demonstra a pipeline completa (gera sinais de teste, multiplexa e demultiplexa):

```bash
python3 main.py
```

O fluxo padrão realiza:
- Geração de 3 arquivos de entrada: `input1.wav` (seno 440 Hz), `input2.wav` (seno 880 Hz), `input3.wav` (ruído branco).
- Multiplexação: instancia `MultiplexadorAudio(file1, file2, file3)` e chama `executar()` — gera `muxed_audio.wav` e arquivos `audio_?_base.wav`.
- Demultiplexação: instancia `Demultiplexador()` — lê `muxed_audio.wav` e salva `demux_channel_A.wav`, `demux_channel_B.wav`, `demux_channel_C.wav`.

## Arquivos gerados

- `input1.wav`, `input2.wav`, `input3.wav` — sinais de teste (gerados por `main.py`).
- `muxed_audio.wav` — sinal multiplexado (A + B + C modulado).
- `audio_A_base.wav`, `audio_B_base.wav`, `audio_C_base.wav` — versões base (banda-base) salvas pelo multiplexador para comparação.
- `demux_channel_A.wav`, `demux_channel_B.wav`, `demux_channel_C.wav` — canais recuperados pelo demultiplexador.

## Observações técnicas

- Frequência de amostragem usada por padrão: 44100 Hz.
- Portadoras definidas no código:
  - Canal A: 4000 Hz
  - Canal B: 10000 Hz
  - Canal C: 14000 Hz
- O multiplexador aplica um filtro passa-baixa (~1900 Hz) antes da modulação para evitar sobreposição de espectro entre canais.
- O demultiplexador aplica filtros passa-banda em torno de cada portadora, demodula por multiplicação por cosseno e aplica filtro passa-baixa para recuperar a banda-base.

## Visualização e comparação

As classes incluem métodos que mostram espectros e espectrogramas:
- `MultiplexadorAudio.plot_spectrum` — mostra espectros dos sinais modulados e do sinal multiplexado.
- `Demultiplexador.comparar_sinais_visual` / `comparar_espectro` / `plota_erros` — exibem comparações visuais entre sinal original e sinal demultiplexado.