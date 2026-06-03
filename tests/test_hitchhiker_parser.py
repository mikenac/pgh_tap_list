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


def test_parse_hitchhiker_html_extracts_portfolio_styles() -> None:
    html = '''
    <article>
      <a href="https://hitchhiker.beer/our-beers/citrus-summer/" aria-label="Citrus Summer"></a>
      <h2 class="entry-title fusion-post-title">
        <a href="https://hitchhiker.beer/our-beers/citrus-summer/">Citrus Summer</a>
      </h2>
      <div class="fusion-post-content"><p>Lemon Wheat Ale</p></div>
    </article>
    <article>
      <a href="https://hitchhiker.beer/our-beers/true/" aria-label="True"></a>
      <h2 class="entry-title fusion-post-title">
        <a href="https://hitchhiker.beer/our-beers/true/">True</a>
      </h2>
      <div class="fusion-post-content"><p>Pilsner</p></div>
    </article>
    '''

    items = parse_hitchhiker_html(html)

    assert items == [
        {"name": "Citrus Summer", "style": "Lemon Wheat Ale", "abv": None},
        {"name": "True", "style": "Pilsner", "abv": None},
    ]
