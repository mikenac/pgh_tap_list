from scripts.scrape import parse_hitchhiker_html


def test_parse_hitchhiker_html_extracts_beer_links() -> None:
    html = '''
    <a href="https://hitchhiker.beer/our-beers/bane-of-existence/">Bane of Existence</a>
    <a href="https://hitchhiker.beer/our-beers/true/">True</a>
    <a href="https://hitchhiker.beer/tap-rooms/">TAP ROOMS</a>
    '''
    items = parse_hitchhiker_html(html)
    names = [item["name"] for item in items]

    assert "Bane of Existence" in names
    assert "True" in names
    assert "TAP ROOMS" not in names
