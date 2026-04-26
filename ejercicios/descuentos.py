# descuentos.py

def calcular_descuento(precio, porcentaje):
    """Calcula el precio con descuento basado en un porcentaje de reducción.

    Args:
        precio (float): Precio original del producto.
        porcentaje (float): Porcentaje de descuento a aplicar.

    Returns:
        float: Precio final con descuento aplicado.
    """
    descuento = precio * (porcentaje / 100)
    return precio - descuento

total = calcular_descuento(100, 20)
print(f"Total con descuento: ${total:.2f}")
