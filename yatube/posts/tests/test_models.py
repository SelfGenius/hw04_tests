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
        post = self.post
        result = post.text[:15]
        self.assertEqual(
            result, str(post))

    def test_post_verbose_name(self):
        """Проверка verbose_name у модели post."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у модели post."""
        post = self.post
        field_help_texts = {
            'text': 'Добавьте описание поста',
            'group': 'Укажите группу в которой опубликуется пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )

    def test_group_verbose_name(self):
        """Проверка verbose_name у модели group."""
        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный адрес группы',
            'description': 'Описание сообщества',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_group_help_text(self):
        """Проверка help_text у модели group."""
        group = self.group
        field_help_texts = {
            'title': 'Укажите название группы',
            'slug': 'Выберите из списка или укажите новый адрес',
            'description': 'Добавьте описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_group_str(self):
        """Проверка, что Group.__str__ возвращает название группы."""
        group = self.group
        result = group.title
        self.assertEqual(result, str(group))
