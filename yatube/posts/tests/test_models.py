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
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост длинее 15 символов',
            group=cls.group,
        )

    def test_group_str(self):
        """Проверка, что Post.__str__ и Group.__str__ работает коректно."""
        value__str__ = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title,
        }
        for value, expected in value__str__.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name(self):
        """Проверка verbose_name у модели Post."""
        field_verboses = (
            ('text', 'Текст поста', self.post),
            ('pub_date', 'Дата публикации', self.post),
            ('author', 'Автор', self.post),
            ('group', 'Группа', self.post),
            ('title', 'Название группы', self.group),
            ('slug', 'Уникальный адрес группы', self.group),
            ('description', 'Описание сообщества', self.group),
        )
        for value, expected, args in field_verboses:
            with self.subTest(value=value):
                self.assertEqual(
                    args._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        field_help_texts = (
            ('title', 'Укажите название группы', self.group),
            ('slug', 'Выберите из списка или укажите новый адрес', self.group),
            ('description', 'Добавьте описание группы', self.group),
            ('text', 'Добавьте описание поста', self.post),
            ('group', 'Укажите группу в которой опубликуется пост', self.post),
        )
        for value, expected, args in field_help_texts:
            with self.subTest(value=value):
                self.assertEqual(
                    args._meta.get_field(value).help_text, expected)
