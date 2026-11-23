# Agent Video Editor v1.0.0

Primeira versão pública do **Agent Video Editor**, um conjunto aberto de ferramentas locais para edição e montagem de vídeos com Python, FFmpeg e FFprobe, utilizável pela linha de comando ou por agentes compatíveis com Agent Skills.

## Recursos incluídos

- Análise de arquivos de vídeo (duração, codecs, resolução, FPS e áudio).
- Folhas de contato e inspeção de quadros próximos aos cortes.
- Sugestões de sincronização por transientes de áudio.
- Montagem reproduzível por arquivo de linha do tempo JSON, com cortes secos e ajustes de velocidade.
- Flashes breves em branco, preto e exposição, controlados por quadros.
- Renderização de vídeos MP4 e verificação técnica da saída.

## Requisitos e instalação

Requer **Python 3.9 ou superior**, **FFmpeg** e **FFprobe** disponíveis no PATH. Descompacte `Agent-Video-Editor-v1.0.0.zip` preservando a pasta `andrew-video-editor/`; consulte o `README.md` dessa pasta para exemplos de utilização. Para agentes compatíveis com Agent Skills, instale a pasta completa com esse mesmo nome.

Nenhum serviço em nuvem, cadastro ou chave de API é necessário para o núcleo da ferramenta.

## Limitações

Esta versão não fornece interface gráfica, transições complexas ou decisões criativas automáticas. Inspecione o vídeo renderizado antes de distribuí-lo. Flashes rápidos podem afetar pessoas com fotossensibilidade.

## Distribuição

O arquivo ZIP anexo contém o pacote de aplicação com código-fonte, instruções, documentação e exemplos. Arquivos temporários e caches Python não estão incluídos. O arquivo SHA-256 anexo permite conferir a integridade do download.

Código aberto, com licença MIT para o pacote `andrew-video-editor/`.
