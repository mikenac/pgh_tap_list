import json

from scripts.scrape import (
    parse_abjuration_on_tap_html,
    parse_acclamation_json,
    parse_dancing_gnome_html,
    parse_four_points_html,
    parse_golden_age_html,
    parse_late_addition_html,
    parse_lolev_html,
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


def test_parse_late_addition_excludes_upcoming_section() -> None:
    html = """
    <main>
      <h2>OUR BEERS</h2>
      <div>
        <h3>Rotes Wien</h3>
        <p>Vienna-style lager</p>
        <p>5.2% ABV</p>
      </div>
      <p>UPCOMING</p>
      <div>
        <h3>Future Sour</h3>
        <p>Solera Sour Ale</p>
        <p>5.9% ABV</p>
      </div>
    </main>
    """

    items = parse_late_addition_html(html)

    assert [item["name"] for item in items] == ["Rotes Wien"]


def test_parse_lolev_html_uses_tap_availability() -> None:
    def script_record(payload: dict) -> str:
        escaped = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace('"', r'\"')
        return f'<script>self.__next_f.push([1,"{escaped}"])</script>'

    html = "".join(
        [
            script_record(
                {
                    "id": "1",
                    "variant": "lupula",
                    "name": "Lupula",
                    "type": "Hazy India Pale Ale",
                    "abv": 6.5,
                    "untappdRating": 4.08,
                    "availability": {
                        "cansAvailable": True,
                        "tap": "3",
                        "lawrenceville": {"tap": "1"},
                    },
                }
            ),
            script_record(
                {
                    "id": "2",
                    "variant": "dom",
                    "name": "Dom",
                    "type": "Kölsch",
                    "abv": 5,
                    "untappdRating": 3.8,
                    "availability": {"cansAvailable": False, "tap": "$undefined"},
                }
            ),
            script_record(
                {
                    "id": "3",
                    "variant": "costilla",
                    "name": "Costilla",
                    "type": "Mexican Dark Lager",
                    "abv": 4.8,
                    "untappdRating": 4.07,
                    "availability": {
                        "cansAvailable": False,
                        "tap": "$undefined",
                        "zelienople": {"tap": "2"},
                    },
                }
            ),
        ]
    )

    items = parse_lolev_html(html)

    assert [item["name"] for item in items] == ["Lupula", "Costilla"]
    assert items[0]["style"] == "Hazy India Pale Ale"
    assert items[0]["abv"] == "6.5%"
    assert items[0]["untappdRating"] == 4.08


def test_parse_acclamation_json_filters_to_beer_taps() -> None:
    payload = {
        "data": {
            "productsList": [
                {
                    "name": "Steel City Lager",
                    "description": "American Light Lager (Galena) - 4.5%",
                    "available": True,
                },
                {
                    "name": "Old Thunder Sol X",
                    "description": "Guest Tap: Dark Mexican Lager - 5.0%",
                    "available": True,
                },
                {
                    "name": "Two Frays Non-Alcoholic Beer",
                    "description": "Fruited Blonde Ale OR West Coast IPA (less than 0.5% abv)",
                    "available": True,
                },
                {
                    "name": "Oh Yeah! Grape",
                    "description": "GF Hard Seltzer - 5.0%",
                    "available": True,
                },
                {
                    "name": "Jackworth N/A Ginger Beer",
                    "description": "Non-Alcoholic - 0.0%",
                    "available": True,
                },
                {
                    "name": "Unavailable IPA",
                    "description": "IPA - 6.0%",
                    "available": False,
                },
            ]
        }
    }

    items = parse_acclamation_json(json.dumps(payload))

    assert [item["name"] for item in items] == [
        "Steel City Lager",
        "Old Thunder Sol X",
        "Two Frays Non-Alcoholic Beer",
    ]
    assert items[0]["style"] == "American Light Lager (Galena)"
    assert items[0]["abv"] == "4.5%"
    assert items[1]["style"] == "Dark Mexican Lager"
    assert items[2]["style"] == "Fruited Blonde Ale OR West Coast IPA"
    assert items[2]["abv"] == "0.5%"
