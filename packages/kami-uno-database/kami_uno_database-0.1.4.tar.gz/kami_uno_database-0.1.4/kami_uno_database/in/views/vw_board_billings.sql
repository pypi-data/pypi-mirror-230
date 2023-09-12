-- db_uc_kami.vw_board_billings source
USE db_uc_kami;
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `vw_board_billings` AS
SELECT
  IFNULL(CAST(YEAR(`pedido`.`dt_implant`) AS CHAR charset utf8mb4),'0') AS `ano`,
  IFNULL(CAST(MONTH(`pedido`.`dt_implant`) AS CHAR charset utf8mb4),'0') AS `mes`,
  IFNULL(CAST(`pedido`.`cod_empresa` AS CHAR charset utf8mb4),'0') AS `cod_empresa_pedido`,
  IFNULL(CAST(`empresa_pedido`.`razao_social` AS CHAR charset utf8mb4),'0') AS `nome_empresa_pedido`,
  IFNULL(CAST(`empresa_pedido`.`sigla_uf` AS CHAR charset utf8mb4),'0') AS `uf_empresa_pedido`,
  IFNULL(CAST(`pedido`.`cod_pedido` AS CHAR charset utf8mb4),'0') AS `cod_pedido`,
  IFNULL(CAST(`pedido`.`cod_cliente` AS CHAR charset utf8mb4),'0') AS `cod_cliente`,
  IFNULL(CAST(`pedido`.`nome_cliente` AS CHAR charset utf8mb4),'0') AS `nome_cliente`,
  IFNULL(CAST(`cliente_endereco`.`sigla_uf` AS CHAR charset utf8mb4),'0') AS `uf_cliente`,
  IFNULL(CAST(IFNULL(`pedido`.`nr_ped_compra_cli`,`pedido`.`cod_pedido_pda`) AS CHAR charset utf8mb4),'0') AS `nr_ped_compra_cli`,
  IFNULL(CAST(`pedido`.`situacao` AS CHAR charset utf8mb4),'0') AS `situacao_pedido`,
  IFNULL(CAST(`pedido`.`nop` AS CHAR charset utf8mb4),'0') AS `nop`,
  IFNULL(CAST(`nota_fiscal`.`desc_abrev_cfop` AS CHAR charset utf8mb4),'0') AS `desc_abrev_cfop`,
  IFNULL(CAST(`ramo_atividade`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `desc_abreviada`,
  IFNULL(CAST(`pedido`.`cod_colaborador` AS CHAR charset utf8mb4),'0') AS `cod_colaborador`,
  IFNULL(CAST(`colaborador`.`nome_colaborador` AS CHAR charset utf8mb4),'0') AS `nome_colaborador`,
  IFNULL(CAST(`pedido`.`cod_cond_pagto` AS CHAR charset utf8mb4),'0') AS `cod_cond_pagto`,
  IFNULL(CAST(`pedido_pagto`.`cod_forma_pagto` AS CHAR charset utf8mb4),'0') AS `cod_forma_pagto`,
  IFNULL(CAST(`forma_pagto`.`desc_abrev` AS CHAR charset utf8mb4),'0') AS `desc_abrev`,
  IFNULL(CAST(`pedido_item`.`cod_produto` AS CHAR charset utf8mb4),'0') AS `cod_produto`,
  IFNULL(CAST(`pedido_item`.`desc_comercial` AS CHAR charset utf8mb4),'0') AS `desc_comercial`,
  IFNULL(CAST(ROUND(`pedido_item`.`qtd`,0) AS CHAR charset utf8mb4),'0') AS `qtd`,
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
  IFNULL(CAST(`pedido_item`.`tb_preco` AS CHAR charset utf8mb4), '0') AS `tb_preco`,
  IFNULL(CAST(`pedido_item`.`preco_venda` AS DECIMAL(10, 2)), 0.0) AS `preco_unit_original`,
  IFNULL(CAST(
    (`pedido_item`.`qtd` * `pedido_item`.`preco_venda`) AS DECIMAL(10,2)), 0.0)
  AS `preco_total_original`,
  IFNULL(CAST((
    ((`pedido_item`.`preco_venda` / `produto_empresa`.`vl_custo_total`)*100)-100
    ) AS DECIMAL(10,2)), 0.0)
  AS `margem_bruta`,
  IFNULL(CAST(`pedido_item`.`preco_total` AS DECIMAL(10, 2)), 0.0) AS `preco_total`,
    IFNULL(CAST((
    `pedido_item`.`preco_total`
    -(`pedido_item`.`preco_total`/`pedido`.`vl_total_produtos`)
    *COALESCE(`pedido`.`vl_desconto`,0)
    ) AS DECIMAL(10,2)), 0.0)
  AS `preco_desconto_rateado`,
  IFNULL(CAST(`pedido`.`vl_total_produtos` AS DECIMAL(10, 2)), 0.0) AS `vl_total_pedido`,
  IFNULL(CAST((`pedido`.`vl_desconto` * -1) AS DECIMAL(10, 2)), 0.0) AS `desconto_pedido`,
  IFNULL(CAST(`nota_fiscal`.`vl_total_nota_fiscal` AS DECIMAL(10, 2)), 0.0) AS `valor_nota`,
  IFNULL(CAST(
    DATE_FORMAT(`pedido`.`dt_implant`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_implante_pedido`,
  IFNULL(CAST(
    DATE_FORMAT(`pedido`.`dt_entrega_comprometida`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_entrega_comprometida`,
  IFNULL(CAST(`pedido`.`situacao` AS CHAR charset utf8mb4), '0') AS `situacao_entrega`,
  IFNULL(CAST(`ponto_controle`.`descricao` AS CHAR charset utf8mb4), '0') AS `descricao`,
    IFNULL(CAST(
    DATE_FORMAT(`nota_fiscal`.`dt_emissao`, '%Y-%m-%d %H:%i:%s')
    AS CHAR charset utf8mb4), 'null')
  AS `dt_faturamento`,
  IFNULL(CAST(`marca`.`desc_abrev` AS CHAR charset utf8mb4), '0') AS `marca`,
  IFNULL(CAST(
    `nota_fiscal`.`cod_empresa`
    AS CHAR charset utf8mb4), '0')
  AS `cod_empresa_faturamento`,
  IFNULL(CAST(
    `empresa_faturamento`.`razao_social`
    AS CHAR charset utf8mb4), '0')
  AS `nome_empresa_faturamento`,
  IFNULL(CAST(
    `empresa_faturamento`.`sigla_uf`
    AS CHAR charset utf8mb4), '0')
  AS `uf_empresa_faturamento`,    
  IFNULL(CAST(`grupo_venda`.`nome_grupo` AS CHAR charset utf8mb4), '0') AS `equipe`
FROM ((((((((((((((((((
  `vd_pedido` AS `pedido`
LEFT JOIN `sg_colaborador` AS `colaborador` 
  ON (`colaborador`.`cod_colaborador` = `pedido`.`cod_colaborador`))
LEFT JOIN `cd_cond_pagto` AS `cond_pagto` 
  ON (`cond_pagto`.`cod_cond_pagto` = `pedido`.`cod_cond_pagto`))
LEFT JOIN `vd_ponto_controle` AS `ponto_controle` 
  ON (`ponto_controle`.`cod_controle` = `pedido`.`situacao`))
LEFT JOIN `vd_pedido_pagto` AS `pedido_pagto` 
  ON (`pedido_pagto`.`cod_pedido` = `pedido`.`cod_pedido` ))
LEFT JOIN `cd_forma_pagto` AS `forma_pagto` 
  ON (`pedido_pagto`.`cod_forma_pagto` = `forma_pagto`.`cod_forma_pagto`))
LEFT JOIN `cd_cliente_atividade` AS `cliente_atividade` 
  ON (`cliente_atividade`.`cod_cliente` = `pedido`.`cod_cliente`))
LEFT JOIN `cd_ramo_atividade` AS `ramo_atividade` 
  ON (`cliente_atividade`.`cod_ramo_atividade` = `ramo_atividade`.`cod_ramo_atividade`))
LEFT JOIN `vd_nota_fiscal` AS `nota_fiscal` 
  ON (`nota_fiscal`.`cod_pedido` = `pedido`.`cod_pedido`)
  AND (`nota_fiscal`.`situacao` < 86)
  AND (`nota_fiscal`.`situacao` > 79))
LEFT JOIN `vd_pedido_item` AS `pedido_item` 
  ON (`pedido`.`cod_pedido` = `pedido_item`.`cod_pedido`)
  AND (`pedido`.`cod_empresa` = `pedido_item`.`cod_empresa`))
LEFT JOIN `cd_produto_empresa` AS `produto_empresa` 
  ON (`pedido_item`.`cod_produto` = `produto_empresa`.`cod_produto`)
  AND (`pedido`.`cod_empresa` = `produto_empresa`.`cod_empresa`))
LEFT JOIN `cd_produto` AS `produto` 
  ON (`produto`.`cod_produto` = `pedido_item`.`cod_produto`))
LEFT JOIN `cd_marca` AS `marca` 
  ON (`marca`.`cod_marca` = `produto`.`cod_marca`))
LEFT JOIN `cd_cliente_endereco` AS `cliente_endereco` 
  ON (`cliente_endereco`.`cod_cliente` = `pedido`.`cod_cliente`))
LEFT JOIN `cd_empresa` AS `empresa_pedido` 
  ON (`empresa_pedido`.`cod_empresa` = `pedido`.`cod_empresa`))
LEFT JOIN `cd_empresa` AS `empresa_faturamento` 
  ON (`empresa_faturamento`.`cod_empresa` = `nota_fiscal`.`cod_empresa`))
LEFT JOIN `vd_grupo_colaborador` AS `grupo_colaborador`
  ON (`grupo_colaborador`.`cod_colaborador` = `colaborador`.`cod_colaborador`)
  AND (`grupo_colaborador`.`cod_empresa` = `pedido`.`cod_empresa`))
LEFT JOIN `vd_grupo` AS `grupo_venda`
  ON (`grupo_venda`.`cod_grupo_venda` = `grupo_colaborador`.`cod_grupo_venda`))
)
WHERE `pedido`.`dt_implant` >= "2022-01-01"
AND `pedido`.`cod_empresa` IN (1,2,3,4,5,6,9,10,11,12,13,14,15,16)
AND `pedido`.`situacao` < 200
GROUP BY ano ,mes ,`pedido`.`cod_pedido` ,`pedido`.`cod_cliente` ,`pedido_item`.`cod_produto`;