from taplist_tracker.config import BREWERY_SOURCES, HITCHHIKER_BASELINE


def test_expected_brewery_configs_exist() -> None:
    expected_ids = {
        "grist-house",
        "dancing-gnome",
        "four-points",
        "late-addition",
        "hitchhiker",
        "old-thunder",
        "abjuration",
        "golden-age",
    }
    assert set(BREWERY_SOURCES.keys()) == expected_ids


def test_hitchhiker_baseline_loaded() -> None:
    cfg = BREWERY_SOURCES["hitchhiker"]
    assert cfg.baseline_names == HITCHHIKER_BASELINE
    assert "People-Watching" in cfg.baseline_names


def test_grist_house_untappd_authoritative() -> None:
    cfg = BREWERY_SOURCES["grist-house"]
    assert cfg.untappd_authoritative is True
    assert cfg.source_priority[0] == "untappd"
