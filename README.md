# Agent Video Editor

**Agent Video Editor** é um conjunto de ferramentas abertas para **montagem e edição de vídeos com cortes precisos**, usando Python, FFmpeg e FFprobe, com execução local e resultados reproduzíveis. Pode ser utilizado diretamente pela linha de comando ou integrado a assistentes compatíveis com a especificação **Agent Skills**.

Ele ajuda a analisar tomadas, escolher pontos de corte, organizar uma sequência, sincronizar mudanças de imagem com a música e aplicar flashes breves na linha do tempo. **Não é um editor gráfico com interface de arrastar e soltar**, nem gera vídeos por inteligência artificial a partir de prompts.

## Para que serve

- Inspecionar arquivos de vídeo: duração, resolução, FPS, codecs e presença de áudio.
- Criar folhas de contato e extrair quadros ao redor dos cortes para avaliar continuidade.
- Identificar possíveis pontos de sincronização por transientes de áudio.
- Definir cortes secos e mudanças de velocidade em uma timeline JSON reproduzível.
- Aplicar flashes curtos em branco, preto ou exposição com duração especificada em quadros.
- Renderizar prévias e versões finais em MP4 e verificar as propriedades técnicas da saída.

As decisões criativas continuam com a pessoa ou agente que realiza a edição: um pico de áudio, por exemplo, é uma sugestão de ponto de corte, não uma ordem automática.

## Requisitos

- Python **3.9 ou posterior**;
- **FFmpeg** e **FFprobe** disponíveis no `PATH`;
- arquivos de vídeo locais e espaço suficiente para os arquivos temporários de renderização.

O núcleo não exige conta, serviço em nuvem nem chave de API. A saída atual utiliza codificação H.264/AAC e a disponibilidade dos codificadores depende da instalação local do FFmpeg.

## Primeiros passos

Entre na pasta principal da ferramenta:

```bash
cd andrew-video-editor
python3 scripts/probe.py video.mp4
python3 scripts/contact_sheet.py video.mp4 -o contato.jpg
python3 scripts/boundary_frames.py video.mp4 --at 2.50 -o quadros/
```

Para editar, copie e adapte [`assets/timeline.example.json`](andrew-video-editor/assets/timeline.example.json) com os arquivos existentes e os intervalos desejados. Em seguida:

```bash
python3 scripts/render_timeline.py timeline.json --fast
python3 scripts/verify.py intro-preview.mp4
```

Os caminhos da timeline relativos ao arquivo JSON são resolvidos em relação à pasta onde esse JSON está salvo. Por padrão, o editor não substitui os arquivos de origem pelo arquivo final.

## Recursos e limites da versão 1.0.0

A versão atual implementa cortes secos, mudanças de velocidade, normalização de resolução/FPS, concatenação, áudio original quando disponível, silêncio para tomadas sem áudio e flashes de curta duração. **Não oferece interface gráfica, efeitos complexos, transições avançadas nem automação completa da decisão editorial.** Ajustes de ritmo e continuidade devem ser conferidos por inspeção das imagens e do vídeo renderizado.

Flashes rápidos podem afetar pessoas sensíveis à luz: utilize efeitos com cuidado e confira o resultado antes de distribuir.

## Documentação e desenvolvimento

O pacote [andrew-video-editor/](andrew-video-editor/) contém o [guia de uso](andrew-video-editor/README.md), a [instrução para agentes](andrew-video-editor/SKILL.md), referências de edição, scripts e o formato de timeline. Os testes automatizados ficam em [`tests/`](tests/).

**Licenças:** o conteúdo da pasta `andrew-video-editor/` é disponibilizado nos termos da licença **MIT** indicada em [`andrew-video-editor/LICENSE`](andrew-video-editor/LICENSE). O arquivo [`LICENSE`](LICENSE) na raiz, preexistente, contém **CC0 1.0**; consulte as licenças aplicáveis antes de redistribuir.

Projeto de **Bobby Dias e Andrew Vox** · Enterprise.
