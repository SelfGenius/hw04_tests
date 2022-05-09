from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


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
            username='user_author'
        )
        cls.ALL_POST_COUNT = 16
        Post.objects.bulk_create(
            Post(author=cls.user_author,
                 text=f'Тестовый пост{num_post}',
                 group=cls.group)
            for num_post in range(cls.ALL_POST_COUNT)
        )

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator(self):
        """Проверка работы пагинатора"""
        last_page = ceil(self.ALL_POST_COUNT / settings.NUMBER_OF_ENTRIES)
        count_posts_on_page = (self.ALL_POST_COUNT - (last_page - 1)
                               * settings.NUMBER_OF_ENTRIES)
        url_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user_author.username}): 'posts/profile.html',
        }
        for reverse_name, template in url_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_client.get(
                    reverse_name, {'page': last_page}
                )
                self.assertEqual(
                    len(response.context['page_obj']), count_posts_on_page
                )
                response = self.unauthorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.NUMBER_OF_ENTRIES
                )
