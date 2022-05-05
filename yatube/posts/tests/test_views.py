from django import forms
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
        cls.form = PostForm()

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
                self.assertEqual(response.context['page_obj'][0], self.post)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон 'post_detail' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context['post'], self.post)

    def test_forms_show_correct(self):
        """Проверка коректности формы.
        С тестом формы не разобрался. Как я понимаю, я сделал текст проверящий
        что в поле 'text'- CharField, а поле 'group' - ChoiceField.
        Как подменить CharField и ChoiceField на PostForm, не разобрался.
        В фиккстурах уже явно прописал, но видно всё мимо.
        К третьему ревью обещаю сделать, нужно подумать как."""
        context = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)
