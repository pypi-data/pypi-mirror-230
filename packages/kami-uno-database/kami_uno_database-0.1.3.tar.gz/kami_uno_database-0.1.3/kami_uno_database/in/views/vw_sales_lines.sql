-- db_uc_kami.vw_sales_lines source
USE db_uc_kami;
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `vw_sales_lines` AS
SELECT  
  IFNULL(CAST(YEAR(`pedido`.`dt_implant`) AS CHAR charset utf8mb4),'0') AS `ano`,
  IFNULL(CAST(MONTH(`pedido`.`dt_implant`) AS CHAR charset utf8mb4),'0') AS `mes`,
  IFNULL(CAST(`pedido`.`cod_empresa` AS CHAR charset utf8mb4),'0') AS `empresa_pedido`,
  IFNULL(CAST(`nota_fiscal_2`.`cod_empresa` AS CHAR charset utf8mb4),'0') AS `empresa_nota_fiscal`,
  IFNULL(CAST(`pedido`.`cod_cliente` AS CHAR charset utf8mb4),'0') AS `cod_cliente`,
  IFNULL(CAST(`pedido`.`cod_colaborador` AS CHAR charset utf8mb4),'0') AS `cod_colaborador`,
  IFNULL(CAST(`colaborador`.`nome_colaborador` AS CHAR charset utf8mb4),'0') AS `nome_colaborador`,
  IFNULL(CAST(`grupo_venda`.`nome_grupo` AS CHAR charset utf8mb4), '0') AS `equipe`,
  IFNULL(CAST(`pedido`.`cod_pedido` AS CHAR charset utf8mb4),'0') AS `cod_pedido`,
  IFNULL(CAST(
    IFNULL(
      `pedido`.`nr_ped_compra_cli`,
      `pedido`.`cod_pedido_pda`
    ) AS CHAR charset utf8mb4),'0')
  AS `nr_ped_compra_cli`,
  IFNULL(CAST(`pedido`.`situacao` AS CHAR charset utf8mb4),'0') AS `cod_situacao`,
  IFNULL(CAST(`ponto_controle`.`descricao` AS CHAR charset utf8mb4),'0') AS `desc_situacao`,
  IFNULL(CAST(`pedido`.`nop` AS CHAR charset utf8mb4),'0') AS `nop`,
  IFNULL(CAST(`nota_fiscal_2`.`desc_abrev_cfop` AS CHAR charset utf8mb4),'0') AS `cfop`,
  IFNULL(CAST(`pedido`.`cod_cond_pagto` AS CHAR charset utf8mb4),'0') AS `cod_cond_pagto`,
  IFNULL(CAST(`pedido_pgto`.`cod_forma_pagto` AS CHAR charset utf8mb4),'0') AS `cod_forma_pagto`,
  IFNULL(CAST(`forma_pagto`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `forma_pagto`,
  IFNULL(CAST(`pedido_item`.`cod_produto` AS CHAR charset utf8mb4),'0') AS `cod_produto`,
  IFNULL(CAST(`pedido_item`.`desc_comercial` AS CHAR charset utf8mb4),'0') AS `desc_produto`,
  IFNULL(CAST(`grupo_item`.`cod_grupo_produto` AS CHAR charset utf8mb4),'0') AS `cod_grupo_produto`,
  IFNULL(CAST(`grupo_produto`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `desc_grupo_produto`,
  IFNULL(CAST(`grupo_produto`.`cod_grupo_pai` AS CHAR charset utf8mb4),'0') AS `cod_grupo_pai`,
  IFNULL(CAST(`grupo_produto_pai`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `desc_grupo_pai`,
  IFNULL(CAST(`marca`.`cod_marca` AS CHAR charset utf8mb4),'0') AS `cod_marca`,
  IFNULL(CAST(`marca`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `desc_marca`,
  IFNULL(CAST(`produto_empresa`.`vl_custo_total` AS DECIMAL(10,2)), 0.0) AS `custo_total`,
  IFNULL(CAST(
    IFNULL(
      `produto_empresa`.`vl_custo_kami`,
      (
      SELECT cpi.preco_unit
      FROM cd_preco_item AS cpi
      WHERE cpi.cod_produto = `pedido_item`.`cod_produto`
      AND cpi.tb_preco = 'TabTbCusto'
      )
    ) AS DECIMAL(10, 2)), 0.0)
  AS `custo_kami`,
  IFNULL(CAST(`pedido_item`.`tb_preco` AS CHAR charset utf8mb4),'0') AS `tb_preco`,
  IFNULL(CAST(`pedido_item`.`qtd` AS DECIMAL(10,2)), 0.0) AS `qtd`,
  IFNULL(CAST(`pedido_item`.`preco_venda` AS DECIMAL(10,2)), 0.0) AS `preco_unit_original`,
  IFNULL(CAST(
    (`pedido_item`.`qtd` * `pedido_item`.`preco_venda`) AS DECIMAL(10,2)), 0.0)
  AS `preco_total_original`,
  IFNULL(CAST((
    ((`pedido_item`.`preco_venda` / `produto_empresa`.`vl_custo_total`)*100)-100
    ) AS DECIMAL(10,2)), 0.0)
  AS `margem_bruta`,
  IFNULL(CAST(`pedido_item`.`preco_total` AS DECIMAL(10,2)), 0.0) AS `preco_total`,
  IFNULL(CAST((
    `pedido_item`.`preco_total`
    -(`pedido_item`.`preco_total`/`pedido`.`vl_total_produtos`)
    *COALESCE(`pedido`.`vl_desconto`,0)
    ) AS DECIMAL(10,2)), 0.0)
  AS `preco_desconto_rateado`,
  IFNULL(CAST(`pedido`.`vl_total_produtos` AS DECIMAL(10,2)), 0.0) AS `vl_total_pedido`,
  IFNULL(CAST((`pedido`.`vl_desconto` * -1) AS DECIMAL(10,2)), 0.0) AS `desconto_pedido`,
  IFNULL(CAST((
    CASE
      WHEN `nota_fiscal`.`vl_total_nota_fiscal` > 0
      THEN `nota_fiscal`.`vl_total_nota_fiscal`
      ELSE `nota_fiscal_2`.`vl_total_nota_fiscal`
    END
    ) AS DECIMAL(10,2)), 0.0)
  AS `valor_nota`,
  IFNULL(CAST(((
    CASE
      WHEN `nota_fiscal`.`vl_total_nota_fiscal` > 0
      THEN `nota_fiscal`.`vl_total_nota_fiscal`
      ELSE `nota_fiscal_2`.`vl_total_nota_fiscal`
    END)
    + `pedido`.`vl_desconto`
    ) AS DECIMAL(10,2)), 0.0)
  AS `total_bruto`,
  IFNULL(CAST(
    DATE_FORMAT(`pedido`.`dt_implant`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_implante_pedido`,
  IFNULL(CAST(
    DATE_FORMAT(`pedido`.`dt_entrega_comprometida`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_entrega_comprometida`,
  IFNULL(CAST(
    DATE_FORMAT((
      CASE
        WHEN `nota_fiscal`.`dt_emissao` > 0
        THEN `nota_fiscal`.`dt_emissao`
        ELSE `nota_fiscal_2`.`dt_emissao`
      END),
      '%Y-%m-%d %H:%i:%s'
    ) AS CHAR charset utf8mb4), 'null')
  AS `dt_faturamento`  
FROM ((((((((((((((((
  `vd_pedido_item` AS `pedido_item`
LEFT JOIN `vd_pedido` AS `pedido` 
  ON (`pedido`.`cod_pedido` = `pedido_item`.`cod_pedido`) 
  AND (`pedido`.`cod_empresa` = `pedido_item`.`cod_empresa`))
LEFT JOIN `sg_colaborador` AS `colaborador` 
  ON (`colaborador`.`cod_colaborador` = `pedido`.`cod_colaborador`))
LEFT JOIN `cd_cond_pagto` AS `cond_pgto` 
  ON (`cond_pgto`.`cod_cond_pagto` = `pedido`.`cod_cond_pagto`))
LEFT JOIN `vd_ponto_controle` AS `ponto_controle` 
  ON (`ponto_controle`.`cod_controle` = `pedido`.`situacao`))
LEFT JOIN `vd_pedido_pagto` AS `pedido_pgto` 
  ON (`pedido_pgto`.`cod_pedido` = `pedido`.`cod_pedido` ))
LEFT JOIN `cd_forma_pagto` AS `forma_pagto` 
  ON (`pedido_pgto`.`cod_forma_pagto` = `forma_pagto`.`cod_forma_pagto`))
LEFT JOIN `vd_nota_fiscal` AS `nota_fiscal` 
  ON (`nota_fiscal`.`cod_pedido` = `pedido`.`cod_pedido`)
  AND (`nota_fiscal`.`situacao` < 86)
  AND (`nota_fiscal`.`situacao` > 79)
  AND (`pedido`.`cod_empresa` = `nota_fiscal`.`cod_empresa`))
LEFT JOIN `vd_nota_fiscal` AS `nota_fiscal_2` 
  ON (`nota_fiscal_2`.`cod_pedido` = `pedido`.`cod_pedido`)
  AND (`nota_fiscal_2`.`situacao` < 86)
  AND (`nota_fiscal_2`.`situacao` > 79))
LEFT JOIN `cd_produto_empresa` AS `produto_empresa` 
  ON (`pedido_item`.`cod_produto` = `produto_empresa`.`cod_produto`)
  AND (`pedido`.`cod_empresa` = `produto_empresa`.`cod_empresa`))
LEFT JOIN `cd_produto` AS `produto` 
  ON (`produto`.`cod_produto` = `pedido_item`.`cod_produto`))
LEFT JOIN `cd_marca` AS `marca` 
  ON (`marca`.`cod_marca` = `produto`.`cod_marca`))
LEFT JOIN `cd_grupo_item` AS `grupo_item` 
  ON (`grupo_item`.`cod_produto` = `pedido_item`.`cod_produto`))
LEFT JOIN `cd_grupo_produto` AS `grupo_produto` 
  ON (`grupo_produto`.`cod_grupo_produto` = `grupo_item`.`cod_grupo_produto`))
LEFT JOIN `cd_grupo_produto` AS `grupo_produto_pai` 
  ON (`grupo_produto_pai`.`cod_grupo_produto` = `grupo_produto`.`cod_grupo_pai`))
LEFT JOIN `vd_grupo_colaborador` AS `grupo_colaborador`
  ON (`grupo_colaborador`.`cod_colaborador` = `colaborador`.`cod_colaborador`)
  AND (`grupo_colaborador`.`cod_empresa` = `pedido`.`cod_empresa`))
LEFT JOIN `vd_grupo` AS `grupo_venda`
  ON (`grupo_venda`.`cod_grupo_venda` = `grupo_colaborador`.`cod_grupo_venda`)
)
WHERE `pedido`.`dt_implant` >= "2022-01-01"
AND `pedido`.`cod_empresa` IN (1,2,3,4,5,6,9,10,11,12,13,14,15,16)
GROUP BY ano, mes, `pedido`.`cod_pedido`, `pedido`.`cod_cliente`, `pedido_item`.`cod_produto`;