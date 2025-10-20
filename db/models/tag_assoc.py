from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint

from db import db

TagAssociation = Table(
    'tag_association',
    db.Model.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
    UniqueConstraint('post_id', 'tag_id', name = 'uq_post_tag')
)
