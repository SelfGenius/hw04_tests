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
            text='Текст поста созданого в фикстурах',
            author=cls.user_author,
            group=cls.group)

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_post_create_unauthorized_user(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост, созданный не авторизированным клиентом. ',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = f"{reverse('login')}?next={reverse('posts:post_create')}"
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_create_authorized_user(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост, созданный авторизированным клиентом.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': self.user_author.username}
            )
        )
        new_post = Post.objects.first()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit_unauthorized_user(self):
        """Проверка редактирования записи не авторизированным клиентом."""
        form_data = {
            'text': 'Текст поста ,измененный не авторизированным клиентом.',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        redirect = (reverse('login') + '?next=' + reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, redirect)
        not_edit_post = Post.objects.first()
        self.assertEqual(not_edit_post.id, self.post.id)
        self.assertNotEqual(not_edit_post.text, form_data['text'])
        self.assertEqual(not_edit_post.text, self.post.text)

    def test_post_edit_authorized_user(self):
        """Проверка редактирования записи авторизированным клиентом."""
        form_data = {
            'text': 'Текст поста ,измененный авторизированным клиентом.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', args=[self.post.id]),
            data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        edit_post = Post.objects.first()
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())
        self.assertEqual(edit_post.author.username, self.user_author.username)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])
