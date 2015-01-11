from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
best_friend = Table('best_friend', post_meta,
    Column('user_id', Integer),
    Column('friend_id', Integer),
)

user = Table('user', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('email', String),
    Column('age', Integer),
    Column('bestfriend_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['best_friend'].create()
    pre_meta.tables['user'].columns['bestfriend_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['best_friend'].drop()
    pre_meta.tables['user'].columns['bestfriend_id'].create()
