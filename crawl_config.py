NEWSPAPER_CONFIG_SELECTOR = {
    'tbsnews': {
        'created_at': '#inner-wrap > div.off-canvas-content > main > div > div.block-content.content > div.row.clearfix.mid-section > div:nth-child(1) > div.panel-pane.pane-news-details-left.no-title.block > div > div > div:nth-child(2)',
        'title': '#inner-wrap > div.off-canvas-content > main > div > div.block-content.content > div.row.clearfix.mid-section > div.large-6.small-12.columns.print-body > div.panel-pane.pane-node-content.no-title.block > div > article > header > h1',
        'description': '#inner-wrap > div.off-canvas-content > main > div > div.block-content.content > div.row.clearfix.mid-section > div.large-6.small-12.columns.print-body > div.panel-pane.pane-node-content.no-title.block > div > article > div.section-content.clearfix.margin-bottom-2',
        'image': '#inner-wrap > div.off-canvas-content > main > div > div.block-content.content > div.row.clearfix.mid-section > div.large-6.small-12.columns.print-body > div.panel-pane.pane-node-content.no-title.block > div > article > div.section-media.position-relative.featured-image > span > picture > img',
        'root_url': 'https://www.tbsnews.net/',
        'forbidden_url': ['/bangla/'],
    }
}