
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