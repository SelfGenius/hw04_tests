from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another_group_slug',
            description='Описание другой группы'
        )
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_pages_show_correct_context(self):
        """Проверка,что контекст на страницах правильно сформирован ."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user_author.username}),
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(self.post, response.context['page_obj'])

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон 'post_detail' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context['post'], self.post)

    def test_form_create_correct_context(self):
        """Шаблон 'form create' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(type(response.context['form']), type(PostForm()))

    def test_form_edit_correct_context(self):
        """Шаблон 'form edit' сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(type(response.context['form']), type(PostForm()))
        self.assertEqual(response.context['form'].instance, self.post)
