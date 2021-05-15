from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug='test-slug'
        )
        cls.user_author = User.objects.create_user(username='Ozzy')
        cls.user_not_author = User.objects.create_user(username='Iggy')
        cls.guest_client = Client()
        cls.authorized_author_client = Client()
        cls.authorized_not_author_client = Client()
        cls.authorized_author_client.force_login(cls.user_author)
        cls.authorized_not_author_client.force_login(cls.user_not_author)

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user_author
        )

    def test_access_for_guest_user(self):
        """Проверка доступа для неавторизованного пользователя"""
        pages_codes = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/{self.user_author.username}/': HTTPStatus.OK,
            f'/{self.user_author.username}/{self.post.id}/': HTTPStatus.OK,
            f'/{self.user_author.username}/{self.post.id}/edit/':
                HTTPStatus.FOUND,
            f'/{self.user_author.username}/{self.post.id}/comment':
                HTTPStatus.FOUND,
        }
        for url, code in pages_codes.items():
            with self.subTest(url=url):
                response = PostsURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_access_for_authorized_user_author(self):
        """Проверка доступа для авторизованного пользователя-автора"""
        pages = (
            '/new/',
            f'/{self.user_author.username}/{self.post.id}/edit/',
        )
        for url in pages:
            with self.subTest(url=url):
                response = PostsURLTests.authorized_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_of_edit_page_for_authorized_user_not_author(self):
        """Страница /<username>/<post_id>/edit не доступна
         авторизованному пользователю-не автору."""
        response = PostsURLTests.authorized_not_author_client.get(
            f'/{self.user_author.username}/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/new/': 'new_post.html',
            f'/{self.user_author.username}/{self.post.id}/edit/':
                'new_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = PostsURLTests.authorized_author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_from_edit_page(self):
        """Редирект со страницы <username>/<post_id>/edit
         работает правильно"""
        edit_post_redirect_to = reverse(
            'post', kwargs={
                'username': self.user_author.username, 'post_id': self.post.id
            }
        )
        response = PostsURLTests.authorized_not_author_client.get(
            f'/{self.user_author.username}/{self.post.id}/edit/'
        )
        self.assertRedirects(response, edit_post_redirect_to)

    def test_missing_page_returns_404_error(self):
        """Запрос к несуществующей странице возвращает код 404"""
        response = self.guest_client.get('/missing/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
