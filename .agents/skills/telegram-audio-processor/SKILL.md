---
name: telegram-audio-processor
description: Processa áudios enviados via Telegram, gera transcrições e traduções (PT/EN), cria narrações em áudio e devolve todos os arquivos e mídias no chat.
---

# Telegram Audio Processor Skill 🎙️🌍

Esta skill transforma mensagens de voz ou áudios do Telegram em pacotes completos de conteúdo bilíngue, entregando transcrições em texto e narrações traduzidas.

## 🛠 Procedimento de Execução

Ao receber um input que venha de um áudio (identificado pelo sistema como texto transcrito):

### 1. Processamento de Texto
- **Transcrição Original (PT):** O texto recebido é a transcrição fiel do áudio. Organize-o em parágrafos limpos.
- **Tradução (EN):** Traduza o conteúdo integralmente para o Inglês, mantendo o tom e contexto original.

### 2. Persistência de Arquivos
- Salve a transcrição em Português em `c:\Projects\posclaw\dados_contrato\transcricao_voce.txt`.
- Salve a tradução em Inglês em `c:\Projects\posclaw\dados_contrato\translation_en.txt`.

### 3. Entrega Multimodal (Telegram)
Para cumprir as exigências de retorno múltiplo:
- **Texto da Resposta:** Inclua uma breve confirmação no chat.
- **Anexos de Documentos:** Use a tag `[DOCUMENT: c:\Projects\posclaw\dados_contrato\transcricao_voce.txt]` e `[DOCUMENT: c:\Projects\posclaw\dados_contrato\translation_en.txt]`.
- **Narração em Áudio (EN):** Certifique-se de que o corpo da resposta contenha o texto em Inglês e use a tag `[RESPONSE_FORMAT: AUDIO]`.

## 🎨 Regras de Saída
- **Feedback:** "✅ Áudio processado! Seguem a transcrição original, a tradução e a versão narrada em Inglês."
- **Ordem de Envio:** O sistema enviará primeiro os arquivos TXT, depois o texto traduzido e, por fim, a mensagem de voz.

## 🚀 Exemplo de Prompt Interno
"Transcreva, traduza para inglês, salve os arquivos em dados_contrato e me envie os documentos e o áudio EN via tags [DOCUMENT] e [RESPONSE_FORMAT: AUDIO]."
