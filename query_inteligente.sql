WITH tb_compras AS (
    
    SELECT dt_compra,
        produto,
        AVG(valor_produto) AS valor_produto

    FROM compras
    GROUP BY dt_compra, produto
),



tb_lag AS (

    SELECT *,
        lag(dt_compra) OVER (PARTITION BY produto ORDER BY dt_compra) AS dt_compra_anterior
    FROM tb_compras
    ORDER BY produto, dt_compra

),


tb_avg AS(

    SELECT produto,
        avg(julianday(dt_compra) - julianday(dt_compra_anterior)) AS avg_dif_dias


    FROM tb_lag
    GROUP BY produto

),

tb_stats_produto AS (

    SELECT produto,
        max(dt_compra) AS dt_ultima_compra,
        avg(valor_produto) AS avg_valor
    FROM compras
    GROUP BY produto

),

tb_final AS (

SELECT t1.*,
        t2.avg_dif_dias,
        julianday('now') - julianday(dt_ultima_compra) AS dias_ultima_compra

FROM tb_stats_produto AS t1
LEFT JOIN tb_avg AS t2
ON t1.produto = t2.produto

)

SELECT * FROM tb_final


