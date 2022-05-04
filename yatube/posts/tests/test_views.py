from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы')
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another_group_slug',
            description='Описание другой группы')
        cls.user_author = User.objects.create_user(
            username='user_author')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user_author,
            group=cls.group)

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user_author.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_content(self, context):
        self.assertEqual(context.author.username, self.user_author.username)
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.group, self.group)
        self.assertNotEqual(context.group, self.another_group)

    def test_index_pages_show_correct_context(self):
        """Шаблон 'index' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assert_content(response.context['page_obj'][0])

    def test_group_list_pages_show_correct_context(self):
        """Шаблон 'group_list' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})))
        self.assert_content(response.context['page_obj'][0])

    def test_profile_pages_show_correct_context(self):
        """Шаблон 'profile' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user_author.username})))
        self.assert_content(response.context['page_obj'][0])

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон 'post_detail' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assert_content(response.context['post'])

    def test_form_create_correct_context(self):
        """Шаблон 'form create' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_form_edit_correct_context(self):
        """Шаблон 'form edit' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorCountTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.user_author = User.objects.create_user(
            username='user_author')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.for_posts = [
            Post(
                author=self.user_author,
                text=f'Тестовый пост{num_post}',
                group=self.group
            )
            for num_post in range(13)
        ]
        Post.objects.bulk_create(self.for_posts)

    def test_paginator(self):
        """Проверка работы пагинатора"""
        posts_on_first_page = 10
        posts_on_second_page = 3

        pages = (
            (1, posts_on_first_page),
            (2, posts_on_second_page)
        )

        url_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user_author.username}): 'posts/profile.html',

        }
        for reverse_name, template in url_pages.items():
            with self.subTest(reverse_name=reverse_name):
                for page, count in pages:
                    response = self.authorized_client.get(
                        reverse_name, {'page': page}
                    )
                    self.assertEqual(
                        len(response.context['page_obj']), count)
