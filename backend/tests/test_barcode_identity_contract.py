"""Barcode identity contract: scanning is not the same as catalogue matching.

Keep all GS1 leading zeroes. Reject arbitrary QR text and invalid check digits
before issuing any product lookup or optional external API request.
"""

import pytest

from app.barcodes import gtin_aliases, validate_gtin


@pytest.mark.parametrize(
    "code",
    [
        "96385074",       # GTIN-8
        "036000291452",   # UPC-A / GTIN-12
        "4006381333931",  # EAN-13 / GTIN-13
        "04006381333931", # GTIN-14 representation
    ],
)
def test_valid_gtin_preserves_exact_digits(code):
    assert validate_gtin(code) == code
    assert code in gtin_aliases(code)


@pytest.mark.parametrize(
    "code",
    [
        "", "123", "4006381333932", "036000291453",
        "4006381333931 ", " 4006381333931", "٤٠٠٦٣٨١٣٣٣٩٣١",
        "https://example.org/12345678", "000000000000000",
        None, 4006381333931,
    ],
)
def test_invalid_or_non_gs1_input_is_rejected(code):
    with pytest.raises(ValueError):
        validate_gtin(code)


def test_upc_and_ean_zero_padded_representations_are_equivalent():
    aliases = gtin_aliases("036000291452")
    assert {"036000291452", "0036000291452", "00036000291452"} <= aliases
    assert gtin_aliases("0036000291452") == aliases


def test_unrelated_gtins_do_not_share_aliases():
    assert gtin_aliases("4006381333931").isdisjoint(gtin_aliases("036000291452"))
