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


def test_parse_untappd_embed_html_filters_to_taproom_tab() -> None:
    html = '''
    <div class="tab-content" data-tab-id="menu-1">
      <div class="menu-info"><h2 class="h2">Taproom Menu</h2></div>
      <div class="menu-item">
        <h4 class="item"><span id="happy_valley_jack">Happy Valley Jack</span></h4>
        <span class="item-category">IPA - New England</span>
        <span class="item-abv">6.4% ABV</span>
        <span class="screenreader-only">Rated 4.25 out of 5 on Untappd</span>
      </div>
      <div class="menu-item">
        <h4 class="item"><span id="draft_cider">Draft Cider</span></h4>
        <span class="item-category">Cider - Traditional</span>
        <span class="item-abv">6% ABV</span>
      </div>
    </div>
    <div class="tab-content" data-tab-id="menu-2">
      <div class="menu-info"><h2 class="h2">CANS &amp; BOTTLES TO GO</h2></div>
      <div class="menu-item">
        <h4 class="item"><span id="packaged_only">Packaged Only</span></h4>
        <span class="item-category">Stout</span>
        <span class="item-abv">8% ABV</span>
      </div>
    </div>
    '''

    items = parse_untappd_embed_html(html)

    assert [item["name"] for item in items] == ["Happy Valley Jack"]
    assert items[0]["style"] == "IPA - New England"
    assert items[0]["abv"] == "6.4%"
    assert items[0]["untappdRating"] == 4.25
