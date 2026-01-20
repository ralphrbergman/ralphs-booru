from typing import Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, select

from db import Post, Snapshot, User, db
from .base import browse_element
from .tag import create_tag, get_tag

def browse_snapshots(*args, post_id: Optional[int] = None, **kwargs) -> SelectPagination:
    def apply_snapshot_specific_query(stmt: Select) -> None:
        nonlocal post_id

        stmt = stmt.where(Snapshot.post_id == post_id)

        return stmt

    return browse_element(Snapshot, extra_fn = apply_snapshot_specific_query, *args, **kwargs)

def create_snapshot(post: Post, user: User) -> Snapshot:
    hist = Snapshot()

    hist.post = post
    hist.user = user
    hist.tags = ' '.join(sorted(( tag.name for tag in post.tags )))

    db.session.add(hist)

    return hist

def get_snapshot(id: int) -> Optional[Snapshot]:
    return db.session.scalar(select(Snapshot).where(Snapshot.id == id))

def revert_snapshot(snapshot: Snapshot, user: User) -> Snapshot:
    prev = snapshot.previous
    post = snapshot.post

    post.tags.clear()
    db.session.flush()

    for tag_name in prev.tags.split():
        tag = get_tag(tag_name) or create_tag(tag_name)

        post.tags.append(tag)

    new_snapshot = create_snapshot(post, user)

    db.session.commit()
    return new_snapshot
