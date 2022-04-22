import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()
POST_IN_FIRST_PAGE = 10
POST_IN_SECOND_PAGE = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='new_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Самый первый комментарий'
        )
        cls.index_url = reverse('Posts:index')
        cls.group_url = reverse('Posts:group_list', kwargs={
            'slug': cls.group.slug
        })
        cls.profile_url = reverse('Posts:profile', kwargs={
            'username': cls.user
        })
        cls.post_detail_url = reverse('Posts:post_detail', kwargs={
            'post_id': cls.post.pk
        })
        cls.post_create_url = reverse('Posts:post_create')
        cls.post_edit_url = reverse('Posts:post_edit', kwargs={
            'post_id': cls.post.pk
        })
        cls.follow_index_url = reverse('Posts:follow_index')
        cls.profile_follow_url = reverse('Posts:profile_follow', kwargs={
            'username': cls.user
        })
        cls.profile_unfollow_url = reverse('Posts:profile_unfollow', kwargs={
            'username': cls.user
        })

        cls.templates_pages_names = {
            cls.index_url: 'posts/index.html',
            cls.group_url: 'posts/group_list.html',
            cls.profile_url: 'posts/profile.html',
            cls.post_detail_url: 'posts/post_detail.html',
            cls.post_create_url: 'posts/create_post.html',
            cls.post_edit_url: 'posts/create_post.html',
            cls.follow_index_url: 'posts/follow.html',
            cls.profile_follow_url: 'posts/follow.html',
            cls.profile_unfollow_url: 'posts/follow.html',
        }
        cls.keys_dict = list(cls.templates_pages_names.keys())
        cls.have_paginator = cls.keys_dict[:3]
        cls.have_paginator.append(cls.keys_dict[6])
        cls.not_templates = cls.keys_dict[-2:]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.other_user = User.objects.create_user(username='other_user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_other = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_other.force_login(self.other_user)


class PostViewsTemplatesTest(BaseViewsTest):
    """Тестирование HTML-шаблонов"""
    def test_pages_used_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                if reverse_name not in self.not_templates:
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)


class PaginatorViewsTest(BaseViewsTest):
    """Тестирование паджинатора."""
    def setUp(self):
        super().setUp()
        for i in range(POST_IN_FIRST_PAGE + POST_IN_SECOND_PAGE):
            Post.objects.create(
                author=self.user,
                text=f'Тестовый пост №{i}',
                group=self.group
            )
        self.authorized_client_other.get(self.profile_follow_url)

    def test_paginator_first_page(self):
        """Тест паджинатора:на первой странице 10 постов."""
        for first in self.templates_pages_names.keys():
            if first in self.have_paginator:
                response = self.authorized_client_other.get(first)
                response.context['page_obj']
                len_cont = len(response.context['page_obj'])
                self.assertEqual(len_cont, POST_IN_FIRST_PAGE)

    def test_paginator_second_page(self):
        """Тест паджинатора:на второй странице 3 поста."""
        for second in self.have_paginator:
            created_post = Post.objects.count()
            response = self.authorized_client_other.get(second + '?page=2')
            len_cont = len(response.context['page_obj'])
            self.assertEqual(len_cont, created_post - POST_IN_FIRST_PAGE)


class PostViewsContextTest(BaseViewsTest):
    """Тестирование контекста в HTML-шаблонах."""
    def test_correct_context_page_obj(self):
        """Тест контекста - page_obj функций index, group_list, profile """
        self.authorized_client_other.get(self.profile_follow_url)
        for obj in range(len(self.have_paginator)):
            response = self.authorized_client_other.get(
                self.have_paginator[obj]
            )
            first_page = response.context['page_obj'][0]
            self.assertEqual(first_page.author.username, self.user.username)
            self.assertEqual(first_page.text, self.post.text)
            self.assertEqual(first_page.group.slug, self.group.slug)
            self.assertEqual(first_page.image, self.post.image)

    def test_index_correct_context_title(self):
        """Тест контекста - title функции index."""
        response = self.guest_client.get(self.index_url)
        title = response.context['title']
        self.assertEqual(title, 'Последние обновления на сайте')

    def test_group_correct_context_group(self):
        """Тест контекста - group функции group_posts."""
        response = self.guest_client.get(self.group_url)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)

    def test_profile_correct_context_profile(self):
        """Тест контекста - profile функции profile."""
        response = self.guest_client.get(self.profile_url)
        profile = response.context['profile']
        cnt_post = self.user.posts.count()
        self.assertEqual(profile.posts.count(), cnt_post)
        self.assertEqual(profile.username, self.user.username)

    def test_detail_correct_context_post(self):
        """Тест контекста - post функции detail_post."""
        response = self.guest_client.get(self.post_detail_url)
        this_post = response.context.get('post')
        comment = response.context['comments'][0]
        self.assertEqual(this_post.text, self.post.text)
        self.assertEqual(this_post.group.slug, self.group.slug)
        self.assertEqual(this_post.author.username, self.user.username)
        self.assertEqual(this_post.image, self.post.image)
        self.assertEqual(comment.text, self.comment.text)

    def test_post_create_correct_context_is_edit(self):
        """Тест контекста - is_edit функции post_create."""
        response = self.authorized_client.get(self.post_create_url)
        is_edit = response.context['is_edit']
        self.assertFalse(is_edit)

    def test_post_edit_correct_context_is_edit(self):
        """Тест контекста - is_edit функции post_edit."""
        response = self.authorized_client.get(self.post_edit_url)
        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)


class PostViewsFieldsTest(BaseViewsTest):
    """Тестирование полей формы в HTML-шаблонах."""
    def test_post_create_correct_context_form_get(self):
        """Шаблон post_create сформирован с правильной формой."""
        response = self.authorized_client.get(self.post_create_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.FileField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context_form_get(self):
        """Шаблон post_edit сформирован с правильной формой."""
        response = self.authorized_client.get(self.post_edit_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.FileField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostViewsCacheTest(BaseViewsTest):
    def test_index_cache(self):
        """Шаблон index работает с кеш."""
        get_content = self.authorized_client.get(self.index_url).content
        response = get_content
        self.post.delete()
        response_cache = get_content
        self.assertEqual(response, response_cache)
        cache.clear()
        response_clear = self.authorized_client.get(get_content)
        self.assertNotEqual(response, response_clear)


class PostViewsFollowTest(BaseViewsTest):
    """Тестирование возможности подписки и отписки от авторов."""
    def test_auth_able_follow(self):
        """Авторизованный пользователь может подписываться на пользователей."""
        cnt_follower = Follow.objects.count()
        redirect_url = self.profile_url
        response = self.authorized_client_other.get(self.profile_follow_url)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), cnt_follower + 1)
        self.assertTrue(
            Follow.objects.filter(author__username='test_user').exists()
        )

    def test_auth_able_unfollow(self):
        """Авторизованный пользователь может удалять авторов из подписок."""
        cnt_follower = Follow.objects.count()
        redirect_url = self.profile_url
        response = self.authorized_client_other.get(self.profile_follow_url)
        self.assertNotEqual(Follow.objects.count(), cnt_follower)
        response = self.authorized_client_other.get(self.profile_unfollow_url)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), cnt_follower)
        self.assertFalse(
            Follow.objects.filter(author__username='test_user').exists()
        )

    def test_do_not_show_posts_to_not_followers(self):
        """Новая запись автора не появляется в ленте тех, кто не подписан."""
        response = self.authorized_client_other.get(self.follow_index_url)
        response.context['page_obj']
        len_cont = len(response.context['page_obj'])
        self.assertEqual(len_cont, Follow.objects.count())

    def test_show_posts_to_followers(self):
        """Новая запись автора появляется в ленте тех, кто на него подписан."""
        self.authorized_client_other.get(self.profile_follow_url)
        response = self.authorized_client_other.get(self.follow_index_url)
        response.context['page_obj']
        len_cont = len(response.context['page_obj'])
        self.assertEqual(len_cont, Follow.objects.count())
