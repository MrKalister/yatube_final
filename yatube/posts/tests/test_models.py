from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='new_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Success consists of going from failure to failure'
                  'without loss of enthusiasm'),
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Метод __str__ в моделях Post, Group совпадает с ожидаемым."""
        post = self.post
        group = self.group
        methods_str = {
            post.text[:15]: str(post),
            group.title: str(group)
        }
        for name_str, extracted_value in methods_str.items():
            with self.subTest(name_str=name_str):
                self.assertEqual(name_str, extracted_value)

    def test_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
