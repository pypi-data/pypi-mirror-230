-- db_uc_kami.vw_customer_details source
CREATE
OR REPLACE ALGORITHM = UNDEFINED VIEW `vw_customer_details` AS
SELECT
  DISTINCTROW IFNULL(
    CAST(`cliente`.`cod_cliente` AS CHAR charset utf8mb4),
    '0'
  ) AS `cod_cliente`,
  IFNULL(
    CAST(`cliente`.`nome_cliente` AS CHAR charset utf8mb4),
    '0'
  ) AS `nome_cliente`,
  IFNULL(
    CAST(`cliente`.`razao_social` AS CHAR charset utf8mb4),
    '0'
  ) AS `razao_social`,
  IFNULL(
    CAST(
      `ramo_atividade`.`desc_abrev` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `ramo_atividade`,
  IFNULL(
    CAST(
      `cliente_endereco`.`bairro` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `bairro`,
  IFNULL(
    CAST(
      `cliente_endereco`.`cidade` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `cidade`,
  IFNULL(
    CAST(
      `cliente_endereco`.`sigla_uf` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `uf`,
  IFNULL(
    CAST(
      `cliente_endereco`.`endereco` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `endereco`,
  IFNULL(
    CAST(
      `cliente_endereco`.`numero` AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `numero`,
  IFNULL(
    CAST(`cliente_endereco`.`cep` AS CHAR charset utf8mb4),
    '0'
  ) AS `cep`,
  IFNULL(
    CAST(
      DATE_FORMAT(`cliente`.`dt_implant`, '%Y-%m-%d %H:%i:%s') AS CHAR charset utf8mb4
    ),
    'null'
  ) AS `dt_cadastro`,
  IFNULL(
    CAST(
      GetDiasAtraso(`cliente`.`cod_cliente`) AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `dias_atraso`,
  IFNULL(
    CAST(
      GetValorDevido(`cliente`.`cod_cliente`) AS DECIMAL(10, 2)
    ),
    0.0
  ) AS `valor_devido`,
  IFNULL(
    CAST(
      DATE_FORMAT(
        GetDtPrimeiraCompra(`cliente`.`cod_cliente`),
        '%Y-%m-%d %H:%i:%s'
      ) AS CHAR charset utf8mb4
    ),
    'null'
  ) AS `dt_primeira_compra`,
  IFNULL(
    CAST(
      DATE_FORMAT(
        GetDtUltimaCompra(`cliente`.`cod_cliente`),
        '%Y-%m-%d %H:%i:%s'
      ) AS CHAR charset utf8mb4
    ),
    'null'
  ) AS `dt_ultima_compra`,
  IFNULL(
    CAST(
      GetStatusCliente(`cliente`.`cod_cliente`) AS CHAR charset utf8mb4
    ),
    'null'
  ) AS 'STATUS',
  IFNULL(
    CAST(
      YEAR(GetDtUltimaCompra(`cliente`.`cod_cliente`)) AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `ultimo_ano_ativo`,
  IFNULL(
    CAST(
      GetQtdTotalCompras(`cliente`.`cod_cliente`) AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `qtd_total_compras`,
  IFNULL(
    CAST(
      GetQtdComprasSemestre(`cliente`.`cod_cliente`) AS CHAR charset utf8mb4
    ),
    '0'
  ) AS `qtd_compras_semestre`,
  IFNULL(
    CAST(
      GetTotalComprasBimestre(`cliente`.`cod_cliente`) AS DECIMAL(10, 2)
    ),
    0.0
  ) AS `total_compras_bimestre`,
  IFNULL(
    CAST(
      GetTotalComprasTrimestre(`cliente`.`cod_cliente`) AS DECIMAL(10, 2)
    ),
    0.0
  ) AS `total_compras_trimestre`,
  IFNULL(
    CAST(
      GetTotalComprasSemestre(`cliente`.`cod_cliente`) AS DECIMAL(10, 2)
    ),
    0.0
  ) AS `total_compras_semestre`
FROM
  (
    (
      (
        (
          `cd_cliente` AS `cliente`
          LEFT JOIN `cd_cliente_endereco` AS `cliente_endereco` ON (
            `cliente_endereco`.`cod_cliente` = `cliente`.`cod_cliente`
          )
        )
        LEFT JOIN `cd_cliente_atividade` AS `cliente_atividade` ON (
          `cliente_atividade`.`cod_cliente` = `cliente`.`cod_cliente`
        )
      )
      LEFT JOIN `cd_ramo_atividade` AS `ramo_atividade` ON (
        `cliente_atividade`.`cod_ramo_atividade` = `ramo_atividade`.`cod_ramo_atividade`
      )
    )
  )
WHERE
  (
    `cliente`.`cod_cliente` IN (
      SELECT
        DISTINCTROW `nota_fiscal`.`cod_cliente`
      FROM
        `vd_nota_fiscal` AS `nota_fiscal`
      WHERE
        `nota_fiscal`.`dt_emissao` >= '2022-01-01'
        AND (
          `nota_fiscal`.`cod_empresa` IN (1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
        )
    )
  )
GROUP BY
  `cliente`.`cod_cliente`;