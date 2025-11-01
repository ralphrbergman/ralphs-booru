brand = {
    'contact': {
        'address': 'example.com',
        'mail': 'user@example.com',
        'name': 'Your Name',
    },
    'full_brand': 'Ralphs Booru',
    'copyright': '(c) 2025 - present',
    'version': '0.1.0',
    'source-url': 'https://github.com/ralphrbergman/ralphs-booru'
}

# Add author's name to copyright line.
brand['copyright'] += ' ' + brand['contact']['name']
