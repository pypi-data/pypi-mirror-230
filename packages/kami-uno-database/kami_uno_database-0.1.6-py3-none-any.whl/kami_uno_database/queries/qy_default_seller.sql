SELECT
  IFNULL(
    CAST(`cliente`.`cod_cliente` AS CHAR charset utf8mb4), 
  '0') AS 'cod_cliente',
  IFNULL(
    CAST(`cliente`.`cod_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'cod_colaborador'
FROM `cd_cliente` AS `cliente`
WHERE (`cliente`.`cod_cliente`
  IN (
    SELECT DISTINCTROW `pedido`.`cod_cliente`
    FROM vd_pedido AS `pedido`
    WHERE YEAR(`pedido`.`dt_implant`) >= 2022
  )
)