from 
--QY_SELLERS_CONTACT = """ 
SELECT DISTINCTROW
  IFNULL(
    CAST(`employee`.`cod_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'id',
  IFNULL(
    CAST(`employee`.`nome_colaborador` AS CHAR charset utf8mb4),
  'null') AS 'name',
  IFNULL(
    CAST(`employee`.`email` AS CHAR charset utf8mb4),
  'null') AS 'email',
  IFNULL(
    CAST(
      CONCAT('+55', `employee`.`ddd_celular`, `employee`.`celular`)
      AS CHAR charset utf8mb4),
  'null') AS 'phone'
FROM (`sg_colaborador` AS `employee`
  INNER JOIN `sg_grupo_colaborador` AS `employee_group`
  ON (`employee_group`.`cod_colaborador` = `employee`.`cod_colaborador`)
)"""

--QY_DEFAULT_SELLER = """ 
SELECT
  IFNULL(
    CAST(`cliente`.`cod_cliente` AS CHAR charset utf8mb4), 
  '0') AS '`cod_cliente`',
  IFNULL(
    CAST(`cliente`.`cod_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'cod_colaborador'
FROM `cd_cliente` AS `cliente`
WHERE (`cliente`.`cod_cliente`
  IN (
    SELECT DISTINCTROW `pedido`.`cod_cliente`
    FROM vd_pedido AS `pedido`
    WHERE YEAR(`pedido`.`dt_implant`) >= {STARTING_YEAR}
  )
)"""
--QY_PARTICIPANT_SELLER = """ 
SELECT 
  IFNULL(
    CAST(`cliente_participante`.`cod_cliente` AS CHAR charset utf8mb4), 
  '0') AS '`cod_cliente`,'
  IFNULL(
    CAST(`cliente_participante`.`cod_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'cod_colaborador'
FROM `cd_cliente_participante` AS `cliente_participante`
WHERE (`cliente_participante`.`cod_cliente`
  IN (
    SELECT DISTINCTROW `pedido`.`cod_cliente`
    FROM `vd_pedido` AS `pedido`
    WHERE YEAR(`pedido`.`dt_implant`) >= {STARTING_YEAR}
  )
)"""
--QY_SALES_TEAMS = """ 
SELECT DISTINCTROW
  IFNULL(
    CAST(`grupo_colaborador`.`cod_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'cod_colaborador',
  IFNULL(
    CAST(`colaborador`.`nome_colaborador` AS CHAR charset utf8mb4), 
  '0') AS 'nome_colaborador',
  IFNULL(
    CAST(`grupo_venda`.`cod_grupo_venda` AS CHAR charset utf8mb4), 
  '0') AS 'cod_grupo_venda',
  IFNULL(
    CAST(`grupo_venda`.`nome_grupo` AS CHAR charset utf8mb4),
  'null') AS 'equipe',
  IFNULL(
    CAST(`grupo_venda`.`cod_empresa` AS CHAR charset utf8mb4), 
  '0') AS 'cod_empresa'
FROM ((`vd_grupo` AS `grupo_venda`
  LEFT JOIN `vd_grupo_colaborador` AS `grupo_colaborador`
    ON (`grupo_colaborador`.`cod_grupo_venda` = `grupo_venda`.`cod_grupo_venda`))
  LEFT JOIN `sg_colaborador` AS `colaborador`
    ON (`colaborador`.`cod_colaborador` = `grupo_colaborador`.`cod_colaborador`)
)