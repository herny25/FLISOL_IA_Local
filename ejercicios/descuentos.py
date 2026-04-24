# descuentos.py

def calcular_descuento(precio, porcentaje):
    """
    Calcula el precio con un descuento aplicado.

    Args:
        precio (float): El precio original.
        porcentaje (float): El porcentaje de descuento a aplicar.

    Returns:
        float: El precio con el descuento aplicado.
    """
    descuento = precio * (porcentaje / 100)
    return precio - descuento

total = calcular_descuento(100, 20)
print(f"Total con descuento: ${total:.2f}")
