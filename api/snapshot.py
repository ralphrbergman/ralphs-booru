from typing import Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, select

from db import Post, Snapshot, User, db
from .base import browse_element
from .tag import create_tag, get_tag

def browse_snapshots(
    *args,
    post_id: Optional[int] = None,
    **kwargs
) -> SelectPagination:
    """
    Paginates snapshots by criteria.

    Args:
        post_id: Which post's snapshots to show
        direction (str, optional): Sorting direction, asc for ascending
        and desc for descending
        limit (int): Amount of snapshots per page
        page (int): Page
        sort (str): Snapshot's column to sort by
    """
    def snapshot_select(stmt: Select) -> None:
        nonlocal post_id

        stmt = stmt.where(Snapshot.post_id == post_id)

        return stmt

    return browse_element(
        Snapshot,
        extra_fn = snapshot_select,
        *args,
        **kwargs
    )

def create_snapshot(post: Post, user: User) -> Snapshot:
    """
    Creates a snapshot of post.

    Args:
        post: Snapshot target
        user: Who creates the snapshot
    """
    snap = Snapshot()

    snap.post = post
    snap.user = user
    snap.tags = ' '.join(sorted(( tag.name for tag in post.tags )))

    db.session.add(snap)

    return snap

def get_snapshot(id: int) -> Optional[Snapshot]:
    """
    Obtains snapshot by its ID.
    """
    return db.session.scalar(select(Snapshot).where(Snapshot.id == id))

def revert_snapshot(snapshot: Snapshot, user: User) -> Snapshot:
    """
    Reverts post to previous snapshot.

    Args:
        snapshot: Which snapshot to revert
        user: User who reverts snapshot
    """
    prev = snapshot.previous
    post = snapshot.post

    post.tags.clear()
    db.session.flush()

    for tag_name in prev.tags.split():
        tag = get_tag(tag_name) or create_tag(tag_name)

        if tag:
            post.tags.append(tag)

    new_snapshot = create_snapshot(post, user)

    return new_snapshot
