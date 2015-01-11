from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
best_friend = Table('best_friend', post_meta,
    Column('user_id', Integer),
    Column('friend_id', Integer),
)

bestfriends_notifications = Table('bestfriends_notifications', post_meta,
    Column('user_id', Integer),
    Column('friend_id', Integer),
)

friends = Table('friends', post_meta,
    Column('user_id', Integer),
    Column('friend_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['best_friend'].create()
    post_meta.tables['bestfriends_notifications'].create()
    post_meta.tables['friends'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['best_friend'].drop()
    post_meta.tables['bestfriends_notifications'].drop()
    post_meta.tables['friends'].drop()
