from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.user_another = User.objects.create_user(
            username='user_another'
        )
        cls.post = Post.objects.create(
            text='Текст который больше 15 символов',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_author)

    def test_url_correct_reverse_name(self):
        """Проверка, что URL-адрес соответвсует reverse('app_name:name')."""
        templates_pages_names = {
            '/': reverse('posts:index'),
            f'/group/{self.group.slug}/': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            f'/profile/{self.user_author.username}/': reverse(
                'posts:profile', args=[self.user_author.username]),
            f'/posts/{self.post.id}/': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}),
            f'/posts/{self.post.id}/edit/': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}),
            '/create/': reverse('posts:post_create'),
        }
        for url, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(url, reverse_name)

    def test_user_status_code_bool(self):
        """Проверка доступа для пользователей."""
        field_urls_code = (
            (reverse('posts:index'), HTTPStatus.OK, None),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             HTTPStatus.OK, None),
            (reverse('posts:group_list', kwargs={'slug': 'bad_slug'}),
             HTTPStatus.NOT_FOUND, None),
            (reverse('posts:group_list', kwargs={'slug': 'bad_slug'}),
             HTTPStatus.NOT_FOUND, True),
            (reverse('posts:profile', args=[self.user_author.username]),
             HTTPStatus.OK, None),
            (reverse('posts:profile', kwargs={'username': 'bad_username'}),
             HTTPStatus.NOT_FOUND, None),
            (reverse('posts:profile', kwargs={'username': 'bad_username'}),
             HTTPStatus.NOT_FOUND, True),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, None),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             HTTPStatus.FOUND, None),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, True),
            (reverse('posts:post_create'), HTTPStatus.FOUND, None),
            (reverse('posts:post_create'), HTTPStatus.OK, True),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND, None),
        )
        for url, response_code, args in field_urls_code:
            with self.subTest(url=url):
                status_code = self.unauthorized_user.get(url).status_code
                if args:
                    status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_unauthorized_user_redirect_status_code(self):
        """Проверка редиректа для неавторизованного пользователя."""
        field_urls_code = (
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            reverse('posts:post_create'),
        )
        for url in field_urls_code:
            with self.subTest(url=url):
                response = self.unauthorized_user.get(url, follow=True)
                redirect = f"{reverse('login')}?next={url}"
                self.assertRedirects(response, redirect)

    def test_authorized_user_redirect_status_code(self):
        """Проверка редиректа при редактировании автором чужого поста."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_user.force_login(self.user_another)
        response = self.authorized_user.get(url, follow=True)
        redirect = reverse('posts:post_detail', args=[self.post.pk])
        self.assertRedirects(response, redirect)
