from openscreener import Screener, Stock


def test_filter_applies_thresholds() -> None:
    screener = Screener(
        [
            Stock(symbol="AAA", price=120.0, volume=2_500_000, pe_ratio=18.4),
            Stock(symbol="BBB", price=45.0, volume=900_000, pe_ratio=31.2),
            Stock(symbol="CCC", price=82.0, volume=1_500_000, pe_ratio=22.1),
        ]
    )

    results = screener.filter(
        min_price=50.0,
        min_volume=1_000_000,
        max_pe_ratio=25.0,
    )

    assert [stock.symbol for stock in results] == ["AAA", "CCC"]


def test_add_stock_updates_universe() -> None:
    screener = Screener()
    screener.add_stock(Stock(symbol="XYZ", price=75.0, volume=2_000_000))

    results = screener.filter(min_price=70.0, min_volume=1_000_000)

    assert [stock.symbol for stock in results] == ["XYZ"]
