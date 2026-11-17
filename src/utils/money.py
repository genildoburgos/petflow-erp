from decimal import Decimal, ROUND_HALF_UP

def to_decimal(val) -> Decimal:
    """
    Converte com segurança qualquer valor numérico ou string para Decimal.
    Evita perda de precisão associada a números de ponto flutuante (float).
    """
    if val is None:
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val
    if isinstance(val, (int, str)):
        return Decimal(str(val))
    if isinstance(val, float):
        return Decimal(f"{val:.4f}")
    return Decimal(str(val))

def round_money(val) -> Decimal:
    """
    Arredonda um valor monetário para exatamente duas casas decimais
    usando o padrão bancário/comercial ROUND_HALF_UP.
    """
    return to_decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
