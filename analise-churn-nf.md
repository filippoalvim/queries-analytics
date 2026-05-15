# 📋 Análise de Churn — Metodologia e Queries

Este documento detalha o processo analítico para definição dos limiares de **pré-churn**, **churn** e **pós-churn** no produto de escaneamento de notas fiscais da VR, incluindo as três abordagens testadas e a evolução do raciocínio.

---

## Problema de Negócio

Usuários do produto de envio de NF da VR acumulam cashback e benefícios escaneando suas notas fiscais. Campanhas de reengajamento precisam ser acionadas **no momento certo** — nem cedo demais (spam para usuários ativos), nem tarde demais (usuário já perdido).

A pergunta central era:

> **Após quantos dias sem envio de NF um usuário deve ser classificado como em risco de churn?**

---

## Estrutura dos Dados

A base de análise contém o histórico de envio de NFs por usuário (`cpf`), com a data de cada escaneamento. O objetivo é calcular o **intervalo entre envios consecutivos** e derivar um indicador comportamental por usuário.

---

## Abordagem 1 — Máximo do Intervalo

### Lógica

Para cada usuário, calcular o **maior intervalo** registrado entre dois envios consecutivos de NF.

```sql
WITH base_eventos AS (
    SELECT
        cpf AS user_id,
        data_criacao AS event_date,
        LEAD(data_criacao) OVER (
            PARTITION BY cpf
            ORDER BY data_criacao
        ) AS next_event_date
    FROM analytics_layer.fact_nf_events
),

intervalos AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS dias_entre_eventos
    FROM base_eventos
),

maximo_por_usuario AS (
    SELECT
        user_id,
        MAX(dias_entre_eventos) AS max_dias_entre_eventos
    FROM intervalos
    GROUP BY user_id
)

SELECT
    max_dias_entre_eventos,
    COUNT(DISTINCT user_id) AS qtd_usuarios
FROM maximo_por_usuario
GROUP BY max_dias_entre_eventos
ORDER BY max_dias_entre_eventos;
```

### Por que não funciona

O **máximo representa o pior momento** do usuário — uma viagem, um período de férias, uma troca de aparelho. Um usuário que envia NF diariamente mas ficou 90 dias inativo em agosto seria tratado como um usuário de baixa frequência.

> ❌ Maximiza o outlier e não representa o comportamento habitual.

---

## Abordagem 2 — Média do Intervalo

### Lógica

Para cada usuário, calcular a **média dos intervalos** entre envios consecutivos.

```sql
WITH base_eventos AS (
    SELECT
        cpf AS user_id,
        data_criacao AS event_date,
        LEAD(data_criacao) OVER (
            PARTITION BY cpf
            ORDER BY data_criacao
        ) AS next_event_date
    FROM analytics_layer.fact_nf_events
),

intervalos AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS dias_entre_eventos
    FROM base_eventos
),

media_por_usuario AS (
    SELECT
        user_id,
        AVG(dias_entre_eventos) AS media_dias_entre_eventos
    FROM intervalos
    GROUP BY user_id
)

SELECT
    ROUND(media_dias_entre_eventos, 0) AS media_dias,
    COUNT(DISTINCT user_id) AS qtd_usuarios
FROM media_por_usuario
GROUP BY ROUND(media_dias_entre_eventos, 0)
ORDER BY media_dias;
```

### Por que não funciona

A média é **sensível a outliers**. Considere um usuário com 3 intervalos registrados: `[2, 2, 135]`. Sua média é ~46 dias — o que faz parecer que ele envia NFs a cada mês e meio, quando na prática ele envia praticamente todo dia. Quanto menos NFs o usuário enviou, maior o impacto de um único intervalo atípico na média.

> ❌ A média depende da quantidade de envios e é distorcida por pausas eventuais.

---

## Abordagem 3 — Mediana do Intervalo ✅

### Lógica

Para cada usuário, calcular a **mediana dos intervalos** entre envios consecutivos usando `PERCENTILE_APPROX`.

```sql
WITH base_eventos AS (
    SELECT
        user_id,
        event_date,
        LEAD(event_date) OVER (
            PARTITION BY user_id
            ORDER BY event_date
        ) AS next_event_date
    FROM analytics_layer.fact_user_events
),

intervalos AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS dias_entre_eventos
    FROM base_eventos
),

mediana_por_usuario AS (
    SELECT
        user_id,
        PERCENTILE_APPROX(dias_entre_eventos, 0.5) AS mediana_dias_entre_eventos
    FROM intervalos
    GROUP BY user_id
),

distribuicao AS (
    SELECT
        mediana_dias_entre_eventos,
        COUNT(DISTINCT user_id) AS qtd_usuarios
    FROM mediana_por_usuario
    GROUP BY mediana_dias_entre_eventos
),

acumulado AS (
    SELECT
        mediana_dias_entre_eventos,
        qtd_usuarios,
        SUM(qtd_usuarios) OVER (
            ORDER BY mediana_dias_entre_eventos
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS soma_acumulada_usuarios,
        ROUND(
            SUM(qtd_usuarios) OVER (
                ORDER BY mediana_dias_entre_eventos
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) * 100.0
            / SUM(qtd_usuarios) OVER (),
        2) AS percentual_acumulado
    FROM distribuicao
)

SELECT
    *,
    LAG(percentual_acumulado) OVER (
        ORDER BY mediana_dias_entre_eventos
    ) AS percentual_anterior,
    percentual_acumulado
        - LAG(percentual_acumulado) OVER (
            ORDER BY mediana_dias_entre_eventos
        ) AS percentual_diferenca
FROM acumulado
ORDER BY mediana_dias_entre_eventos;
```

### Por que funciona

A mediana representa o **valor central da distribuição de intervalos** de cada usuário. Para o mesmo exemplo `[2, 2, 135]`, a mediana é **2 dias** — identificando corretamente que este é um usuário de alta frequência. Ela combina frequência com recorrência e é robusta a outliers.

> ✅ Representa o comportamento real e habitual do usuário.

---

## Resultados da Distribuição

Com a mediana como métrica base, a curva de distribuição acumulada revelou:

| Mediana de Intervalo | % Acumulado de Usuários |
|----------------------|-------------------------|
| ≤ 1 dia              | ~40%                    |
| ≤ 5 dias             | ~65%                    |
| ≤ 10 dias            | ~75%                    |
| **≤ 15 dias**        | **~80% ← Pareto**       |
| ≤ 30 dias            | ~90%                    |

### Curva Logarítmica

O formato da curva é **logarítmico**: o crescimento do percentual acumulado é muito rápido nos primeiros dias e desacelera progressivamente. Isso confirma que:

1. A base é dominada por usuários de alta frequência
2. Intervalos maiores representam uma parcela cada vez menor e decrescente de usuários
3. O incremento marginal de cada dia adicional de intervalo traz pouquíssimos usuários novos a partir de ~15 dias

```
% Acumulado
   100% |                                                    __________
    90% |                                     ______________/
    80% |                        ____________/ ← Pareto (15 dias)
    70% |               ________/
    60% |          _____/
    40% |    ______/
    20% |___/ ← 40% enviam NF todo dia
     0% +----+----+----+----+----+----+----+----+----+-----→ dias
          0   1   2   3   4   5   7   10  12  15  20  30
```

---

## Definição dos Limiares de Churn

Com base na curva de Pareto e no comportamento observado, os limiares foram definidos da seguinte forma:

| Fase           | Critério                                                        |
|----------------|-----------------------------------------------------------------|
| **Ativo**      | Dentro do intervalo habitual de envio (até o ponto de Pareto)   |
| **Pré-Churn**  | Ultrapassou o intervalo habitual — sinal de queda de engajamento |
| **Churn**      | Inativo há tempo suficiente para caracterizar abandono do hábito |
| **Pós-Churn**  | Inativo por período significativamente acima do limiar de churn  |

O ponto de corte de **15 dias** (80° percentil da base) foi usado como âncora para calibrar esses limiares, garantindo que a classificação de risco seja **baseada em evidência comportamental** e não em critério arbitrário.

---

## Comparativo das Abordagens

| Métrica  | Sensível a Outliers? | Representa comportamento habitual? | Indicada? |
|----------|----------------------|-------------------------------------|-----------|
| Máximo   | ✅ Sim               | ❌ Não                              | ❌        |
| Média    | ✅ Sim               | ⚠️ Parcialmente                    | ❌        |
| Mediana  | ❌ Não               | ✅ Sim                              | ✅        |

---

## Tecnologias Utilizadas

- **SQL** — Spark SQL / Databricks
- **Window Functions** — `LEAD`, `LAG`, `SUM OVER`, `ROW_NUMBER`
- **Estatística aplicada** — `PERCENTILE_APPROX`, distribuição acumulada, princípio de Pareto
- **CTEs** — estrutura modular para clareza e reutilização da lógica
