# 📊 Análise de Churn — Escaneamento de Notas Fiscais (VR)

Este repositório documenta a análise de **churn comportamental de usuários** no produto de escaneamento de notas fiscais da VR, com foco na definição de limiares de **pré-churn**, **churn** e **pós-churn** a partir do comportamento real de envio dos usuários.

## 📊 Dashboard Interativo

> **[🔗 Abrir visualização interativa](https://htmlpreview.github.io/?https://raw.githubusercontent.com/filippoalvim/queries-analytics/main/churn-dashboard.html)**
>
> Explore a curva de distribuição logarítmica, filtre por intervalo de dias e veja os indicadores de usuários e percentual acumulado em tempo real.

---

## 🧩 Contexto do Problema

O produto de envio de notas fiscais da VR permite que trabalhadores escaneiem suas NFs e acumulem cashback e benefícios. Para acionar campanhas de reengajamento com precisão, era necessário responder:

> **"Quantos dias sem envio de NF caracterizam um usuário em risco de churn?"**

A resposta exigia entender o **padrão de frequência de envio** de cada usuário — e não uma definição arbitrária baseada em feeling.

---

## 🔬 Evolução da Abordagem Estatística

Para definir o intervalo típico entre envios por usuário, foram testadas **três abordagens estatísticas**, cada uma com suas limitações:

### 1️⃣ Máximo — "O pior cenário"

A primeira tentativa foi calcular o **maior intervalo** entre duas NFs consecutivas de cada usuário.

**Problema:** o máximo representa o pior momento do usuário, não o comportamento habitual. Um usuário que envia NF todo dia, mas ficou 90 dias sem enviar em um momento de viagem, seria classificado como churn tardio — o que distorce completamente a análise.

> ❌ Maximiza o outlier. Não representa o comportamento real.

---

### 2️⃣ Média — "Puxada pelos extremos"

A segunda abordagem foi calcular a **média dos intervalos** entre envios.

**Problema:** a média é altamente sensível a outliers. Um usuário que enviou 3 NFs — duas com intervalo de 2 dias e uma com intervalo de 135 dias — terá uma média de ~46 dias, mascarando que ele, na prática, é um usuário frequente.

> ❌ Distorcida por intervalos atípicos. Penaliza usuários recorrentes com eventuais pausas.

---

### 3️⃣ Mediana — "A frequência real do usuário"

A abordagem final foi calcular a **mediana dos intervalos** entre envios consecutivos por usuário.

A mediana combina **frequência** com **recorrência**: ela representa o intervalo mais típico daquele usuário, ignorando picos e vales extremos. É robusta a outliers e reflete fielmente o ritmo de envio.

> ✅ Representa o comportamento central do usuário. Escolha ideal para definição de churn.

---

## 📈 Distribuição dos Usuários por Mediana de Intervalo

Com a mediana calculada por usuário, foi construída a **curva de distribuição acumulada** — percentual de usuários por faixa de dias de intervalo.

### Principais achados:

```
Intervalo (dias)  | % Acumulado de Usuários
------------------|------------------------
≤ 1 dia           | ~40%
≤ 5 dias          | ~65%
≤ 10 dias         | ~75%
≤ 15 dias         | ~80%   ← Ponto de Pareto
≤ 30 dias         | ~90%
```

### Curva Logarítmica

O gráfico de distribuição acumulada forma uma **curva logarítmica**, o que revela um padrão claro:

> **Quanto maior o intervalo de envio, menor é o incremento de novos usuários naquele grupo.**

O crescimento é acelerado nos primeiros dias e desacelera progressivamente — comportamento típico de uma base concentrada em usuários altamente frequentes.

```
% Acumulado
   100% |                                          ___________
    80% |                          _______________/
    60% |               __________/
    40% |    ___________/
    20% |___/
     0% +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+---→ dias
        0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
```

---

## 🎯 Conclusões e Definição dos Limiares de Churn

### Ponto de Pareto (80/20)

Aplicando o **princípio de Pareto**, identificamos que **80% dos usuários possuem um intervalo mediano de envio de até 15 dias**. Esse é o ponto de inflexão que baliza a definição de churn:

| Fase           | Definição                                                       |
|----------------|-----------------------------------------------------------------|
| **Ativo**      | Usuário dentro do seu intervalo habitual de envio               |
| **Pré-Churn**  | Usuário que ultrapassou o intervalo habitual, mas ainda não atingiu o limiar crítico |
| **Churn**      | Usuário que atingiu o limiar baseado na curva de Pareto (≥ 15 dias para 80% da base) |
| **Pós-Churn**  | Usuário inativo por período significativamente acima do limiar  |

### Insight de Alta Frequência

> **40% dos usuários têm mediana de intervalo ≤ 1 dia**, ou seja, **4 em cada 10 usuários enviam notas fiscais todos os dias.**

Esse dado reforça que a base possui um núcleo de usuários altamente engajados — o que torna a definição de churn ainda mais crítica para não disparar alertas prematuros para esse grupo.

---

## 🛠️ Técnicas e Ferramentas

| Categoria           | Tecnologia/Técnica                             |
|---------------------|------------------------------------------------|
| Linguagem           | SQL (Spark SQL / Databricks)                   |
| Window Functions    | `LEAD`, `LAG`, `SUM OVER`, `ROW_NUMBER`        |
| Estatística         | `PERCENTILE_APPROX` (mediana), média, máximo   |
| Estrutura da query  | CTEs em camadas para separação de responsabilidades |
| Validação           | Excel com dados sintéticos                     |

---

## 📁 Arquivos

| Arquivo | Descrição |
|--------|-----------|
| [`analise-churn`](./analise-churn) | Query SQL final com cálculo de mediana, distribuição e percentual acumulado |
| [`tb_nfs_ofertas_campanhas.ipynb`](./tb_nfs_ofertas_campanhas.ipynb) | Pipeline completo de processamento de NFs por campanha (Databricks) |
| [`portfolio_distribuicao_dias_sem_envio_sintetico.xlsx`](./portfolio_distribuicao_dias_sem_envio_sintetico.xlsx) | Dados sintéticos da distribuição de usuários por intervalo de envio |

---

## 📬 Contato

* LinkedIn: [filippocupolillo](https://www.linkedin.com/in/filippocupolillo/)
* Email: filippoalvim@gmail.com
