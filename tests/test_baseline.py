from backend.model.baseline import load_baseline

M = load_baseline()


def test_rate_z_extreme_for_thousand_per_hour() -> None:
    assert M.rate_z("component_manufacture", 1000.0) > M.thresholds["rate_z_hard"]


def test_rate_z_low_for_normal() -> None:
    assert M.rate_z("component_manufacture", 65.0) < 1.0


def test_known_country_true_for_home_country() -> None:
    supplier = next(iter(M.supplier_country))
    home = max(M.supplier_country[supplier], key=M.supplier_country[supplier].get)
    assert M.is_known_country(supplier, home) is True


def test_valid_time_whitelist() -> None:
    assert M.is_valid_time("raw_material_supply", "09:00:00Z") is True
    assert M.is_valid_time("final_integration", "04:03:21Z") is False
