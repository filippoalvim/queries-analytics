# 📊 SQL Analytics Portfolio

Este repositório tem como objetivo reunir projetos práticos de **análise de dados utilizando SQL**, com foco em resolução de problemas reais de negócio, exploração de dados e geração de insights acionáveis.

---

## 🎯 Objetivo

Demonstrar habilidades em:

* Manipulação e transformação de dados
* Análise exploratória (EDA)
* Criação de métricas e indicadores
* Modelagem de consultas eficientes
* Pensamento analítico aplicado a dados

---

## 🧠 Abordagem

Cada projeto presente neste repositório segue uma estrutura:

1. **Contexto do problema**
   Explicação do cenário de negócio e objetivo da análise

2. **Construção da lógica analítica**
   Queries SQL organizadas em etapas (CTEs), priorizando clareza e reutilização

3. **Métricas e cálculos**
   Criação de indicadores relevantes para tomada de decisão

4. **Insights finais**
   Interpretação dos resultados obtidos

---

## 📁 Estrutura do repositório

```
/projetos
  /nome-do-projeto
    - descricao.md
    - query.sql
    - insights.md
```

---

## 📌 Exemplo de análise

Um dos projetos deste repositório analisa o **intervalo de dias entre eventos de usuários**, com o objetivo de entender o comportamento de recorrência.

### O que foi feito:

* Cálculo do intervalo entre eventos utilizando `LEAD`
* Tratamento de eventos finais com `CURRENT_DATE`
* Cálculo da **mediana de dias entre eventos por usuário**
* Construção da **distribuição de usuários**
* Geração de **percentual acumulado (curva de comportamento)**

### Principais técnicas utilizadas:

* Window Functions (`LEAD`, `LAG`, `SUM OVER`)
* CTEs para organização da lógica
* `PERCENTILE_APPROX` para cálculo de mediana
* Análise de distribuição e acumulado

---

## 🚀 Ferramentas e tecnologias

* SQL (Spark SQL / Databricks / BigQuery-like)
* Git & GitHub
* Excel / Notebooks auxiliares para validação

---

## 📈 O que você vai encontrar aqui

* Queries otimizadas e bem estruturadas
* Problemas próximos de cenários reais de empresas
* Foco em clareza e storytelling com dados
* Evolução contínua com novos projetos

---

## 📬 Contato

Se quiser trocar ideias sobre dados, analytics ou oportunidades:

* LinkedIn: *https://www.linkedin.com/in/filippocupolillo/*
* Email: *filippoalvim@gmail.com*

---
