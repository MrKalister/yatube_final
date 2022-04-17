import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from ..models import Comment, Group, Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='new_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост',
            group=cls.group
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.form_data = {
            'text': 'Анонимный текст'
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Самый первый комментарий'
        )


class PostFormsTestCreateAuth(BaseFormsTest):
    def test_post_create_form_auth(self):
        """Валидная форма авторизованного пользователя создает запись."""
        cnt_post = Post.objects.count()
        test_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test_pic.gif',
            content=test_pic,
            content_type='image/gif'
        )
        create_data = {
            'author': self.user,
            'text': 'Измененный текст',
            'image': uploaded
        }
        redirect_url = reverse(
            'Posts:profile',
            kwargs={'username': self.user.username}
        )
        response = self.authorized_client.post(
            reverse('Posts:post_create'),
            data=create_data,
            follow=True
        )
        post_obj = Post.objects.get(text=create_data['text'])

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), cnt_post + 1)
        self.assertTrue(Post.objects.filter(text=create_data['text']).exists())
        self.assertEqual(post_obj.image, 'posts/test_pic.gif')


class PostFormsTestCreateAnonim(BaseFormsTest):
    def test_post_create_form_anonim(self):
        """
        У анонимного пользователя нет прав на создание записи
        Происходит редирект, новый пост не создается.
        """
        cnt_post = Post.objects.count()
        redirect_url = '/auth/login/?next=/create/'

        response = self.guest_client.post(
            reverse('Posts:post_create'),
            data=self.form_data,
            follow=True
        )

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), cnt_post)
        self.assertFalse(
            Post.objects.filter(
                text='Анонимный текст'
            ).exists()
        )


class PostFormsTestEditAuthor(BaseFormsTest):
    def test_post_edit_form(self):
        """Автор поста редактирует пост и отправляет валидную форму."""
        update_text = 'Текст был изменен'
        self.form_data['text'] = update_text

        response = self.authorized_client.post(
            reverse(
                'Posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.form_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, update_text)

    def test_post_edit_error_is_form_post(self):
        """
        Выводит ошибку в случае неправильного заполнения поля формы.
        """
        self.form_data['text'] = ''

        response = self.authorized_client.post(
            reverse(
                'Posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.form_data,
            follow=True
        )
        error = response.context.get('form').errors
        self.post.refresh_from_db()

        self.assertTrue(self.post.text)
        self.assertEqual(error['text'][0], 'Обязательное поле.')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostFormsTestEditAnonim(BaseFormsTest):
    def test_post_edit_form_anonim(self):
        """
        У анонимного пользователя нет прав на редактирование записи
        Происходит редирект, текст поста не меняется.
        """
        redirect_url = f'/auth/login/?next=/posts/{self.post.pk}/edit/'

        response = self.guest_client.post(
            reverse(
                'Posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.form_data,
            follow=True
        )

        self.assertRedirects(response, redirect_url)
        self.assertFalse(
            Post.objects.filter(
                text='Анонимный текст'
            ).exists()
        )


class PostFormsTestEditAuth(BaseFormsTest):
    def setUp(self):
        self.other_user = User.objects.create_user(username='other_user')
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.other_user)

    def test_post_edit_for_not_author(self):
        """
        Выполняется редирект на страницу posts/<post_id>/,
        если пользователь не является автором поста,
        текст поста не меняется.
        """
        redirect_url = f'/posts/{self.post.pk}/'

        response = self.authorized_client_other.post(
            reverse(
                'Posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.form_data,
            follow=True
        )

        self.post.refresh_from_db()
        self.assertRedirects(response, redirect_url)
        self.assertFalse(
            Post.objects.filter(
                text='Анонимный текст'
            ).exists()
        )


class CommentFormTestCreateAnonim(BaseFormsTest):
    def test_comment_create_form_anonim(self):
        """
        У анонимного пользователя нет прав на создание комментария,
        происходит редирект, новый комментарий не создается.
        """
        cnt_post = Comment.objects.count()
        redirect_url = f'/auth/login/?next=/posts/{self.post.pk}/comment/'

        response = self.guest_client.post(
            reverse(
                'Posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=self.form_data,
            follow=True
        )

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Comment.objects.count(), cnt_post)
        self.assertFalse(
            Comment.objects.filter(
                text='Анонимный текст'
            ).exists()
        )


class CommentFormTestCreateAuth(BaseFormsTest):
    def test_comment_create_form_auth(self):
        """Валидная форма авторизованного пользователя создает комментарий."""
        cnt_post = Comment.objects.count()
        comment_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Второй тестовый комментарий'
        }
        redirect_url = reverse(
            'Posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )

        response = self.authorized_client.post(
            reverse(
                'Posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=comment_data,
            follow=True
        )

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Comment.objects.count(), cnt_post + 1)
        self.assertTrue(Comment.objects.filter(
            text=comment_data['text']
        ).exists())
