from logging import getLogger
from typing import Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, select

from db import Post, Snapshot, User, db
from .base import browse_element
from .tag import create_tag, get_tag

logger = getLogger('app_logger')

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
        logger.debug(f'Searching for post #{post_id} snapshots.')

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
    snap.tags = post.tags

    db.session.add(snap)
    logger.info(
        f'Created snapshot for post #{post.id} with tags {snap.tags}'
    )

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

    post.tags = list(prev.tags) 
    
    new_snapshot = create_snapshot(post, user)

    tag_names = ", ".join((tag.name for tag in new_snapshot.tags))
    logger.info(
        f'Reverted post #{post.id} to state from snapshot #{prev.id}. '
        f'New snapshot tags: {tag_names}'
    )

    return new_snapshot
