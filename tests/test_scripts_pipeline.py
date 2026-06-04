from scripts.classify import classify_style
from scripts.compare import compare_entries
from scripts.scrape import normalize_name, parse_html_taplist, parse_pdf_menu_text


def test_name_normalization() -> None:
    assert normalize_name(" Double Lustra™ ") == "double lustra"
    assert normalize_name("You’ll Shoot Your Eye Out!!!") == "you'll shoot your eye out"


def test_style_classification() -> None:
    assert classify_style("Bohemian Pilsner") == "czech_lager"
    assert classify_style("Helles Lager") == "european_lager"
    assert classify_style("Fruited Sour") == "sour"
    assert classify_style("West Coast IPA") == "ipa"
    assert classify_style("Dry Stout") == "stout"


def test_addition_removal_and_style_changes() -> None:
    previous = [
        {
            "breweryId": "x",
            "normalizedName": "rice lager",
            "name": "Rice Lager",
            "style": "Lager",
            "untappdRating": 4.0,
            "active": True,
        },
        {
            "breweryId": "x",
            "normalizedName": "old",
            "name": "Old",
            "style": "IPA",
            "untappdRating": 3.7,
            "active": True,
        },
    ]
    current = [
        {
            "breweryId": "x",
            "normalizedName": "rice lager",
            "name": "Rice Lager",
            "style": "Japanese Rice Lager",
            "untappdRating": 4.3,
            "active": True,
        },
        {
            "breweryId": "x",
            "normalizedName": "new",
            "name": "New",
            "style": "Helles",
            "untappdRating": 3.9,
            "active": True,
        },
    ]
    result = compare_entries(previous, current, "x")

    assert result["additions"] == ["New"]
    assert result["removals"] == ["Old"]
    assert result["styleChanges"] == [
        {"beer": "Rice Lager", "oldStyle": "Lager", "newStyle": "Japanese Rice Lager"}
    ]
    assert result["ratingChanges"][0]["beer"] == "Rice Lager"


def test_script_compare_ignores_normalized_style_equivalents() -> None:
    previous = [
        {
            "breweryId": "x",
            "normalizedName": "not always present",
            "name": "Not Always Present",
            "style": "Kölsch Style Ale",
            "active": True,
        }
    ]
    current = [
        {
            "breweryId": "x",
            "normalizedName": "not always present",
            "name": "Not Always Present",
            "style": "Kölsch-style Ale",
            "active": True,
        }
    ]

    result = compare_entries(previous, current, "x")

    assert result["styleChanges"] == []


def test_parsing_sample_html_and_pdf_text() -> None:
    html = """
    <ul>
      <li>Ceremonials - Bohemian Pilsner - 5.2%</li>
      <li>House Sour - Fruited Sour - 6.0%</li>
    </ul>
    """
    parsed_html = parse_html_taplist(html)
    assert any(item["name"] == "Ceremonials" for item in parsed_html)

    pdf_text = """
    Ceremonials - Bohemian Pilsner - 5.2%
    Dark Mild - Mild - 4.1%
    House Pils - German Pils - 5.0%
    """
    parsed_pdf = parse_pdf_menu_text(pdf_text)
    assert any(item["name"] == "Ceremonials" for item in parsed_pdf)
    assert any(item["name"] == "House Pils" for item in parsed_pdf)
