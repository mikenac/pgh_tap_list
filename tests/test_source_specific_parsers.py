from scripts.scrape import (
    parse_abjuration_on_tap_html,
    parse_dancing_gnome_html,
    parse_four_points_html,
    parse_golden_age_html,
)


def test_parse_dancing_gnome_html() -> None:
    html = '''
    <div class="module--untappd-wot">
      <div class="list-item">
        <h2 class="item-title">Lustra</h2>
        <div class="item-descriptor">IPA - Citra, Mosaic</div>
      </div>
      <div class="list-item">
        <h2 class="item-title">Pilsner</h2>
        <div class="item-descriptor">German Pilsner</div>
      </div>
    </div>
    <a title="Wit – 5%">Wit – 5%</a>
    '''
    items = parse_dancing_gnome_html(html)
    names = [item["name"] for item in items]
    assert "Lustra" in names
    assert "Pilsner" in names
    assert "Wit" in names


def test_parse_golden_age_html() -> None:
    html = '''
    <div class="menu-item">
      <div class="menu-item-title">German Lager</div>
      <div class="menu-item-description">
        Classic German Pilsner brewed with Hallertau hops. 5.1%
      </div>
    </div>
    '''
    items = parse_golden_age_html(html)
    assert items[0]["name"] == "German Lager"
    assert items[0]["style"].startswith("Classic German Pilsner")
    assert items[0]["abv"] == "5.1%"


def test_parse_four_points_html() -> None:
    html = '''
    <p><strong>DESTROYER PILS</strong><br><em>*LUKR</em>
    <em>west coast pilsner</em> | <strong>5.0%</strong>
    <br><strong>$5.5 | 7 | 26</strong></p>
    <p><strong>MOJITO</strong><br><em>goodlander draft cocktail</em> |
    <strong>10.5%</strong></p>
    '''
    items = parse_four_points_html(html)
    assert items[0]["name"] == "DESTROYER PILS"
    assert items[0]["style"] == "west coast pilsner"
    assert items[0]["abv"] == "5.0%"
    assert all("cocktail" not in (item["style"] or "") for item in items)


def test_parse_abjuration_on_tap_html() -> None:
    html = '''
    <div class="feed-element">
      <a href="/Beer/112?v=2.0" class="ontapbeer">
        <strong>Fruited India Pale Ale [Grapefruit] (FRIPA v2.0)</strong>
      </a>
    </div>
    <div class="feed-element">
      <a href="/Beer/82?v=1.32" class="ontapbeer">
        <strong>Fruited Sour [Pineapple/Honeydew] (FS v1.32)</strong>
      </a>
    </div>
    '''

    items = parse_abjuration_on_tap_html(html)

    assert [item["name"] for item in items] == [
        "Fruited India Pale Ale [Grapefruit] (FRIPA v2.0)",
        "Fruited Sour [Pineapple/Honeydew] (FS v1.32)",
    ]
    assert [item["style"] for item in items] == ["Fruited India Pale Ale", "Fruited Sour"]
