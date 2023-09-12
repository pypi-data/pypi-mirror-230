# -*- coding: utf-8 -*-
import numpy as np

BILLINGS_DATETIME_COLS = [
    'dt_implante_pedido',
    'dt_entrega_comprometida',
    'dt_faturamento',
]
BOARD_BILLINGS_NUM_COLS = {
    'ano': np.int64,
    'mes': np.int64,
    'cod_empresa_pedido': np.int64,
    'cod_pedido': np.int64,
    'cod_cliente': np.int64,
    'situacao_pedido': np.int64,
    'cod_colaborador': np.int64,
    'qtd': np.int64,
    'custo_total': np.float64,
    'custo_kami': np.float64,
    'preco_unit_original': np.float64,
    'preco_total_original': np.float64,
    'margem_bruta': np.float64,
    'preco_total': np.float64,
    'preco_desconto_rateado': np.float64,
    'vl_total_pedido': np.float64,
    'desconto_pedido': np.float64,
    'valor_nota': np.float64,
    'situacao_entrega': np.int64,
    'cod_empresa_faturamento': np.int64,
}
CUSTOMER_DETAILS_DATETIME_COLS = [
    'dt_cadastro',
    'dt_primeira_compra',
    'dt_ultima_compra',
]
CUSTOMER_DETAILS_NUM_COLS = {
    'cod_cliente': np.int64,
    'dias_atraso': np.int64,
    'valor_devido': np.float64,
    'ultimo_ano_ativo': np.int64,
    'qtd_total_compras': np.int64,
    'qtd_compras_semestre': np.int64,
    'total_compras_semestre': np.float64,
    'total_compras_trimestre': np.float64,
    'total_compras_bimestre': np.float64,
}
FUTURE_BILLS_DATETIME_COLS = ['dt_vencimento']
FUTURE_BILLS_NUM_COLS = {
    'cod_empresa': np.int64,
    'total_a_receber': np.float64,
}
ORDER_ITEM_DATE_COLS = [
    'data_entrega',
    'dt_entrega',
    'dt_implant',
    'dt_impressao_etiqueta',
    'dt_pre_separacao',
    'dt_prev_treinamento',
    'dt_prevista',
    'dt_reserva_estoque',
    'dt_retorno',
]
SALES_LINES_NUM_COLS = {
    'ano': np.int64,
    'mes': np.int64,
    'empresa_pedido': np.int64,
    'empresa_nota_fiscal': np.int64,
    'cod_cliente': np.int64,
    'cod_colaborador': np.int64,
    'cod_pedido': np.int64,
    'cod_situacao': np.int64,
    'cod_grupo_produto': np.int64,
    'cod_grupo_pai': np.int64,
    'cod_marca': np.int64,
    'custo_total': np.float64,
    'custo_kami': np.float64,
    'qtd': np.float64,
    'preco_unit_original': np.float64,
    'preco_total_original': np.float64,
    'margem_bruta': np.float64,
    'preco_total': np.float64,
    'preco_desconto_rateado': np.float64,
    'vl_total_pedido': np.float64,
    'desconto_pedido': np.float64,
    'valor_nota': np.float64,
    'total_bruto': np.float64,
}
