USE db_uc_kami;

DROP FUNCTION IF EXISTS `GetDiasAtraso`;

DELIMITER / / CREATE FUNCTION `GetDiasAtraso`(cod_cliente INT) RETURNS INT BEGIN DECLARE dias_atraso INT;

SELECT
  (
    CASE
      WHEN (
        SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`)
      ) > 0 THEN (
        TIMESTAMPDIFF(DAY, `recebe`.`dt_vencimento`, CURRENT_DATE())
      )
      ELSE 0
    END
  ) INTO dias_atraso
FROM
  `fn_titulo_receber` AS `recebe`
WHERE
  (
    `recebe`.`dt_vencimento` < SUBDATE(CURDATE(), INTERVAL 1 DAY)
  )
  AND (`recebe`.`situacao` < 30)
  AND (`recebe`.`cod_cliente` = cod_cliente);

RETURN dias_atraso;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetValorDevido`;

DELIMITER / / CREATE FUNCTION `GetValorDevido`(cod_cliente INT) RETURNS INT BEGIN DECLARE valor_devido INT;

SELECT
  (
    CASE
      WHEN (
        SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`)
      ) > 0 THEN (
        SUM(`recebe`.`vl_total_titulo`) - SUM(`recebe`.`vl_total_baixa`)
      )
      ELSE '0'
    END
  ) INTO valor_devido
FROM
  `fn_titulo_receber` AS `recebe`
WHERE
  `recebe`.`dt_vencimento` < SUBDATE(CURDATE(), INTERVAL 1 DAY)
  AND (`recebe`.`situacao` < 30)
  AND (`recebe`.`cod_cliente` = cod_cliente);

RETURN valor_devido;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetDtPrimeiraCompra`;

DELIMITER / / CREATE FUNCTION `GetDtPrimeiraCompra`(cod_cliente INT) RETURNS DATETIME BEGIN DECLARE dt_primeira_compra DATETIME;

SELECT
  (MIN(`nota_fiscal`.`dt_emissao`)) INTO dt_primeira_compra
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN dt_primeira_compra;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetDtUltimaCompra`;

DELIMITER / / CREATE FUNCTION `GetDtUltimaCompra`(cod_cliente INT) RETURNS DATETIME BEGIN DECLARE dt_ultima_compra DATETIME;

SELECT
  (MAX(`nota_fiscal`.`dt_emissao`)) INTO dt_ultima_compra
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN dt_ultima_compra;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetDtPenultimaCompra`;

DELIMITER / / CREATE FUNCTION `GetDtPenultimaCompra`(cod_cliente INT) RETURNS DATETIME BEGIN DECLARE dt_penultima_compra DATETIME;

SELECT
  `nota_fiscal`.`dt_emissao` INTO dt_penultima_compra
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  )
ORDER BY
  `nota_fiscal`.`dt_emissao` DESC
LIMIT
  1 OFFSET 1;

RETURN dt_penultima_compra;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetDiasUltimaCompra`;

DELIMITER / / CREATE FUNCTION `GetDiasUltimaCompra`(cod_cliente INT) RETURNS INT BEGIN DECLARE dias_ultima_compra INT;

SELECT
  (
    TIMESTAMPDIFF(
      DAY,
      `GetDtUltimaCompra`(cod_cliente),
      CURRENT_DATE()
    )
  ) INTO dias_ultima_compra;

RETURN dias_ultima_compra;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetDiasPenultimaCompra`;

DELIMITER / / CREATE FUNCTION `GetDiasPenultimaCompra`(cod_cliente INT) RETURNS INT BEGIN DECLARE dias_penultima_compra INT;

SELECT
  (
    TIMESTAMPDIFF(
      DAY,
      `GetDtPenultimaCompra`(cod_cliente),
      CURRENT_DATE()
    )
  ) INTO dias_penultima_compra;

RETURN dias_penultima_compra;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetStatusCliente`;

DELIMITER / / CREATE FUNCTION `GetStatusCliente`(cod_cliente INT) RETURNS CHAR(11) BEGIN DECLARE cliente_status CHAR(11);

DECLARE dias_ultima_compra INT;

SET
  dias_ultima_compra = `GetDiasUltimaCompra`(cod_cliente);

SELECT
  (
    CASE
      WHEN(
        `GetDiasUltimaCompra`(cod_cliente) <= 30
        AND `GetDiasPenultimaCompra`(cod_cliente) >= 180
      ) THEN 'NOVO'
      WHEN(dias_ultima_compra > 60) THEN 'PRE-INATIVO'
      WHEN(dias_ultima_compra > 90) THEN 'INATIVO'
      WHEN(dias_ultima_compra > 180) THEN 'PERDIDO'
      ELSE 'ATIVO'
    END
  ) INTO cliente_status;

RETURN cliente_status;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetQtdTotalCompras`;

DELIMITER / / CREATE FUNCTION `GetQtdTotalCompras`(cod_cliente INT) RETURNS INT BEGIN DECLARE qtd_total_compras INT;

SELECT
  (
    COUNT(`nota_fiscal`.`cod_nota_fiscal`)
  ) INTO qtd_total_compras
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN qtd_total_compras;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetQtdComprasSemestre`;

DELIMITER / / CREATE FUNCTION `GetQtdComprasSemestre`(cod_cliente INT) RETURNS INT BEGIN DECLARE qtd_compras_semestre INT;

SELECT
  (
    COUNT(`nota_fiscal`.`cod_nota_fiscal`)
  ) INTO qtd_compras_semestre
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (
      TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 180
    )
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN qtd_compras_semestre;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetTotalComprasBimestre`;

DELIMITER / / CREATE FUNCTION `GetTotalComprasBimestre`(cod_cliente INT) RETURNS DECIMAL(10, 2) BEGIN DECLARE total_compras_bimestre DECIMAL(10, 2);

SELECT
  (
    SUM(`nota_fiscal`.`cod_nota_fiscal`)
  ) INTO total_compras_bimestre
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (
      TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 60
    )
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN total_compras_bimestre;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetTotalComprasTrimestre`;

DELIMITER / / CREATE FUNCTION `GetTotalComprasTrimestre`(cod_cliente INT) RETURNS DECIMAL(10, 2) BEGIN DECLARE total_compras_trimestre DECIMAL(10, 2);

SELECT
  (
    SUM(`nota_fiscal`.`cod_nota_fiscal`)
  ) INTO total_compras_trimestre
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (
      TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 90
    )
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN total_compras_trimestre;

END / / DELIMITER;

DROP FUNCTION IF EXISTS `GetTotalComprasSemestre`;

DELIMITER / / CREATE FUNCTION `GetTotalComprasSemestre`(cod_cliente INT) RETURNS DECIMAL(10, 2) BEGIN DECLARE total_compras_semestre DECIMAL(10, 2);

SELECT
  (
    SUM(`nota_fiscal`.`cod_nota_fiscal`)
  ) INTO total_compras_semestre
FROM
  `vd_nota_fiscal` AS `nota_fiscal`
WHERE
  (
    `nota_fiscal`.`nop` IN (
      '6.102',
      '6.404',
      'BLACKFRIDAY',
      'VENDA',
      'VENDA_S_ESTOQUE',
      'WORKSHOP',
      'VENDA DE MERCADORIA P/ NÃO CONTRIBUINTE',
      'VENDA MERCADORIA DENTRO DO ESTADO'
    )
    AND (`nota_fiscal`.`situacao` > 79)
    AND (`nota_fiscal`.`situacao` < 86)
    AND (
      TIMESTAMPDIFF(DAY, `nota_fiscal`.`dt_emissao`, CURRENT_DATE()) <= 180
    )
    AND (`nota_fiscal`.`cod_cliente` = cod_cliente)
  );

RETURN total_compras_semestre;

END / / DELIMITER;