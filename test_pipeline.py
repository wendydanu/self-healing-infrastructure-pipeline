import pytest
from server_math import calculate_invoice

pytestmark = pytest.mark.asyncio

async def test_invoice_success_without_discount():
    items = [{"price": 50000, "qty": 2}]
    assert calculate_invoice(items, 0.11) == 111000.0

async def test_invoice_success_with_discount():
    items = [{"price": 100000, "qty": 1}]
    assert calculate_invoice(items, 0.10, "SAVE10") == 99000.0

async def test_invoice_invalid_input_type():
    with pytest.raises(TypeError):
        calculate_invoice("not a list string", 0.11)