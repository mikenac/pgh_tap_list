from taplist_tracker.normalize import (
    has_untappd_embed,
    normalize_beer_name,
    normalize_style,
    parse_abv,
)


def test_normalize_beer_name_rules() -> None:
    assert normalize_beer_name(" Double Lustra™ ") == "double lustra"
    assert normalize_beer_name("You'll Shoot Your Eye Out!!!") == "you'll shoot your eye out"
    assert normalize_beer_name("YoRazberry   ") == "yorazberry"


def test_parse_abv() -> None:
    assert parse_abv("6.7% ABV") == 6.7
    assert parse_abv(5) == 5.0
    assert parse_abv(None) is None
    assert parse_abv("No ABV") is None


def test_normalize_style_ignores_presentation_drift() -> None:
    assert normalize_style("Kölsch Style Ale") == "kolsch style ale"
    assert normalize_style("Kölsch-style Ale") == "kolsch style ale"
    assert normalize_style("  German   Pils – Lager ") == "german pils lager"
    assert normalize_style(None) is None


def test_untappd_embed_detection() -> None:
    html = '<iframe src="https://business.untappd.com/widgets/iframer"></iframe>'
    assert has_untappd_embed(html)
    assert not has_untappd_embed("<div>no embeds</div>")
