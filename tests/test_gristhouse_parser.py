from scripts.scrape import (
    extract_embed_html_from_js,
    parse_untappd_embed_html,
)


def test_extract_embed_html_from_js() -> None:
    js = (
        'function x(){container.innerHTML = "'
        '<div class=\\"menu-item\\"><div class=\\"item-name\\">Lustra</div></div>'
        '";}'
    )
    html = extract_embed_html_from_js(js)
    assert html is not None
    assert 'item-name' in html


def test_parse_untappd_embed_html() -> None:
    html = '''
    <div class="menu-item">
      <div class="item-name">Lustra</div>
      <div class="item-style">Pale Ale</div>
      <div class="item-abv">6.8% ABV</div>
    </div>
    '''
    items = parse_untappd_embed_html(html)
    assert items[0]["name"] == "Lustra"
    assert items[0]["style"] == "Pale Ale"
    assert items[0]["abv"] == "6.8%"
