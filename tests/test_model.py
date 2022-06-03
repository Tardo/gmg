# GMG Copyright 2022 - Alexandre Díaz
import json
from datetime import datetime, timedelta
from flask import session
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.sqlalchemy.models.analyzer import (
    AnalyzerUser,
    AnalyzerPost,
    AnalyzerPostComment,
    AnalyzerPostMedia,
    AnalyzerWebEvent,
    WebEventType
)
from gmgl.utils import date_to_str, time_to_str


def test_analyzer_user(client, records_loader):
    with client:
        records_loader('test_chart_data')
        records_loader('test_analyzer_user')
        site_id = RecordMetadata.ref('base_site_test').id

        user = AnalyzerUser.getByName(site_id, 'TestUserChartA')
        assert user is not None
        assert user.name == 'TestUserChartA'

        userbyid = AnalyzerUser.getByID(site_id, user.id)
        assert userbyid is not None
        assert userbyid.name == 'TestUserChartA'

        moderators = AnalyzerUser.getModeratorUsers(site_id, 1)
        assert len(moderators) == 0
        moderators = AnalyzerUser.getModeratorUsers(site_id, 3)
        assert len(moderators) == 1
        assert moderators[0].name == 'TestAnalyzerUserModerator'

        users_banned = AnalyzerUser.getBannedUsers(site_id, 5)
        assert len(users_banned) == 1
        assert users_banned[0].name == 'TestAnalyzerUserBanned'

        users_deleted = AnalyzerUser.getDeletedUsers(site_id, 5)
        assert len(users_deleted) == 1
        assert users_deleted[0].name == 'TestAnalyzerUserDeleted'

        users_new = AnalyzerUser.getNewUsers(site_id, 5)
        assert len(users_new) == 3
        assert users_deleted[0].name == 'TestAnalyzerUserDeleted'

        user_test = RecordMetadata.ref('test_user_chart_data_a')
        month_status = user_test.getMonthStatus()
        assert round(sum(month_status.values()), 0) == 100


def test_analyzer_post(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        user_test = RecordMetadata.ref('test_user_chart_data_b')

        mentions = AnalyzerPost.getMentionsMonthByUser(site_id, user_test.id)
        assert len(mentions) == 1
        assert mentions[0]['name'] == 'TestUserChartA'

        users_active = AnalyzerPost.getMostMonthActiveUsers(site_id, 5)
        assert len(users_active) == 2
        assert users_active[0]['name'] == 'TestUserChartB'
        assert users_active[0]['count'] == 2
        assert users_active[1]['name'] == 'TestUserChartA'
        assert users_active[1]['count'] == 1

        user_first_post = AnalyzerPost.getFirstByUser(site_id, user_test.id)
        assert user_first_post.id == RecordMetadata.ref('test_post_chart_data_b').id

        user_last_post = AnalyzerPost.getLastByUser(site_id, user_test.id)
        assert user_last_post.id == RecordMetadata.ref('test_post_chart_data_c').id

        user_count = AnalyzerPost.getCountByUser(site_id, user_test.id)
        assert user_count == 2

        user_top_threads = AnalyzerPost.getTopThreadsByUser(site_id, user_test.id)
        assert len(user_top_threads) == 1
        print(user_top_threads)
        assert (
            user_top_threads[0]['id']
            == RecordMetadata.ref('test_thread_chart_data_a').id
        )


def test_analyzer_post_comment(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        user_test = RecordMetadata.ref('test_user_chart_data_b')

        word_count = AnalyzerPostComment.getMonthWordCountByUser(site_id, user_test.id)
        assert 'comment' in word_count
        assert word_count['comment'] == 1


def test_analyzer_post_media(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        user_test = RecordMetadata.ref('test_user_chart_data_b')

        medias_youtube = AnalyzerPostMedia.getTopWeekByType(site_id, 'youtube', 5)
        assert len(medias_youtube) == 2
        assert medias_youtube[0]['author_name'] == 'TestUserChartB'
        assert medias_youtube[0]['votes'] == 3

        medias_youtube = AnalyzerPostMedia.getLastByType(site_id, 'youtube', 5)
        assert len(medias_youtube) == 2
        assert medias_youtube[0]['author_name'] == 'TestUserChartA'
        assert medias_youtube[0]['votes'] == 0


def test_analyzer_web_event(client, records_loader):
    with client:
        records_loader('test_chart_data')
        records_loader('test_bin_avatar')
        site_id = RecordMetadata.ref('base_site_test').id

        event = AnalyzerWebEvent.createEvent("online_users", {
            'site_id': site_id,
            'count': 35,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("post_reply", {
            'site_id': site_id,
            'origin_post_id': RecordMetadata.ref('test_post_chart_data_b').id,
            'post_id': RecordMetadata.ref('test_post_chart_data_a').id,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("post_mention", {
            'site_id': site_id,
            'origin_post_id': RecordMetadata.ref('test_post_chart_data_a').id,
            'user_id': RecordMetadata.ref('test_user_chart_data_a').id,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("user_avatar_change", {
            'site_id': site_id,
            'user_id': RecordMetadata.ref('test_user_chart_data_a').id,
            'old_avatar_id': RecordMetadata.ref('test_attachment_bin_avatar_a').id,
            'new_avatar_id': RecordMetadata.ref('test_attachment_bin_avatar_b').id,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("user_banned", {
            'site_id': site_id,
            'user_id': RecordMetadata.ref('test_user_chart_data_a').id,
            'status': True,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("user_deleted", {
            'site_id': site_id,
            'user_id': RecordMetadata.ref('test_user_chart_data_a').id,
            'status': True,
        })
        assert event is not None

        event = AnalyzerWebEvent.createEvent("hot_thread", {
            'site_id': site_id,
            'thread_id': RecordMetadata.ref('test_thread_chart_data_a').id,
            'diff_count': 95,
        })
        assert event is not None

        events = AnalyzerWebEvent.query.filter_by(site_id=site_id).all()
        assert len(events) == 7