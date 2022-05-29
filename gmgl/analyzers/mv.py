# GMG Copyright 2022 - Alexandre Díaz
import time
import datetime
import logging
import re
import html2text
from typing import List, Tuple, Callable, Awaitable, Any
from lxml import etree
from flask import current_app
from sqlalchemy.exc import NoResultFound
from gmgl.sqlalchemy.database import db
from gmgl.sqlalchemy.models.internal import AppWebConfig, Attachment, Site
from gmgl.sqlalchemy.models.analyzer import (
    AnalyzerUser,
    AnalyzerPost,
    AnalyzerPostComment,
    AnalyzerPostStat,
    AnalyzerPostMedia,
    AnalyzerThread,
    AnalyzerThreadCategory,
    AnalyzerWebEvent,
    MediaType,
)
from gmgl.utils import (
    etree_to_string,
    css_xpath,
    localize_datetime,
    int_to_date,
    get_url_filename_format,
    gen_sha256_from_memory,
)
from gmgl.http import Http
from gmgl.nlp.knowledge import WORDS, ANALYZER_WORD_TYPES


class MVHttp(Http):
    _domain = 'www.mediavida.com'
    _session_cookie_key = 'sess'

    def __init__(
        self,
        session_hash: str,
        max_tries: int = 3,
        debuglevel=0,
        post_per_page: int = 30,
    ):
        super().__init__(
            session_hash,
            max_tries=max_tries,
            debuglevel=debuglevel,
            post_per_page=post_per_page,
        )
        self._html2text = html2text.HTML2Text()
        self._html2text.escape_snob = True
        self._html2text.ignore_links = True
        self._html2text.ignore_anchors = True
        self._html2text.ignore_images = True

    def get_online_users_count(self):
        page_tree = self.get('/')
        users_count_elem = css_xpath(page_tree, 'ul.memb li:last-child')
        users_count = etree_to_string(users_count_elem[0])
        users_count = self._html2text.handle(users_count)
        if users_count:
            return int(users_count.strip().split(' ')[1][2:])
        return 0

    def get_spy_threads(self, timestamp=0):
        return self.post(
            '/foro/spy_get.php',
            data={
                'timestamp': timestamp,
            },
            xmlhttprequest=True,
        )

    def get_post(self, base_url, post_id):
        post_page = int(post_id / self.post_per_page) + 1
        url = f'{base_url}/{post_page}'
        print(f'Getting: {url}')
        page_tree = self.get(url, cache=True)
        post_element = css_xpath(page_tree, f'div.post[data-num={post_id}]')
        return post_element[0] if len(post_element) else None


class MVAnalyzer(object):
    _PREV_PAGES = 2
    _HOT_THREAD_COUNT = 20

    def __init__(self):
        self._site = RecordMetadata.ref('base_site_mediavida')
        self._http = MVHttp(
            session_hash=current_app.config['MV_SESSION_HASH'],
            debuglevel=1,
            post_per_page=self._site.post_per_page,
        )
        self._html2text = html2text.HTML2Text()
        self._html2text.escape_snob = True
        self._html2text.ignore_links = True
        self._html2text.ignore_anchors = True
        self._html2text.ignore_images = True

    def start(self):
        self.analyze_online_users()
        last_timestamp = AppWebConfig.get_param(
            'last_mv_spy_timestamp', int(time.time())
        )
        timestamp, athreads = self.analyze_threads(timestamp=last_timestamp)
        AppWebConfig.set_param('last_mv_spy_timestamp', timestamp)
        thread_requests_delay = current_app.config['MV_SCHEDULER_THREAD_REQUESTS_DELAY']
        for _, athread in enumerate(athreads):
            print(f"Analyzing thread posts '{athread.id}'...")
            thread_url, aposts = self.analyze_posts(athread)
            print(f'Scan finished! Post imported: {len(aposts)}')
            print(f'Waiting {thread_requests_delay} seconds...')
            time.sleep(thread_requests_delay)

    def analyze_online_users(self):
        online_users_count = self._http.get_online_users_count()
        AnalyzerWebEvent.createEvent(
            'online_users',
            {
                'site_id': self._site.id,
                'count': online_users_count,
            },
        )
        db.session.commit()

    def analyze_threads(self, timestamp):
        spy_threads = self._http.get_spy_threads(timestamp=timestamp)
        print(f"Found {len(spy_threads['items'])} new threads...")
        athreads = []
        for _, thread_info in enumerate(spy_threads['items']):
            author_id = int(thread_info['autor_id'])
            analyzer_user = AnalyzerUser.getByName(self._site.id, thread_info['autor'])
            if analyzer_user is None:
                analyzer_user = AnalyzerUser(
                    ref_id=author_id, name=thread_info['autor'], site_id=self._site.id
                )
                db.session.add(analyzer_user)
                db.session.flush()
            else:
                if not analyzer_user.ref_id:
                    analyzer_user.ref_id = author_id
            last_author = None
            if 'ultimo_uid' in thread_info and int(thread_info['ultimo_uid']) > 0:
                analyzer_user_last_user = AnalyzerUser.getByName(
                    self._site.id, thread_info['ultimo_nombre']
                )
                if analyzer_user_last_user is None:
                    analyzer_user_last_user = AnalyzerUser(
                        ref_id=int(thread_info['ultimo_uid']),
                        name=thread_info['ultimo_nombre'],
                        site_id=self._site.id,
                    )
                    db.session.add(analyzer_user_last_user)
                    db.session.flush()
                else:
                    if not analyzer_user_last_user.ref_id:
                        analyzer_user_last_user.ref_id = author_id
            post_category_id = int(thread_info['fid'])
            analyzer_thread_category = AnalyzerThreadCategory.query.filter_by(
                site_id=self._site.id, short_name=thread_info['friendly']
            ).first()
            if not analyzer_thread_category:
                analyzer_thread_category = AnalyzerThreadCategory(
                    ref_id=post_category_id,
                    short_name=thread_info['friendly'],
                    name=thread_info['nombre'],
                    site_id=self._site.id,
                )
                db.session.add(analyzer_thread_category)
                db.session.flush()

            thread_id = int(thread_info['tid'])
            analyzer_thread = AnalyzerThread.query.filter_by(
                site_id=self._site.id, ref_id=thread_id
            ).first()
            if analyzer_thread is None:
                analyzer_thread = AnalyzerThread(
                    ref_id=thread_id,
                    category_id=analyzer_thread_category.id,
                    subcategory_id=int(thread_info['cid']),
                    title=thread_info['cabecera'],
                    author_id=analyzer_user.id,
                    date=localize_datetime(
                        int_to_date(int(thread_info['fecha']), tz='Europe/Madrid'),
                        'UTC',
                    ),
                    url=thread_info['url'],
                    site_id=self._site.id,
                    last_page_done=int(thread_info['npag']),
                )
                db.session.add(analyzer_thread)
                db.session.flush()
            analyzer_thread.last_date = (
                localize_datetime(
                    int_to_date(int(thread_info['ultimo_fecha']), tz='Europe/Madrid'),
                    'UTC',
                )
                if 'ultimo_fecha' in thread_info
                else None
            )
            analyzer_thread.last_comment_user_id = (
                analyzer_user_last_user.id if analyzer_user_last_user else None
            )
            analyzer_thread.comment_count = int(thread_info['respuestas'])
            read_count = int(thread_info['lecturas'])
            current_read_count = analyzer_thread.read_count or 0
            diff_read_count = read_count - current_read_count
            if diff_read_count > self._HOT_THREAD_COUNT:
                AnalyzerWebEvent.createEvent(
                    'hot_thread',
                    {
                        'site_id': self._site.id,
                        'thread_id': analyzer_thread.id,
                        'diff_count': diff_read_count,
                    },
                )
            analyzer_thread.read_count = read_count
            analyzer_thread.page_count = int(thread_info['npag'])
            athreads.append(analyzer_thread)
        db.session.commit()
        return int(spy_threads['timestamp']), athreads

    def analyze_post(self, analyzer_thread, post):
        post_id = int(post.get('data-num'))
        # Get author info
        user_card_element = css_xpath(post, 'div.post-meta a.autor')[0]
        user_banned = css_xpath(post, 'div.post-meta .ban')
        is_user_banned = user_banned is not None and len(user_banned)
        author_id = user_card_element.get('data-id')
        is_banned = False
        is_deleted = False
        if author_id:
            author_id = int(author_id)
            if is_user_banned:
                is_banned = True
        else:
            is_deleted = is_user_banned
        author_username = post.get('data-autor')
        user_avatar_element = css_xpath(post, 'div.post-avatar img.avatar')
        author_avatar_url = user_avatar_element and user_avatar_element[0].get(
            'data-src'
        )
        mimetype_avatar = f'image/{get_url_filename_format(author_avatar_url)}'
        analyzer_user = AnalyzerUser.getByName(analyzer_thread.site_id, author_username)
        new_user_values = {
            'ref_id': author_id,
            'name': author_username,
            'banned': is_banned,
            'deleted': is_deleted,
            'site_id': analyzer_thread.site_id,
        }
        if analyzer_user is None:
            author_avatar = (
                self._http.download(author_avatar_url) if author_avatar_url else None
            )
            if author_avatar:
                author_avatar_hash = gen_sha256_from_memory(author_avatar)
                avatar_attachment = Attachment.query.filter_by(
                    hash_ref=author_avatar_hash
                ).first()
                if not avatar_attachment:
                    avatar_attachment = Attachment(
                        data=author_avatar, mimetype=mimetype_avatar
                    )
                new_user_values.update(
                    {
                        'last_avatar_url': author_avatar_url,
                        'avatar_ids': [avatar_attachment],
                    }
                )
            analyzer_user = AnalyzerUser(**new_user_values)
            db.session.add(analyzer_user)
        else:
            if author_id and not analyzer_user.ref_id:
                analyzer_user.ref_id = author_id
            if is_banned != analyzer_user.banned:
                analyzer_user.banned = is_banned
                AnalyzerWebEvent.createEvent(
                    'user_banned',
                    {
                        'site_id': analyzer_thread.site_id,
                        'user_id': analyzer_user.id,
                        'status': is_banned,
                    },
                )
            if is_deleted != analyzer_user.deleted:
                analyzer_user.deleted = is_deleted
                AnalyzerWebEvent.createEvent(
                    'user_deleted',
                    {
                        'site_id': analyzer_thread.site_id,
                        'user_id': analyzer_user.id,
                        'status': is_deleted,
                    },
                )
            if (
                analyzer_user.last_avatar_url != author_avatar_url
                and not is_banned
                and not is_deleted
            ):
                analyzer_user.last_avatar_url = author_avatar_url
                author_avatar = (
                    self._http.download(author_avatar_url)
                    if author_avatar_url
                    else None
                )
                if author_avatar:
                    author_avatar_hash = gen_sha256_from_memory(author_avatar)
                    avatar_attachment = Attachment.query.filter_by(
                        hash_ref=author_avatar_hash
                    ).first()
                    if not avatar_attachment:
                        avatar_attachment = Attachment(
                            data=author_avatar, mimetype=mimetype_avatar
                        )
                else:
                    avatar_attachment = None
                if avatar_attachment:
                    analyzer_user.avatar_ids.append(avatar_attachment)
                AnalyzerWebEvent.createEvent(
                    'user_avatar_change',
                    {
                        'site_id': analyzer_thread.site_id,
                        'user_id': analyzer_user.id,
                        'old_avatar_id': analyzer_user.avatar_ids[-1].id
                        if analyzer_user.avatar_ids
                        else None,
                        'new_avatar_id': avatar_attachment.id
                        if avatar_attachment
                        else None,
                    },
                )
        # Get CT
        ct_element = css_xpath(post, 'div.post-meta span.ct')
        has_ct = len(ct_element) != 0
        if has_ct:
            ct_text = ct_element[0].text
            if ct_text == 'Moderador':
                analyzer_user.admin = True
                analyzer_user.last_seen_admin_date = datetime.datetime.utcnow()
            else:
                analyzer_user.ct_text = ct_element[0].text
        # Get date info
        date_element = css_xpath(post, 'div.post-meta span.rd')[0]
        date = int(date_element.get('data-time'))
        date_obj = localize_datetime(int_to_date(date, tz='Europe/Madrid'), 'UTC')
        # Get if was edited
        edited_element = css_xpath(post, 'div.post-meta time.edited')
        is_edited = len(edited_element) != 0
        if is_edited:
            # Get edited date
            edited_date = edited_element[0].get('datetime') if is_edited else None
            edited_date_split = edited_date.split('+')
            edited_date_offset = edited_date_split[1].replace(':', '')
            edited_date_obj = localize_datetime(
                datetime.datetime.strptime(
                    f'{edited_date_split[0]}+{edited_date_offset}',
                    '%Y-%m-%dT%H:%M:%S%z',
                ),
                'UTC',
            )
        else:
            edited_date_obj = None
        # Get post content
        content_element = css_xpath(post, 'div.post-contents')[0]
        content = etree_to_string(content_element)
        content_clean = self._html2text.handle(content)
        content_clean = re.sub(r'\[code\]\n*.+\n*\[\/code\]', '', content_clean)
        # Get votes count
        votes_element = css_xpath(post, 'div.post-controls a.btnmola span')
        analyzer_post = AnalyzerPost.query.filter_by(
            site_id=analyzer_thread.site_id,
            thread_id=analyzer_thread.id,
            ref_id=post_id,
        ).first()
        if analyzer_post is None:
            analyzer_post = AnalyzerPost(
                ref_id=post_id,
                thread_id=analyzer_thread.id,
                author_id=analyzer_user.id,
                date=date_obj,
                site_id=analyzer_thread.site_id,
            )
            db.session.add(analyzer_post)
        content = content.strip()
        content_clean = content_clean.strip()
        if (
            not analyzer_post.comment_ids
            or analyzer_post.comment_ids[-1].content_clean != content_clean
        ):
            db.session.flush()
            analyzer_post_comment = AnalyzerPostComment(
                post_id=analyzer_post.id,
                date=edited_date_obj or date_obj,
                content=content,
                content_clean=content_clean,
            )
            analyzer_post.comment_ids.append(analyzer_post_comment)
        analyzer_post.votes_good_count = len(votes_element) and votes_element[0].text
        db.session.flush()
        self.analyze_post_content(analyzer_post)
        return analyzer_post

    def analyze_posts(self, analyzer_thread):
        aposts = []
        initial_page_num = max(analyzer_thread.last_page_done - self._PREV_PAGES, 1)
        pages_to_analyze_num = (analyzer_thread.page_count - initial_page_num) + 1
        for page_num in range(pages_to_analyze_num):
            page_url = f'{analyzer_thread.url}/{initial_page_num + page_num}'
            print(f'Page {page_url}')
            etree_page = self._http.get(url=page_url)
            post_elements = css_xpath(etree_page, '.cf.post')
            for post in post_elements:
                analyzer_post = self.analyze_post(analyzer_thread, post)
                aposts.append(analyzer_post)
            time.sleep(current_app.config['MV_SCHEDULER_POST_REQUESTS_DELAY'])
        analyzer_thread.last_page_done = analyzer_thread.page_count
        db.session.flush()
        return analyzer_thread.url, aposts

    def analyze_post_content(self, analyzer_post):
        content_elm = etree.fromstring(
            f'<div>{analyzer_post.comment_ids[-1].content}</div>'
        )
        if content_elm is None:
            return
        analyzer_post_stat = AnalyzerPostStat.query.filter_by(
            post_id=analyzer_post.id
        ).first()
        if analyzer_post_stat is None:
            analyzer_post_stat = AnalyzerPostStat(post_id=analyzer_post.id)
            db.session.add(analyzer_post_stat)
            db.session.flush()
        # User mentions
        user_mentions = css_xpath(content_elm, 'a.mention')
        users = []
        for user_mention in user_mentions:
            username = user_mention.get('data-name')
            analyzer_user = AnalyzerUser.getByName(analyzer_post.site_id, username)
            if analyzer_user is None:
                analyzer_user = AnalyzerUser(
                    name=username, site_id=analyzer_post.site_id
                )
                db.session.add(analyzer_user)
                db.session.flush()
            users.append(analyzer_user)
            AnalyzerWebEvent.createEvent(
                'post_mention',
                {
                    'site_id': analyzer_post.site_id,
                    'origin_post_id': analyzer_post.id,
                    'user_id': analyzer_user.id,
                },
            )
        analyzer_post_stat.mention_user_ids = users
        # Post mentions
        post_mentions = css_xpath(content_elm, 'a.quote')
        posts = set()
        for post_mention in post_mentions:
            quote_post_id = int(post_mention.get('rel'))
            analyzer_post_quote = AnalyzerPost.query.filter_by(
                site_id=analyzer_post.site_id,
                ref_id=quote_post_id,
                thread_id=analyzer_post.thread_id,
            ).first()
            if analyzer_post_quote is None:
                analyzer_thread = AnalyzerThread.query.get(analyzer_post.thread_id)
                post = self._http.get_post(analyzer_thread.url, quote_post_id)
                if post is None:
                    continue
                analyzer_post_quote = self.analyze_post(analyzer_thread, post)
                time.sleep(current_app.config['MV_SCHEDULER_POST_REQUESTS_DELAY'])
            posts.add(analyzer_post_quote)
            AnalyzerWebEvent.createEvent(
                'post_reply',
                {
                    'site_id': analyzer_post.site_id,
                    'origin_post_id': analyzer_post.id,
                    'post_id': analyzer_post_quote.id,
                },
            )
        analyzer_post_stat.mention_post_ids = list(posts)
        # Words
        for type_word in ANALYZER_WORD_TYPES:
            occur = re.findall(
                WORDS[type_word], analyzer_post.comment_ids[-1].content_clean
            )
            field_name = f'{type_word}_word_count'
            setattr(analyzer_post_stat, field_name, len(occur))
        analyzer_post_stat.word_count = len(
            analyzer_post.comment_ids[-1].content_clean.split(' ')
        )
        # Media links
        medias = []
        links = css_xpath(content_elm, 'a[href^=http][target]')
        media_type_link = MediaType.getByShortName('link')
        for link in links:
            link_href = link.get('href')
            analyzer_post_media = AnalyzerPostMedia.query.filter_by(
                post_id=analyzer_post.id, url=link_href
            ).first()
            if analyzer_post_media is None:
                analyzer_post_media = AnalyzerPostMedia(
                    post_id=analyzer_post.id,
                    url=link_href,
                    media_type_id=media_type_link.id,
                )
                db.session.add(analyzer_post_media)
            medias.append(analyzer_post_media)
        # Media videos youtube
        youtube_links = css_xpath(content_elm, 'a[data-youtube]')
        media_type_youtube = MediaType.getByShortName('youtube')
        for youtube_link in youtube_links:
            link_href = youtube_link.get('href')
            analyzer_post_media = AnalyzerPostMedia.query.filter_by(
                post_id=analyzer_post.id, url=link_href
            ).first()
            if analyzer_post_media is None:
                analyzer_post_media = AnalyzerPostMedia(
                    post_id=analyzer_post.id,
                    url=link_href,
                    media_type_id=media_type_youtube.id,
                )
                db.session.add(analyzer_post_media)
            medias.append(analyzer_post_media)
        # Media images
        image_links = css_xpath(content_elm, 'img[src]:not(.emoji)')
        media_type_image = MediaType.getByShortName('image')
        for image_link in image_links:
            link_src = image_link.get('src')
            analyzer_post_media = AnalyzerPostMedia.query.filter_by(
                post_id=analyzer_post.id, url=link_src
            ).first()
            if analyzer_post_media is None:
                analyzer_post_media = AnalyzerPostMedia(
                    post_id=analyzer_post.id,
                    url=link_src,
                    media_type_id=media_type_image.id,
                )
                db.session.add(analyzer_post_media)
            medias.append(analyzer_post_media)
        # Generic iframe links
        media_type_names = ('soundcloud', 'twitter')
        for media_type_name in media_type_names:
            media_type = MediaType.getByShortName(media_type_name)
            media_links = css_xpath(
                content_elm, f'div[data-s9e-mediaembed] iframe[src*={media_type_name}]'
            )
            for media_link in media_links:
                iframe_src = media_link.get('src')
                analyzer_post_media = AnalyzerPostMedia.query.filter_by(
                    post_id=analyzer_post.id, url=iframe_src
                ).first()
                if analyzer_post_media is None:
                    analyzer_post_media = AnalyzerPostMedia(
                        post_id=analyzer_post.id,
                        url=iframe_src,
                        media_type_id=media_type.id,
                    )
                    db.session.add(analyzer_post_media)
                medias.append(analyzer_post_media)
        db.session.flush()


def start_analyze():
    with db.app.app_context():
        analyzer = MVAnalyzer()
        print('Starting MV Analysis...')
        analyzer.start()
        print('MV Analysis Completed!')
    return True
