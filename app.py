from os import getenv

from apiflask import APIFlask
from dotenv import load_dotenv
from flask import g, request, redirect
from flask.cli import with_appcontext
from flask_migrate import Migrate

from api import get_user
from brand import brand
from blueprint import api_bp, root_bp
from db import db, Permission, Role, User
from encryption import bcrypt
from login import login_manager
from logger import setup_logging
from translation import SUPPORTED_TRANSLATIONS, babel

load_dotenv()

SSL_ENABLED = getenv('SSL_ENABLED') == 'true'

def create_app() -> APIFlask:
    url = brand['url']
    app = APIFlask(
        import_name = __name__,
        template_folder = 'template',
        title = 'Ralphs Booru'
    )

    # Setup logging.
    setup_logging()

    if url:
        app.config['SERVERS'] = [
            {'url': url, 'description': 'Production server'}
        ]

    app.jinja_env.globals['brand'] = brand
    app.config['SECRET_KEY'] = getenv('SECRET_KEY')
    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

    db.init_app(app)

    @app.cli.command('setup-roles')
    @with_appcontext
    def setup_roles_command():
        perms = {
            'comment': Permission(slug='post:comment'),
            'upload': Permission(slug='post:upload'),
            'edit': Permission(slug = 'post:edit'),
            'delete': Permission(slug='post:delete'),
            'tag_edit': Permission(slug='tag:edit'),
            'user_ban': Permission(slug='user:ban'),
        }

        admin = Role(name = 'Admin', priority = 10)
        mod = Role(name = 'Moderator', priority = 8)
        janitor = Role(name = 'Janitor', priority = 2)
        user = Role(name = 'User', priority = 1)

        # Admins get everything
        admin.permissions = list(perms.values())

        # Moderators get most things
        mod.permissions = [perms['comment'], perms['edit'], perms['upload'], perms['delete'], perms['tag_edit'], perms['user_ban']]

        # Janitors only help with content
        janitor.permissions = [perms['comment'], perms['edit'], perms['delete'], perms['tag_edit']]

        # Normal users can only upload
        user.permissions = [perms['comment'], perms['upload']]

        db.session.add_all([admin, mod, user, janitor])
        db.session.commit()

    @app.cli.command('reindex')
    @with_appcontext
    def reindex_command():
        from sqlalchemy import delete, inspect, select

        from api import (
            add_vote,
            create_tag,
            create_thumbnail,
            get_comment,
            get_tag,
            remove_vote
        )
        from db import (
            db,
            Post,
            ScoreAssociation,
            Tag,
            Thumbnail,
            TagAssociation
        )

        print('Reindexing posts...')

        # Create offline models of posts.
        posts = db.session.scalars(
            select(Post)
            .order_by(Post.created.asc())
        ).all()

        post_data = []
        post_meta = {}

        for post in posts:
            data = {
                c.key: getattr(post, c.key)
                for c in inspect(post).mapper.column_attrs
            }
            data.pop('id', None)  # We don't want to reassign the same ID.

            meta = {
                'comments': [
                    {
                        'id': comment.id,
                        'score': [
                            {
                                'user_id': score.user_id,
                                'value': score.value
                            } for score in comment.scores
                        ]
                    } for comment in post.comments
                ],
                'score': [
                    {
                        'id': score.target_id,
                        'user_id': score.user_id,
                        'value': score.value
                    } for score in post.scores
                ],
                'tags': [ tag.name for tag in post.tags ]
            }

            post_data.append(data)
            post_meta[post.md5] = meta

        # Delete all rows in Post/Score/Tag/Thumbnail tables.
        db.session.execute(delete(Post))
        db.session.execute(delete(ScoreAssociation))
        db.session.execute(delete(Tag))
        db.session.execute(delete(Thumbnail))
        db.session.execute(delete(TagAssociation))
        db.session.commit()
        db.session.expire_all()
        db.session.expunge_all()

        # Convert offline models to online instances.
        db.session.bulk_insert_mappings(Post, post_data)
        db.session.commit()

        # Re-assign comments, scores, tags, thumbnails to posts.
        new_posts = db.session.scalars(
            select(Post)
            .order_by(Post.id.asc())
        ).all()
        tag_cache = dict()

        for post in new_posts:
            meta = post_meta[post.md5]

            with db.session.no_autoflush:
                # Comments.
                for comment_data in meta['comments']:
                    comment = get_comment(comment_data['id'])

                    for score in comment_data['score']:
                        if score['value'] == 1:
                            add_vote(
                                comment.id,
                                score['user_id'],
                                'comment'
                            )
                        else:
                            remove_vote(
                                comment.id,
                                score['user_id'],
                                'comment'
                            )

                    if comment and comment not in post.comments:
                        post.comments.append(comment)

                # Scores.
                for score in meta['score']:
                    if score['value'] == 1:
                        add_vote(post.id, score['user_id'], 'post')
                    else:
                        remove_vote(post.id, score['user_id'], 'post')

                # Tags.
                for tag_name in set(meta['tags']):
                    tag = tag_cache.get(tag_name) or get_tag(tag_name)

                    if not tag:
                        tag = create_tag(tag_name)

                    tag_cache[tag_name] = tag
                    
                    if tag not in post.tags:
                        post.tags.append(tag)

                # Thumbnail.
                thumb = create_thumbnail(post)

                if thumb:
                    db.session.add(thumb)

        db.session.commit()
        db.session.execute(db.text('VACUUM'))
        print("Reindexing complete.")

    # Elevate standard HTTP links to HTTPS for consumption
    # within Jinja2 templates.
    def secure_url(url: str) -> str:
        if url and url.startswith('http://') and SSL_ENABLED:
            return url.replace('http://', 'https://')

        return url

    # Initialize translations
    def get_locale() -> str:
        return g.get('lang_code', request.accept_languages.best_match(SUPPORTED_TRANSLATIONS))
    
    @app.before_request
    def ensure_lang_prefix():
        """ Redirect users to /en URL prefix if there's no languages prefixed. """
        if request.path.startswith('/static') or request.endpoint == 'static':
            return

        if request.path.startswith('/api'):
            return

        if request.path.startswith('/docs') or request.path.startswith('/openapi.json'):
            return

        path_parts = request.path.split('/')
        first_segment = path_parts[1] if len(path_parts) > 1 else None

        if first_segment in SUPPORTED_TRANSLATIONS:
            g.lang_code = first_segment
            return 

        lang = request.cookies.get('lang_code') or request.accept_languages.best_match(SUPPORTED_TRANSLATIONS) or 'en'
        return redirect(f'/{lang}{request.full_path}', code=302)

    babel.init_app(app, locale_selector = get_locale)

    # Initialize encrypting
    bcrypt.init_app(app)

    # Initialize session management
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return get_user(int(user_id))

    # Initialize database migration interface
    migrate = Migrate(app, db)

    app.jinja_env.filters['secure'] = secure_url
    app.register_blueprint(api_bp)
    app.register_blueprint(root_bp)

    return app
