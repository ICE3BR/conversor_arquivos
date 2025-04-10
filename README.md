# Conversor e Compressor de Arquivos

Uma aplicação em Python com interface gráfica para conversão e compressão de diversos tipos de arquivos.

## Funcionalidades

### Conversão de Arquivos
- Conversão entre diversos formatos de mídia
- Suporte para áudio, vídeo, imagens e documentos
- Opções avançadas de conversão como qualidade, resolução, taxa de bits
- Extração de áudio de arquivos de vídeo

### Compressão de Arquivos
- Compressão de diversos tipos de arquivos
- Diferentes níveis de compressão
- Compressão de imagem com qualidade ajustável
- Compressão de vídeo e áudio com parâmetros configuráveis

## Requisitos

- Python 3.6 ou superior
- Bibliotecas Python:
  - tkinter
  - PIL (Pillow)
  - PyPDF2 (opcional, para conversão de documentos)
- Ferramentas externas:
  - FFmpeg (necessário para conversão e compressão de áudio/vídeo)

## Instalação

1. Clone o repositório ou baixe os arquivos do projeto

2. Instale as dependências:
```bash
pip install pillow
pip install PyPDF2
```

3. Instale o FFmpeg:
   - Windows: Baixe e instale do [site oficial](https://ffmpeg.org/download.html) ou use gerenciadores de pacotes como Chocolatey
   - Linux: Use gerenciadores de pacotes (apt, yum, pacman)
   - macOS: Use o Homebrew (`brew install ffmpeg`)

## Uso

Execute o arquivo principal:
```bash
python main.py
```

### Conversão de arquivos:
1. Selecione o modo "Converter" na tela inicial
2. Clique em "Selecionar Arquivos" para escolher os arquivos a serem convertidos
3. Escolha o formato de saída desejado
4. (Opcional) Ative "Opções Avançadas" para configurar parâmetros adicionais
5. Escolha o diretório de saída ou use o padrão
6. Clique em "Converter" para iniciar o processo

### Compressão de arquivos:
1. Selecione o modo "Comprimir" na tela inicial
2. Clique em "Selecionar Arquivos" para escolher os arquivos a serem comprimidos
3. Escolha o nível de compressão desejado
4. Escolha o diretório de saída ou use o padrão
5. Clique em "Comprimir" para iniciar o processo

## Estrutura do Projeto

```
conversor_compressor/
├── main.py                 # Arquivo principal
├── interface/
│   ├── __init__.py
│   ├── app.py              # Interface principal
│   ├── tela_converter.py   # Interface de conversão
│   └── tela_comprimir.py   # Interface de compressão
├── utils/
│   ├── __init__.py
│   ├── compressor.py       # Funções de compressão
│   └── conversor.py        # Funções de conversão
└── assets/                 # Ícones e recursos visuais
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.