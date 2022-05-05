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

    def test_post_str(self):
        """Проверка, что Post.__str__ возвращает первые 15 символов поста."""
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_group_str(self):
        """Проверка, что Group.__str__ возвращает название группы."""
        self.assertEqual(self.group.title, str(self.group))

    def test_post_verbose_name(self):
        """Проверка verbose_name у модели Post."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_name(self):
        """Проверка verbose_name у модели Group."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный адрес группы',
            'description': 'Описание сообщества',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у модели Post."""
        field_help_texts = {
            'text': 'Добавьте описание поста',
            'group': 'Укажите группу в которой опубликуется пост',
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected)

    def test_group_help_text(self):
        field_help_texts = {
            'title': 'Укажите название группы',
            'slug': 'Выберите из списка или укажите новый адрес',
            'description': 'Добавьте описание группы',
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text, expected)
