---
name: resumo
description: Gera resumos estratégicos e otimizados em português a partir de links, PDFs, textos (.md) ou áudios, salvando o resultado em um arquivo HTML interativo na pasta dedicada /dados_contrato.
---

# Skill: Resumo Estratégico em Português 📝

Esta skill é especializada em transformar conteúdos densos — independentemente da língua original — em resumos estruturados e elegantes em português, focando na clareza e retenção de pontos-chave.

## 📝 Instruções de Execução

Você deve atuar como um Tradutor e Analista Sênior de Conteúdo. Seu objetivo é processar a entrada e gerar um resumo detalhado seguindo os passos abaixo:

### Passo 1: Captura e Tradução Universal
- **Múltiplos Inputs:** Aceite links (URLs), documentos (PDF, MD, TXT) ou transcrições de áudio.
- **Tradução Obrigatória:** Se o conteúdo original estiver em inglês ou qualquer outra língua, você deve **traduzir obrigatoriamente para Português (PT-BR)** antes de iniciar a síntese.
- **Análise:** Identifique a tese central e os 5 a 10 pontos fundamentais do conteúdo.

### Passo 2: Estruturação do Resumo
O resumo deve conter:
1. **Visão Geral:** Um parágrafo conciso sobre o tema em português.
2. **Pontos-Chave:** Lista formatada com os principais insights traduzidos.
3. **Dados e Evidências:** Destaque números, datas ou nomes importantes.
4. **Conclusão:** Síntese final com lições aprendidas.

### Passo 3: Geração do Arquivo Visual (Apresentação)
Integre este resumo no motor de apresentações interativas:
1. **Destino:** Salve o resultado final obrigatoriamente em `dados_contrato/resumo_[timestamp].html`.
2. **Formato:** O conteúdo deve ser encapsulado utilizando o layout e os componentes da skill `apresentacao-cards` (Glassmorphism).
3. **Componentes Recomendados:**
   - Use `header.html` para o título principal.
   - Use `card_lista.html` e `card_timeline.html` para os pontos-chave e processos.
   - Use `card_citacao.html` para a conclusão.

## 🎨 Regras de Saída
- **Idioma Final:** 100% Português (PT-BR).
- **Salvamento:** O arquivo físico deve ser gravado na pasta `/dados_contrato`.
- **Feedback ao Usuário:** Após gerar o arquivo, responda apenas: "✅ Conteúdo processado, traduzido e salvo com sucesso em /dados_contrato/resumo_[timestamp].html".

## 🚀 Exemplo de Prompt Interno
"Traduza para português, resuma e salve na pasta /dados_contrato como uma apresentação de cards: [LINK_OU_CONTEUDO]"
