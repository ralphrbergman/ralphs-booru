from sqlalchemy import Column, ForeignKey, Integer, Table

from db import db

TagAssociation = Table(
    'tag_association',
    db.Model.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)
