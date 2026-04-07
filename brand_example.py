from flask_babel import gettext

brand = {
    'contact': {
        'discord': 'discord.gg/xxxxxxxx',
        'mail': 'admin@example.com',
        'media': {
            'social_media_1': 'my_handle',
            'social_media_2': '@my_handle',
            'social_media_3': 'http://example.com/my_handle'
        },
        'name': 'John Doe'
    },
    'description': gettext('My booru'),
    'full_brand': 'example.com',
    'copyright': '(c) 1970 - present',
    'version': '0.1.0',
    'url': 'http://example.com',
    'source_url': 'https://github.com/ralphrbergman/ralphs-booru'
}

# Add author's name to copyright line.
brand['copyright'] += ' ' + brand['contact']['name']
