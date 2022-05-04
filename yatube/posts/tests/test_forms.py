from http import HTTPStatus

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

    def test_post_create_unauthorized_user(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.unauthorized_user.post(reverse(
            'posts:post_create'), data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_create_authorized_user(self):
        """Проверка создания записи авторизированным клиентом."""
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(reverse(
            'posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user_author.username}))
        post = Post.objects.first()
        self.assertEqual(post.author.username, self.user_author.username)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, self.group.id)

    def test_post_edit_unauthorized_user(self):
        """Проверка редактирования записи не авторизированным клиентом."""
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.unauthorized_user.post(reverse(
            'posts:post_edit', args=[self.post.id]),
            data=form_data, follow=True)
        redirect = (reverse('login') + '?next=' + reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, redirect)
        post = Post.objects.first()
        self.assertEqual(post.text, 'Текст поста')

    def test_post_edit_authorized_user(self):
        """Проверка редактирования записи авторизированным клиентом."""
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', args=[self.post.id]),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.first()
        self.assertEqual(post.author.username, self.user_author.username)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, self.group.id)
