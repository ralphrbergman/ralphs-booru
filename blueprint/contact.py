from flask import Blueprint, render_template

contact_bp = Blueprint(
    name = 'Contact',
    import_name = __name__,
    url_prefix = '/contact'
)

@contact_bp.route('')
def contact_page():
    return render_template('contact.html')
