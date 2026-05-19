---
name: youtube-transcritor-tradutor
description: Transcreve vídeos do YouTube com timestamps, gera uma tradução completa para Português (PT-BR), sintetiza áudio (TTS) e devolve tudo via Telegram.
---

# YouTube Transcritor, Tradutor & Narrador Skill 🎥🎙️

Esta skill avançada automatiza a extração de transcrições do YouTube, gera traduções profissionais e cria uma versão narrada (áudio) em Português (PT-BR), entregando o conteúdo completo diretamente no Telegram.

## 🛠 Procedimento de Execução

Ao receber um link do YouTube, siga rigorosamente estes passos:

### 1. Extração da Transcrição via Browser
Use o `browser_subagent` para capturar a transcrição original:
- Navegue até o URL do vídeo.
- Clique em "...mais" (...more) na descrição do vídeo para expandir os detalhes.
- Clique no botão **"Mostrar transcrição" (Show transcript)**.
- Copie todo o texto da transcrição (incluindo os timestamps).
- Priorize o idioma original (geralmente Inglês/English).

### 2. Salvamento Persistente (No Servidor)
- Salve a transcrição original em `c:\Projects\posclaw\dados_contrato\transcricao_[VIDEO_ID].txt`.
- Salve a tradução estruturada em `c:\Projects\posclaw\dados_contrato\traducao_[VIDEO_ID].txt`.
- Estes arquivos servem como backup e histórico no sistema.

### 3. Síntese de Áudio e Entrega via Telegram
Para cumprir a exigência de retorno via Telegram (Texto + Áudio):
- Prepare o conteúdo da resposta final com a **tradução completa para Português (PT-BR)**.
- Adicione uma introdução breve indicando que os arquivos foram salvos.
- **Obrigatório:** No final da resposta, insira a tag `[RESPONSE_FORMAT: AUDIO]`.
- Isso fará com que o sistema envie tanto o texto da tradução quanto a narração (TTS) para o usuário.

## 📁 Estrutura de Arquivos
- **Pasta:** `c:\Projects\posclaw\dados_contrato/`
- **Padrão:**
    - `transcricao_[VIDEO_ID].txt` (Original)
    - `traducao_[VIDEO_ID].txt` (Traduzido)

## 🎨 Regras de Saída
- **Idioma Final:** Português (PT-BR) 🇧🇷.
- **Formatação:** Use parágrafos claros para a tradução.
- **Entrega:** Ative o formato `AUDIO` para garantir que o usuário receba a voz narrada juntamente com a tradução escrita no chat.

## 🚀 Exemplo de Fluxo Interno
1. Captura `00:01 - Hello` -> `00:01 - Olá`.
2. Salva arquivos no sistema.
3. Responde: "Abaixo está a tradução do vídeo... [TEXTO DA TRADUÇÃO] [RESPONSE_FORMAT: AUDIO]"
