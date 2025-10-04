from pathlib import Path

from flask import Blueprint, request, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from api import create_post, get_post
from db import db, Post
from forms import UploadForm

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)

@post_bp.route('/browse')
def browse_page():
    posts = db.paginate(select(Post))
    return render_template('browse.html', posts = posts)

@post_bp.route('/view/<int:post_id>')
def view_page(post_id: int):
    return render_template('view.html', post = get_post(post_id))

@post_bp.route('/view_f/<int:post_id>')
def view_file_resource(post_id: int):
    post = get_post(post_id)

    return send_file(post.path)

@post_bp.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload_page():
    form = UploadForm()

    if request.method == 'GET':
        return render_template('upload.html', form = form)
    else:
        if form.validate_on_submit():
            for file in form.files.data:
                temp_path = Path('temp') / file.filename
                file.save(temp_path)

                post = create_post(
                    author = current_user,
                    path = temp_path,
                    directory = form.directory.data,
                    caption = form.caption.data,
                    tags = form.tags.data
                )

                flash(f'Successfully uploaded post #{post.id}')

            return redirect(url_for('Post.browse_page'))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

        return redirect(url_for('Post.upload_page'))
