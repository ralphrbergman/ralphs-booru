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
        Post,
        ScoreAssociation,
        Tag,
        Thumbnail,
        TagAssociation,
        db
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

def setup_roles_command():
    from db import Permission, Role, db

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
    mod.permissions = [
        perms['comment'],
        perms['edit'],
        perms['upload'],
        perms['delete'],
        perms['tag_edit'],
        perms['user_ban']
    ]

    # Janitors only help with content
    janitor.permissions = [
        perms['comment'],
        perms['edit'],
        perms['delete'],
        perms['tag_edit']
    ]

    # Normal users can only upload
    user.permissions = [perms['comment'], perms['upload']]

    db.session.add_all([admin, mod, user, janitor])
    db.session.commit()
