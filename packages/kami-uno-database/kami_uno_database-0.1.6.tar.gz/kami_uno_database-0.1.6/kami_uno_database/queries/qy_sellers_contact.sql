
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
)