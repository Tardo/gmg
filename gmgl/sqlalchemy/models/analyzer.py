# GMG Copyright 2022 - Alexandre Díaz
from gmgl.addons import cache
from datetime import datetime, timedelta
from flask_sqlalchemy_caching import FromCache
from flask_babel import _
from sqlalchemy import func, desc
from gmgl.utils import localize_datetime
from gmgl.nlp.knowledge import WORDS, get_analyzer_sections
from .mixins import AnalyzerMixin
from .base import BaseModel
from ..database import db


class MediaType(BaseModel):
    __tablename__ = 'media_type'
    _name_field = 'name'

    short_name = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(255))

    @classmethod
    def getByShortName(cls, short_name):
        return (
            cls.query.options(FromCache(cache)).filter_by(short_name=short_name).first()
        )


class WebEventType(BaseModel):
    __tablename__ = 'web_event_type'
    _name_field = 'name'

    short_name = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(255))

    @classmethod
    def getByShortName(cls, short_name):
        return (
            cls.query.options(FromCache(cache)).filter_by(short_name=short_name).first()
        )


rel_analyzer_post_analyzer_post_stat = db.Table(
    'rel_analyzer_post_analyzer_post_stat',
    BaseModel.metadata,
    db.Column('analyzer_post_id', db.ForeignKey('analyzer_post.id')),
    db.Column('analyzer_post_stat_id', db.ForeignKey('analyzer_post_stat.id')),
)
rel_analyzer_user_analyzer_post_stat = db.Table(
    'rel_analyzer_user_analyzer_post_stat',
    BaseModel.metadata,
    db.Column('analyzer_user_id', db.ForeignKey('analyzer_user.id')),
    db.Column('analyzer_post_stat_id', db.ForeignKey('analyzer_post_stat.id')),
)
rel_analyzer_user_avatar_attachment = db.Table(
    'rel_analyzer_user_avatar_attachment',
    BaseModel.metadata,
    db.Column(
        'analyzer_user_id', db.ForeignKey('analyzer_user.id', ondelete='CASCADE')
    ),
    db.Column('attachment_id', db.ForeignKey('attachment.id', ondelete='CASCADE')),
)
rel_analyzer_post_analyzer_post_comment = db.Table(
    'rel_analyzer_post_analyzer_post_comment',
    BaseModel.metadata,
    db.Column(
        'analyzer_post_id', db.ForeignKey('analyzer_post.id', ondelete='CASCADE')
    ),
    db.Column(
        'analyzer_post_comment_id',
        db.ForeignKey('analyzer_post_comment.id', ondelete='CASCADE'),
    ),
)


class AnalyzerUser(AnalyzerMixin, BaseModel):
    __tablename__ = 'analyzer_user'
    _name_field = 'name'

    name = db.Column(db.String(25), unique=True, nullable=False)
    ct_text = db.Column(db.String(128))
    banned = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    last_seen_admin_date = db.Column(db.DateTime(timezone=True))
    last_avatar_url = db.Column(db.Text)

    analyzer_post_stat_ids = db.relationship(
        'AnalyzerPostStat',
        secondary=rel_analyzer_user_analyzer_post_stat,
        back_populates='mention_user_ids',
    )
    avatar_ids = db.relationship(
        'Attachment', secondary=rel_analyzer_user_avatar_attachment
    )

    @classmethod
    def getByName(cls, site_id, name):
        return (
            cls.query.options(FromCache(cache))
            .filter_by(site_id=site_id, name=name)
            .first()
        )

    @classmethod
    def getByID(cls, site_id, id):
        return (
            cls.query.options(FromCache(cache))
            .filter_by(site_id=site_id, id=id)
            .first()
        )

    @classmethod
    def getModeratorUsers(cls, site_id, days):
        today = localize_datetime(datetime.utcnow())
        startday = (today - timedelta(days=days)).replace(hour=0, minute=0, second=0)
        startday_utc = localize_datetime(startday, 'UTC')
        return (
            cls.query.filter(
                cls.site_id == site_id,
                cls.last_seen_admin_date >= startday_utc,
                cls.banned == False,
                cls.admin == True,
                cls.name != '[Borrado]',
            )
            .order_by(cls.id.desc())
            .all()
        )

    @classmethod
    def getBannedUsers(cls, site_id, limit):
        return (
            cls.query.filter(
                cls.site_id == site_id, cls.banned == True, cls.name != '[Borrado]'
            )
            .order_by(cls.id.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def getDeletedUsers(cls, site_id, limit):
        return (
            cls.query.filter(
                cls.site_id == site_id, cls.deleted == True, cls.name != '[Borrado]'
            )
            .order_by(cls.id.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def getNewUsers(cls, site_id, limit):
        return (
            cls.query.filter(
                cls.site_id == site_id,
                cls.banned == False,
                cls.admin == False,
                cls.name != '[Borrado]',
            )
            .order_by(cls.id.desc())
            .limit(limit)
            .all()
        )

    def getMonthStatus(self):
        today = localize_datetime(datetime.utcnow())
        startday = today.replace(day=1, hour=0, minute=0, second=0)
        post_count = AnalyzerPost.query.filter(
            AnalyzerPost.site_id == self.site_id, AnalyzerPost.author_id >= self.id
        ).count()
        stats = (
            db.session.query(
                func.sum(AnalyzerPostStat.insult_word_count),
                func.sum(AnalyzerPostStat.swear_word_count),
                func.sum(AnalyzerPostStat.good_word_count),
                func.sum(AnalyzerPostStat.laugh_word_count),
                func.sum(AnalyzerPostStat.love_word_count),
                func.sum(AnalyzerPostStat.sad_word_count),
                func.sum(AnalyzerPostStat.dead_word_count),
                func.sum(AnalyzerPostStat.sex_word_count),
            )
            .join(AnalyzerPost, isouter=True)
            .join(
                AnalyzerPostComment,
                AnalyzerPostComment.post_id == AnalyzerPostStat.post_id,
                isouter=True,
            )
            .filter(
                AnalyzerPost.site_id == self.site_id,
                AnalyzerPost.author_id == self.id,
                AnalyzerPostComment.date >= startday,
            )
            .first()
        )
        result = {}
        if any(stats):
            total = sum(list(stats))
            print(list(stats))
            analyzer_sections = get_analyzer_sections()
            result.update(
                {
                    analyzer_sections[0]: round(stats[0] / total * 100, 2),
                    analyzer_sections[1]: round(stats[1] / total, 2),
                    analyzer_sections[2]: round((stats[2] + stats[3]) / total * 100, 2),
                    analyzer_sections[3]: round(stats[4] / total * 100, 2),
                    analyzer_sections[4]: round(stats[5] / total * 100, 2),
                    analyzer_sections[5]: round(stats[6] / total * 100, 2),
                    analyzer_sections[6]: round(stats[7] / total * 100, 2),
                }
            )
        return result


class AnalyzerThreadCategory(AnalyzerMixin, BaseModel):
    __tablename__ = 'analyzer_thread_category'
    _name_field = 'name'

    short_name = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(32), nullable=False)


class AnalyzerThread(AnalyzerMixin, BaseModel):
    __tablename__ = 'analyzer_thread'
    _name_field = 'title'

    category_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerThreadCategory.id), nullable=False
    )
    subcategory_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    author_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerUser.id), nullable=False, index=True
    )
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    read_count = db.Column(db.Integer, nullable=False, default=0)
    page_count = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    last_date = db.Column(db.DateTime(timezone=True))
    last_comment_user_id = db.Column(db.Integer, db.ForeignKey(AnalyzerUser.id))
    url = db.Column(db.Text, nullable=False, unique=True)
    last_page_done = db.Column(db.Integer, nullable=False)

    author = db.relationship('AnalyzerUser', foreign_keys='AnalyzerThread.author_id')
    last_comment_user = db.relationship(
        'AnalyzerUser', foreign_keys='AnalyzerThread.last_comment_user_id'
    )
    category = db.relationship(
        'AnalyzerThreadCategory', foreign_keys='AnalyzerThread.category_id'
    )

    db.UniqueConstraint('ref_id', 'site_id')


class AnalyzerPost(AnalyzerMixin, BaseModel):
    __tablename__ = 'analyzer_post'
    _name_field = 'thread_id'

    thread_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerThread.id), nullable=False, index=True
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerUser.id), nullable=False, index=True
    )
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    votes_good_count = db.Column(db.Integer, nullable=False, default=0)

    thread = db.relationship('AnalyzerThread', foreign_keys='AnalyzerPost.thread_id')
    author = db.relationship('AnalyzerUser', foreign_keys='AnalyzerPost.author_id')

    analyzer_post_stat_ids = db.relationship(
        'AnalyzerPostStat',
        secondary=rel_analyzer_post_analyzer_post_stat,
        back_populates='mention_post_ids',
    )
    comment_ids = db.relationship(
        'AnalyzerPostComment', secondary=rel_analyzer_post_analyzer_post_comment
    )

    db.UniqueConstraint('ref_id', 'thread_id', 'site_id')

    @classmethod
    def getMentionsMonthByUser(cls, site_id, user_id):
        today = localize_datetime(datetime.utcnow())
        startday = today.replace(day=1, hour=0, minute=0, second=0)
        query_res = db.session.execute(
            """
            SELECT analyzer_user.id, count(analyzer_user.name) as count_iters, analyzer_user.name from
            (
                SELECT
                    analyzer_user.name AS analyzer_user_name,
                    count(rel_analyzer_post_analyzer_post_stat.analyzer_post_id) as total_mentions,
                    rel_analyzer_post_analyzer_post_stat.analyzer_post_id AS rel_analyzer_post_analyzer_post_stat_analyzer_post_id
                FROM
                    rel_analyzer_post_analyzer_post_stat
                LEFT OUTER JOIN
                    analyzer_post_stat ON analyzer_post_stat.id = rel_analyzer_post_analyzer_post_stat.analyzer_post_stat_id
                LEFT OUTER JOIN
                    analyzer_post ON analyzer_post.id = analyzer_post_stat.post_id
                LEFT OUTER JOIN
                    analyzer_user ON analyzer_user.id = analyzer_post.author_id
                WHERE
                    analyzer_post.site_id = :site_id AND analyzer_post.author_id = :user_id
                GROUP BY
                    rel_analyzer_post_analyzer_post_stat.analyzer_post_id, analyzer_user.name
                ORDER BY
                    total_mentions desc
            ) as subq
            LEFT OUTER JOIN
                analyzer_post ON analyzer_post.id = subq.rel_analyzer_post_analyzer_post_stat_analyzer_post_id
            LEFT OUTER JOIN
                analyzer_post_comment ON analyzer_post_comment.post_id = subq.rel_analyzer_post_analyzer_post_stat_analyzer_post_id
            LEFT OUTER JOIN
                analyzer_user ON analyzer_user.id = analyzer_post.author_id
            WHERE
                analyzer_post_comment.date >= :startdate
            GROUP BY
                analyzer_user.name, subq.analyzer_user_name, analyzer_user.id
            ORDER BY
                count_iters desc
        """,
            {
                'site_id': site_id,
                'user_id': user_id,
                'startdate': startday,
            },
        )
        results = []
        for result in query_res:
            user = AnalyzerUser.query.get(result[0])
            results.append(
                {
                    'id': user.id,
                    'count': result[1],
                    'name': result[2],
                    'avatar_hash_ref': user.avatar_ids[-1].hash_ref
                    if user.avatar_ids
                    else '0',
                }
            )
        return results

    @classmethod
    def getMostMonthActiveUsers(cls, site_id, limit):
        today = localize_datetime(datetime.utcnow())
        startday = today.replace(day=1, hour=0, minute=0, second=0)
        startday_utc = localize_datetime(startday, 'UTC')
        query_res = (
            db.session.query(
                cls.author_id,
                func.count(cls.id).label('total_posts'),
                AnalyzerUser.name,
            )
            .join(AnalyzerUser, isouter=True)
            .filter(cls.site_id == site_id, cls.date >= startday_utc)
            .group_by(
                cls.author_id,
                AnalyzerUser.name,
            )
            .order_by(desc('total_posts'))
            .limit(limit)
            .all()
        )
        results = []
        for result in query_res:
            user = AnalyzerUser.query.get(result[0])
            results.append(
                {
                    'id': user.id,
                    'count': result[1],
                    'name': result[2],
                    'avatar_hash_ref': user.avatar_ids[-1].hash_ref
                    if user.avatar_ids
                    else '0',
                }
            )
        return results

    @classmethod
    def getFirstByUser(cls, site_id, user_id):
        return (
            cls.query.filter(cls.site_id == site_id, cls.author_id == user_id)
            .order_by(cls.date.asc())
            .first()
        )

    @classmethod
    def getLastByUser(cls, site_id, user_id):
        return (
            cls.query.filter(cls.site_id == site_id, cls.author_id == user_id)
            .order_by(cls.date.desc())
            .first()
        )

    @classmethod
    def getCountByUser(cls, site_id, user_id):
        return cls.query.filter(
            cls.site_id == site_id, cls.author_id == user_id
        ).count()

    @classmethod
    def getTopThreadsByUser(cls, site_id, user_id, limit=None, with_last_post=False):
        query_res = (
            db.session.query(
                cls.author_id,
                func.count(cls.id).label('total_posts'),
                AnalyzerThread.id,
                AnalyzerThread.url,
                AnalyzerThread.title,
                AnalyzerThreadCategory.name,
            )
            .join(AnalyzerThread, AnalyzerThread.id == cls.thread_id, isouter=True)
            .join(
                AnalyzerThreadCategory,
                AnalyzerThreadCategory.id == AnalyzerThread.category_id,
                isouter=True,
            )
            .filter(cls.site_id == site_id, cls.author_id == user_id)
            .group_by(
                cls.author_id,
                AnalyzerThreadCategory.name,
                AnalyzerThread.id,
                AnalyzerThread.url,
                AnalyzerThread.title,
            )
            .order_by(desc('total_posts'))
            .limit(limit)
            .all()
        )
        thread_post_ref_ids = {}
        if with_last_post:
            thread_ids = tuple(map(lambda x: x[2], query_res))
            query_post_res = (
                db.session.query(
                    func.max(cls.ref_id).label('last_post_ref_id'),
                    AnalyzerThread.id,
                )
                .join(AnalyzerThread, AnalyzerThread.id == cls.thread_id, isouter=True)
                .filter(
                    cls.site_id == site_id,
                    cls.author_id == user_id,
                    cls.thread_id.in_(thread_ids),
                )
                .group_by(AnalyzerThread.id)
                .order_by(desc('last_post_ref_id'))
                .all()
            )
            thread_post_ref_ids = {result[1]: result[0] for result in query_post_res}
        results = []
        for result in query_res:
            results.append(
                {
                    'id': result[2],
                    'count_posts': result[1],
                    'url': result[3],
                    'title': result[4],
                    'category': result[5],
                    'last_post_ref_id': thread_post_ref_ids.get(result[2], 0),
                }
            )
        return results


class AnalyzerPostComment(BaseModel):
    __tablename__ = 'analyzer_post_comment'
    _name_field = 'content'

    post_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerPost.id), nullable=False, index=True
    )
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    content = db.Column(db.Text)
    content_clean = db.Column(db.Text)

    post = db.relationship('AnalyzerPost', foreign_keys='AnalyzerPostComment.post_id')

    @classmethod
    def getMonthWordCountByUser(cls, site_id, user_id, limit=None):
        today = datetime.utcnow()
        startday = today.replace(day=1, hour=0, minute=0, second=0)
        results = db.session.execute(
            r"""
            SELECT w.word, sum(w.num_occurrences) AS total
            FROM {} apc
                CROSS JOIN LATERAL (
                    SELECT word, count(*) AS num_occurrences
                    FROM regexp_split_to_table(lower(apc.content_clean), '[\s[:punct:]]+') AS x(word)
                    WHERE word <> '' AND LENGTH(word) > 2 AND word !~ '^\d+$' AND word !~* '{}' AND word !~* '{}' AND word !~* '{}' AND word !~* '{}' AND word !~* '{}' AND word !~* '{}' AND word !~* '{}'
                    GROUP BY apc.post_id, word
                    ORDER BY apc.post_id, apc.id desc
                ) w
            LEFT OUTER JOIN
                analyzer_post ap ON ap.id = apc.post_id
            WHERE ap.site_id = :site_id AND ap.author_id = :user_id AND apc.date >= :startdate
            GROUP BY w.word
            ORDER BY total desc
            LIMIT :limit
        """.format(
                cls.__tablename__,
                WORDS['preposition'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['pronoun'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['adverb'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['conjunction'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['article'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['contraction'].replace(':', '\\:').replace('\\b', '\\y'),
                WORDS['ignore'].replace(':', '\\:').replace('\\b', '\\y'),
            ),
            {
                'user_id': user_id,
                'site_id': site_id,
                'startdate': startday,
                'limit': limit,
            },
        )
        return {result[0]: int(result[1]) for result in results}


class AnalyzerPostStat(BaseModel):
    __tablename__ = 'analyzer_post_stat'
    _name_field = 'post_id'

    post_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerPost.id), nullable=False, index=True
    )
    mention_user_ids = db.relationship(
        'AnalyzerUser',
        secondary=rel_analyzer_user_analyzer_post_stat,
        back_populates='analyzer_post_stat_ids',
    )
    mention_post_ids = db.relationship(
        'AnalyzerPost',
        secondary=rel_analyzer_post_analyzer_post_stat,
        back_populates='analyzer_post_stat_ids',
    )
    insult_word_count = db.Column(db.Integer)
    swear_word_count = db.Column(db.Integer)
    good_word_count = db.Column(db.Integer)
    love_word_count = db.Column(db.Integer)
    laugh_word_count = db.Column(db.Integer)
    sad_word_count = db.Column(db.Integer)
    dead_word_count = db.Column(db.Integer)
    sex_word_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)

    post = db.relationship('AnalyzerPost', foreign_keys='AnalyzerPostStat.post_id')


class AnalyzerPostMedia(BaseModel):
    __tablename__ = 'analyzer_post_media'
    _name_field = 'media_type_id'

    media_type_id = db.Column(
        db.Integer, db.ForeignKey(MediaType.id), nullable=False, index=True
    )
    post_id = db.Column(
        db.Integer, db.ForeignKey(AnalyzerPost.id), nullable=False, index=True
    )
    post_stat_id = db.Column(db.Integer, db.ForeignKey(AnalyzerPostStat.id))
    url = db.Column(db.Text, nullable=False)

    media_type = db.relationship(
        'MediaType', foreign_keys='AnalyzerPostMedia.media_type_id'
    )
    post = db.relationship('AnalyzerPost', foreign_keys='AnalyzerPostMedia.post_id')

    db.UniqueConstraint('url', 'media_type_id', 'post_id', 'site_id')

    @classmethod
    def getTopWeekByType(cls, site_id, media_type, limit):
        today = localize_datetime(datetime.utcnow())
        startday = (today - timedelta(days=today.weekday())).replace(
            hour=0, minute=0, second=0
        )
        startday_utc = localize_datetime(startday, 'UTC')
        query_res = (
            db.session.query(
                cls.url,
                MediaType.short_name,
                AnalyzerUser.name,
                AnalyzerPost.ref_id,
                AnalyzerPost.votes_good_count,
                AnalyzerThread.url,
            )
            .join(AnalyzerPost, AnalyzerPost.id == cls.post_id, isouter=True)
            .join(
                AnalyzerPostComment,
                AnalyzerPostComment.post_id == cls.post_id,
                isouter=True,
            )
            .join(AnalyzerUser, AnalyzerUser.id == AnalyzerPost.author_id, isouter=True)
            .join(
                AnalyzerThread,
                AnalyzerThread.id == AnalyzerPost.thread_id,
                isouter=True,
            )
            .join(MediaType, MediaType.id == cls.media_type_id, isouter=True)
            .filter(
                AnalyzerPost.site_id == site_id,
                AnalyzerPostComment.date >= startday_utc,
                MediaType.short_name == media_type,
            )
            .order_by(AnalyzerPost.votes_good_count.desc())
            .limit(limit)
            .all()
        )
        results = []
        for result in query_res:
            results.append(
                {
                    'url': result[0],
                    'type': result[1],
                    'author_name': result[2],
                    'ref_id': result[3],
                    'votes': result[4],
                    'thread_url': result[5],
                }
            )
        return results

    @classmethod
    def getLastByType(cls, site_id, media_type, limit):
        query_res = (
            db.session.query(
                cls.url,
                MediaType.short_name,
                AnalyzerUser.name,
                AnalyzerPost.ref_id,
                AnalyzerPost.votes_good_count,
                AnalyzerThread.url,
            )
            .join(AnalyzerPost, AnalyzerPost.id == cls.post_id, isouter=True)
            .join(
                AnalyzerPostComment,
                AnalyzerPostComment.post_id == cls.post_id,
                isouter=True,
            )
            .join(AnalyzerUser, AnalyzerUser.id == AnalyzerPost.author_id, isouter=True)
            .join(
                AnalyzerThread,
                AnalyzerThread.id == AnalyzerPost.thread_id,
                isouter=True,
            )
            .join(MediaType, MediaType.id == cls.media_type_id, isouter=True)
            .filter(
                AnalyzerPost.site_id == site_id,
                MediaType.short_name == media_type,
            )
            .order_by(AnalyzerPostComment.date.desc())
            .limit(limit)
            .all()
        )
        results = []
        for result in query_res:
            results.append(
                {
                    'url': result[0],
                    'type': result[1],
                    'author_name': result[2],
                    'ref_id': result[3],
                    'votes': result[4],
                    'thread_url': result[5],
                }
            )
        return results


class AnalyzerWebEvent(AnalyzerMixin, BaseModel):
    __tablename__ = 'analyzer_web_event'
    _name_field = 'type_id'

    type_id = db.Column(
        db.Integer, db.ForeignKey(WebEventType.id), nullable=False, index=True
    )
    origin_post_id = db.Column(db.Integer, db.ForeignKey(AnalyzerPost.id), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey(AnalyzerPost.id))
    user_id = db.Column(db.Integer, db.ForeignKey(AnalyzerUser.id), index=True)
    thread_id = db.Column(db.Integer, db.ForeignKey(AnalyzerThread.id))
    user_count = db.Column(db.Integer)
    old_avatar_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    new_avatar_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    applied = db.Column(db.Boolean, default=False)
    diff_count = db.Column(db.Integer)

    web_event_type = db.relationship(
        'WebEventType', foreign_keys='AnalyzerWebEvent.type_id'
    )
    origin_post = db.relationship(
        'AnalyzerPost', foreign_keys='AnalyzerWebEvent.origin_post_id'
    )
    post = db.relationship('AnalyzerPost', foreign_keys='AnalyzerWebEvent.post_id')
    user = db.relationship('AnalyzerUser', foreign_keys='AnalyzerWebEvent.user_id')
    thread = db.relationship(
        'AnalyzerThread', foreign_keys='AnalyzerWebEvent.thread_id'
    )
    old_avatar = db.relationship(
        'Attachment', foreign_keys='AnalyzerWebEvent.old_avatar_id'
    )
    new_avatar = db.relationship(
        'Attachment', foreign_keys='AnalyzerWebEvent.new_avatar_id'
    )

    @classmethod
    def createEvent(cls, event_type, options, add=True):
        invokes = {
            'online_users': cls._createEventUsersOnline,
            'post_reply': cls._createEventPostReply,
            'post_mention': cls._createEventPostMention,
            'user_avatar_change': cls._createEventUserAvatarChange,
            'user_banned': cls._createEventUserBanned,
            'user_deleted': cls._createEventUserDeleted,
            'hot_thread': cls._createEventHotThread,
        }
        if event_type in invokes:
            web_event = invokes[event_type](**options)
        else:
            raise Exception(_('Invalid event type'))
        if add and web_event:
            db.session.add(web_event)
        return web_event

    @classmethod
    def _createEventUsersOnline(cls, site_id, count):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('online_users').id,
            user_count=count,
        )

    @classmethod
    def _createEventPostReply(cls, site_id, origin_post_id, post_id):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('post_reply').id,
            origin_post_id=origin_post_id,
            post_id=post_id,
        )

    @classmethod
    def _createEventPostMention(cls, site_id, origin_post_id, user_id):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('post_mention').id,
            origin_post_id=origin_post_id,
            user_id=user_id,
        )

    @classmethod
    def _createEventUserAvatarChange(
        cls, site_id, user_id, old_avatar_id, new_avatar_id
    ):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('user_avatar_change').id,
            user_id=user_id,
            old_avatar_id=old_avatar_id,
            new_avatar_id=new_avatar_id,
        )

    @classmethod
    def _createEventUserBanned(cls, site_id, user_id, status):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('user_banned').id,
            user_id=user_id,
            applied=status,
        )

    @classmethod
    def _createEventUserDeleted(cls, site_id, user_id, status):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('user_deleted').id,
            user_id=user_id,
            applied=status,
        )

    @classmethod
    def _createEventHotThread(cls, site_id, thread_id, diff_count):
        return cls(
            site_id=site_id,
            type_id=WebEventType.getByShortName('hot_thread').id,
            thread_id=thread_id,
            diff_count=diff_count,
        )
