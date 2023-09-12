-- db_uc_kami.vw_customer_details source
USE db_uc_kami;
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `vw_customer_details` AS
SELECT DISTINCTROW 
  IFNULL(CAST(`cliente`.`cod_cliente` AS CHAR charset utf8mb4), '0') AS `cod_cliente`,
  IFNULL(CAST(`cliente`.`nome_cliente` AS CHAR charset utf8mb4), '0') AS `nome_cliente`,
  IFNULL(CAST(`cliente`.`razao_social` AS CHAR charset utf8mb4), '0') AS `razao_social`,
  IFNULL(CAST(
    `ramo_atividade`.`desc_abrev` 
    AS CHAR charset utf8mb4),'0')
  AS `ramo_atividade`,
  IFNULL(CAST(`cliente_endereco`.`bairro` AS CHAR charset utf8mb4), '0') AS `bairro`,
  IFNULL(CAST(`cliente_endereco`.`cidade` AS CHAR charset utf8mb4), '0') AS `cidade`,
  IFNULL(CAST(`cliente_endereco`.`sigla_uf` AS CHAR charset utf8mb4), '0') AS `uf`,
  IFNULL(CAST(`cliente_endereco`.`endereco` AS CHAR charset utf8mb4), '0') AS `endereco`,
  IFNULL(CAST(`cliente_endereco`.`numero` AS CHAR charset utf8mb4), '0') AS `numero`,
  IFNULL(CAST(`cliente_endereco`.`cep` AS CHAR charset utf8mb4), '0') AS `cep`,
  IFNULL(CAST(
    DATE_FORMAT(`cliente`.`dt_implant`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_cadastro`,
  IFNULL(CAST(
    (
    SELECT 
      CASE
        WHEN (SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`)) > 0 
        THEN (TIMESTAMPDIFF(DAY,`recebe`.`dt_vencimento`,CURRENT_DATE()))
        ELSE '0'
      END    
    WHERE `recebe`.`dt_vencimento` < SUBDATE(CURDATE(), INTERVAL 1 DAY)    
    )
    AS CHAR charset utf8mb4), '0')
  AS `dias_atraso`,
  IFNULL(CAST(
    (
    SELECT 
      CASE 
        WHEN (SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`)) > 0
        THEN (SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`))
        ELSE '0' 
      END
    WHERE `recebe`.`dt_vencimento` < SUBDATE(CURDATE(), INTERVAL 1 DAY)    
    )
    AS DECIMAL(10,2)), 0.0)
  AS `valor_devido`,
  IFNULL(CAST(
    DATE_FORMAT(MIN(`nota_fiscal`.`dt_emissao`), '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_primeira_compra`,
  IFNULL(CAST(
    DATE_FORMAT(MAX(`nota_fiscal`.`dt_emissao`), '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_ultima_compra`,
  IFNULL(CAST((
    CASE
      WHEN(
        TIMESTAMPDIFF(DAY, MAX(`nota_fiscal`.`dt_emissao`), CURRENT_DATE())) > 180 
      THEN 'PERDIDO'
      WHEN(
        TIMESTAMPDIFF(DAY, MAX(`nota_fiscal`.`dt_emissao`), CURRENT_DATE())) > 90
      THEN 'INATIVO'
      WHEN(
        TIMESTAMPDIFF(DAY, MAX(`nota_fiscal`.`dt_emissao`), CURRENT_DATE())) > 60
      THEN 'PRE-INATIVO'
      ELSE 'ATIVO'
    END)
    AS CHAR charset utf8mb4), 'null')
  AS 'STATUS',
  IFNULL(CAST(
    MAX(YEAR(`nota_fiscal`.`dt_emissao`)) AS CHAR charset utf8mb4), '0')
  AS `ultimo_ano_ativo`,
  IFNULL(CAST(
    COUNT(`nota_fiscal`.`cod_nota_fiscal`)
    AS CHAR charset utf8mb4), '0')
  AS `qtd_total_compras`,
  IFNULL(CAST(
    COUNT(`nota_fiscal`.`cod_nota_fiscal`)
    AS CHAR charset utf8mb4), '0')
  AS `qtd_compras_semestre`,
  IFNULL(CAST(
    (
    SELECT SUM(`nota_fiscal`.`vl_total_nota_fiscal`)
    WHERE TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 180
    )    
    AS DECIMAL(10,2)), 0.0)
  AS `total_compras_semestre`,
  IFNULL(CAST(
      (
      SELECT SUM(`nota_fiscal`.`vl_total_nota_fiscal`)
      WHERE TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 90
      )    
      AS DECIMAL(10,2)), 0.0)
  AS `total_compras_trimestre`,
  IFNULL(CAST(
      (
      SELECT SUM(`nota_fiscal`.`vl_total_nota_fiscal`)
      WHERE TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 60
      )    
      AS DECIMAL(10,2)), 0.0)
  AS `total_compras_bimestre`
FROM ((((( `cd_cliente` AS `cliente`
LEFT JOIN `cd_cliente_endereco` AS `cliente_endereco`
  ON (`cliente_endereco`.`cod_cliente` = `cliente`.`cod_cliente`))
LEFT JOIN `cd_cliente_atividade` AS `cliente_atividade`
  ON (`cliente_atividade`.`cod_cliente` = `cliente`.`cod_cliente`))
LEFT JOIN `cd_ramo_atividade` AS `ramo_atividade`
  ON (`cliente_atividade`.`cod_ramo_atividade` = `ramo_atividade`.`cod_ramo_atividade`))
LEFT JOIN `vd_nota_fiscal` AS `nota_fiscal` 
  ON (`nota_fiscal`.`cod_cliente` = `cliente`.`cod_cliente`))
LEFT JOIN `fn_titulo_receber` AS `recebe`
  ON (`recebe`.`cod_cliente` = `cliente`.`cod_cliente`)
)
WHERE (`nota_fiscal`.`situacao` < 86)
AND (`nota_fiscal`.`situacao` > 79)
AND (`nota_fiscal`.`cod_empresa` IN (1,2,3,4,5,6,9,10,11,12,13,14,15,16))
AND (
  `nota_fiscal`.`nop` IN
  ('6.102', '6.404', 'BLACKFRIDAY', 'VENDA', 'VENDA_S_ESTOQUE', 'WORKSHOP')
)
AND `recebe`.`situacao` < 30
AND `recebe`.`cod_empresa` IN (1,2,3,4,5,6,9,10,11,12,13,14,15,16)
GROUP BY `cliente`.`cod_cliente`;