from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class BaseUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            slug='new_group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.url_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }
        cls.list_anonim = list(cls.url_templates.keys())[:4]
        cls.list_auth = list(cls.url_templates.keys())[4]
        cls.list_author = list(cls.url_templates.keys())[5]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class PostTestAccessAnonim(BaseUrlsTest):
    """Проверяем URLS для анонимного пользователя."""
    def test_access_for_anonim(self):
        """Основные страницы доступны для анонимного пользователя."""
        for address in self.url_templates:
            if address in self.list_anonim:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonim(self):
        """Выполняется редирект на страницу /auth/login/."""
        for address in self.url_templates:
            if address not in self.list_anonim:
                with self.subTest(address=address):
                    url = f'/auth/login/?next={address}'
                    response = self.guest_client.get(address, follow=True)
                    self.assertRedirects(response, url)

    def test_get404_for_anonim(self):
        """Не существующая страница отображает код HTTP 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class PostTestTemplatesAnonim(BaseUrlsTest):
    """Проверяем Templates для анонимного пользователя"""
    def test_used_correct_templates_for_anonim(self):
        """HTML-шаблон приходит в соответствиии с URL-адресом."""
        if self.url_templates in self.list_anonim:
            for address, template in self.url_templates:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)


class PostTestAccessAuth(BaseUrlsTest):
    """Проверяем доступность страниц для авторизованного пользователя."""
    def test_available_for_auth_users(self):
        """Страницы для авторизованного пользователя доступны."""
        for address in self.url_templates:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_for_auth_users(self):
        """Не существующая страница отображает код HTTP 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class PostTestTemplatesAuth(BaseUrlsTest):
    """Проверяем Templates для авторизованного пользователя."""
    def test_used_correct_template_for_auth_users(self):
        """HTML-шаблон приходит в соответствиии с URL-адресом."""
        if self.list_author not in self.url_templates:
            for address, template in self.url_templates:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
        response = self.authorized_client.get(self.list_author)
        template = self.url_templates[self.list_author]
        self.assertTemplateUsed(response, template)


class PostTestTemplatesAuthor(BaseUrlsTest):
    """Проверяем доступность страницы редактирования поста."""
    def setUp(self):
        super().setUp()
        self.other_user = User.objects.create_user(username='other_user')
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.other_user)

    def test_redirect_for_not_author(self):
        """
        Выполняется редирект на страницу posts/<post_id>/,
        если пользователь не является автором поста.
        """
        response = self.authorized_client_other.get(self.list_author)
        url = self.list_anonim[3]
        self.assertRedirects(response, url)
