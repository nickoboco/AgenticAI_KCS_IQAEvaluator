# AVALIADOR DE ARTIGOS com IA - IQA - METODOLOGIA KCS

Nesse projeto realizei a criação de um Agente de IA (Plugado em um LLM) com objetivo de realizar avaliação de artigos de conhecimentos com base na metodologia KCS - Knowledge Centered Support - considerando os itens listados no IQA - Índice de Qualidade do Artigo:

* Único Artigo
* Descrição Completa
* Ambiente
* Palavras-Chave
* Título Aderente
* Clareza
* Instruções Suficientes

A avaliação dos artigos de conhecimento faz parte do processo de implantação e gestão da metodologia KCS e com apoio da IA, o processo de avaliação pode ser otimizado.

![WhatsApp Image 2024-12-13 at 17 52 13](https://github.com/user-attachments/assets/a685f9ad-f6f0-46e5-8356-032562a3c686)

## VERSÃO LOW CODE

Com foco em otimizar o processo de implantação e facilitar a manutenção, criei uma versão curstomizada do fluxo no n8n, utilizando dois Agentes de IA especilizados em avaliar artigos e um Agente de IA supervisor, responsável por comparar e definir as notas e sugestões mais condizentes.

As avaliações realizadas pelos Agentes são armazenadas em um banco de dados e durante os próximos ciclos de avaliação do mesmo artigo, o Agente pode consultar o histórico e definir se determinado tópico foi melhorado e se sua sugestão foi seguida. Com base nisso, ele decide aumentar, diminuir ou manter a nota dada anteriormente.

![image](https://github.com/user-attachments/assets/c65fb1ac-1243-4f93-82de-fc7f1911aefd)

## FUTURO DO PROJETO

Em breve, esse Agentic Workflow estará integrado a plataforma de conhecimentos da empresa, possibilitando que os colaboradores utilizem o recurso durante a criação dos artigos e em etapas recorrentes de avaliação do IQA.

![image](https://github.com/user-attachments/assets/f46051ee-0771-4014-8b35-ef411b734a7e)
