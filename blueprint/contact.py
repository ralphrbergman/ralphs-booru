from flask import Blueprint, redirect, render_template
from brand import brand

contact_bp = Blueprint(
    name = 'Contact',
    import_name = __name__,
    url_prefix = '/contact'
)

@contact_bp.route('')
def contact_page():
    return render_template('contact.html')

@contact_bp.route('/discord')
def discord_page():
    return redirect(brand['contact']['discord'])
