# Análise de Reclamações: Um Estudo de Caso da Americanas - Loja Online

## Resumo do Projeto

Este projeto realiza uma análise completa do perfil de reclamações registradas contra a Americanas - Loja Online na plataforma Reclame Aqui. O objetivo é identificar os principais motivos de insatisfação dos clientes e mapear padrões comportamentais a partir de dados reais, demonstrando um fluxo de trabalho completo de análise de dados, da coleta à visualização.

**Dashboard Interativo no Power BI:**  
[**Clique aqui para acessar o dashboard completo**](https://app.powerbi.com/view?r=eyJrIjoiMmEwZmM5MjQtMzYxZS00NTQ5LWIzNGEtNmJmNDE0ZWY1MGUwIiwidCI6ImIwZTU1Y2UzLTIzODktNDkwYi05MjRlLWRjNGRjZjI5NTZlOSJ9)

![Dashboard de Análise de Reclamações da Americanas](https://github.com/miysk/portifolio-review-analises/blob/main/dashboard/analisegraficos.png?raw=true)

---

## Principais Insights Descobertos

- **Volume Concentrado:** Foram analisadas 500 reclamações registradas em apenas 9 dias (26/05/2025 a 03/06/2025), indicando um volume médio de aproximadamente 55 novas reclamações por dia.

- **Temas Principais:** A análise textual identificou **Logística e Entrega** como a categoria mais crítica, representando **40,8%** das reclamações. Em segundo lugar, **Pagamento** (reembolsos e estornos) aparece com **31%**. Isso indica gargalos operacionais tanto na cadeia de suprimentos quanto no pós-venda financeiro.

- **Padrão Semanal:** Um pico acentuado de reclamações foi observado nas **terças-feiras**, sugerindo que os consumidores concentram suas insatisfações no início da semana útil.

- **Desempenho do Atendimento:** No momento da coleta, **100% das reclamações** encontravam-se com o status **"Não Respondida"**, mesmo após 9 dias da data de publicação. Esse atraso ultrapassa o prazo médio de resposta de 2 dias úteis estimado pelo Reclame Aqui. Esse cenário pode indicar uma possível sobrecarga ou insuficiência da equipe de atendimento.

---

## Ferramentas e Tecnologias Utilizadas

- **Coleta de Dados:** Python (`Selenium`, `BeautifulSoup4`, `undetected-chromedriver`)
- **Armazenamento:** SQL Server
- **Análise e Consulta:** SQL
- **Transformação e Visualização:** Power BI (`Power Query`, `DAX`)

---

## Metodologia

O projeto foi executado em quatro etapas principais:

1. **Web Scraping:** Desenvolvido um script em Python que navega automaticamente no site Reclame Aqui, coletando dados resumidos dos cartões e detalhes completos de cada reclamação.

2. **Armazenamento:** Os dados foram inicialmente salvos em arquivo `.csv` e posteriormente importados para uma tabela em um banco SQL Server.

3. **Análise:** Foram elaboradas consultas SQL para identificar padrões, categorias temáticas e comportamentos temporais das reclamações.

4. **Visualização:** Conexão dos dados ao Power BI, aplicação de transformações via Power Query e construção de um dashboard interativo com KPIs e gráficos dinâmicos.

---

## Consultas SQL Utilizadas

**Consulta 0: Preparação dos Dados - Conversão de Data**
*A coluna de data foi coletada como texto (`nvarchar`). Para permitir análises temporais, foi necessário criar uma nova coluna do tipo `DATE` e populá-la com os valores convertidos. Este é um passo fundamental de ETL (Extração, Transformação, Carga).*

```sql
-- Passo 1: Adicionar a nova coluna para a data convertida
ALTER TABLE dbo.Reclamacoes
ADD data_convertida DATE;
GO

-- Passo 2: Atualizar a nova coluna com os valores convertidos da coluna de texto
UPDATE dbo.Reclamacoes
SET data_convertida = TRY_CONVERT(DATE,
    CASE 
        WHEN CHARINDEX(' às ', data) > 0 THEN SUBSTRING(data, 1, CHARINDEX(' às ', data) - 1) 
        ELSE NULL -- Ignora formatos inesperados
    END, 103) -- 103 é o código de estilo para formato dd/mm/yyyy
WHERE data IS NOT NULL;
```


### Consulta 1: Categorização dos Temas das Reclamações

*Classifica cada reclamação em temas de negócio utilizando `CASE`, permitindo quantificar os principais motivos de insatisfação.*

```sql
-- Agrupa as reclamações em temas predefinidos para análise.
WITH TabelaComTemas AS (
    SELECT 
        CASE 
            WHEN LOWER(descricao_completa) LIKE '%entrega%' OR LOWER(descricao_completa) LIKE '%atraso%' OR LOWER(descricao_completa) LIKE '%rastreio%' THEN 'Logística e Entrega'
            WHEN LOWER(descricao_completa) LIKE '%reembolso%' OR LOWER(descricao_completa) LIKE '%estorno%' OR LOWER(descricao_completa) LIKE '%pagamento%' THEN 'Pagamento'
            WHEN LOWER(descricao_completa) LIKE '%cancelamento%' OR LOWER(descricao_completa) LIKE '%cancelar%' THEN 'Cancelamento'
            WHEN LOWER(descricao_completa) LIKE '%produto%' AND (LOWER(descricao_completa) LIKE '%defeito%' OR LOWER(descricao_completa) LIKE '%errado%') THEN 'Produto'
            WHEN LOWER(descricao_completa) LIKE '%propaganda enganosa%' THEN 'Publicidade'
            ELSE 'Outros'
        END AS Tema
    FROM dbo.Reclamacoes
)
SELECT 
    Tema,
    COUNT(*) AS Quantidade
FROM TabelaComTemas
GROUP BY Tema
ORDER BY Quantidade DESC;
```
### Consulta 2: Análise do Volume de Reclamações por Data e Dia da Semana

*Esta consulta consolidada agrega o número de reclamações por data específica e, ao mesmo tempo, identifica o dia da semana correspondente. Ela é a base para a criação de gráficos de tendência diária e de análise de comportamento semanal.*

```sql
-- Conta o número total de reclamações para cada dia da semana.
SELECT
    DATENAME(WEEKDAY, data_convertida) AS dia_da_semana,
    COUNT(*) AS total_reclamacoes
FROM dbo.Reclamacoes
WHERE data_convertida IS NOT NULL
GROUP BY 
    DATENAME(WEEKDAY
```


## Conclusão

Este estudo de caso demonstrou, com base em dados reais coletados do **Reclame Aqui**, que a **Americanas - Loja Online** enfrentou um **alto volume de reclamações concentradas em um curto período**, com destaque para os **problemas logísticos** e **financeiros**.

Além disso, foi identificado um possível **gargalo na capacidade de atendimento ao cliente**, uma vez que **100% das reclamações analisadas estavam com status "Não Respondida"**, mesmo considerando o prazo médio informado pela empresa de até **2 dias úteis** para resposta.

A análise também revelou **padrões comportamentais relevantes**, como o **pico de reclamações às terças-feiras**, o que pode sugerir um acúmulo de insatisfações durante o fim de semana e uma procura mais ativa por solução no início da semana útil.

