from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'Root.Account.login_page'
