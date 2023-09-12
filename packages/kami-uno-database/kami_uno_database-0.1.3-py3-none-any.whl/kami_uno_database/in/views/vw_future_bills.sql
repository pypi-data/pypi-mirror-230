-- db_uc_kami.vw_future_bills source
USE db_uc_kami;
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `vw_future_bills` AS
SELECT
  IFNULL(CAST(`titulo_receber`.`cod_empresa` AS CHAR charset utf8mb4),'0') AS `cod_empresa`,
  IFNULL(CAST(`empresa`.`razao_social` AS CHAR charset utf8mb4),'0') AS `nome_empresa_pedido`,
  IFNULL(CAST(
    DATE_FORMAT(`titulo_receber`.`dt_vencimento`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_vencimento`,
  IFNULL(CAST(
    (
      SUM(`titulo_receber`.`vl_total_titulo`)
      - SUM(`titulo_receber`.`vl_total_baixa`)
    )
    AS DECIMAL(10, 2)), 0.0)
  AS `total_a_receber`
FROM (
  `fn_titulo_receber` AS `titulo_receber`
LEFT JOIN `cd_empresa` AS `empresa`
  ON (`empresa`.`cod_empresa` = `titulo_receber`.`cod_empresa`)
)
WHERE `titulo_receber`.`situacao` < 30
AND `titulo_receber`.`dt_vencimento` > CURDATE()
GROUP BY `titulo_receber`.`cod_empresa`, `titulo_receber`.`dt_vencimento`;
