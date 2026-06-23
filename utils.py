"""Funções utilitárias de formatação, datas e status."""

import calendar
from datetime import date

def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_valor(txt):
    txt = str(txt).strip().replace("R$", "").replace(" ", "")
    if not txt:
        return 0.0
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None

def due_date_for_month(mes, dia):
    if dia is None:
        return None
    ano, mes_num = map(int, mes.split("-"))
    ultimo_dia = calendar.monthrange(ano, mes_num)[1]
    return date(ano, mes_num, min(dia, ultimo_dia))

def status_pagamento(mes, valor, status_lancamento, dia, tipo):
    venc = due_date_for_month(mes, dia)
    hoje = date.today()
    lancado = valor is not None
    vencido = bool(venc and venc < hoje)
    if not lancado:
        if tipo == "debito automatico":
            return "Débito automático"
        if vencido:
            return "⚠ Vencido sem lançamento"
        return "Não lançado"
    if status_lancamento == "Pago":
        return "Pago"
    if status_lancamento == "Débito automático":
        return "Débito automático"
    if vencido:
        return "⚠ Não pago vencido"
    return "Não pago"
