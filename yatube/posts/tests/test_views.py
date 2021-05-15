import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from posts.models import Follow, Group, Post, User
from yatube import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group_target = Group.objects.create(
            title='Тестовая группа для записи',
            description='Описание тестовой группы',
            slug='test-slug-target'
        )
        cls.group_empty = Group.objects.create(
            title='Побочная тестовая группа',
            description='Описание побочной тестовой группы',
            slug='test-slug-empty'
        )
        cls.user = User.objects.create_user(username='Ozzy')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_follower = User.objects.create_user(username='Tony')
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.user_follower)

        cls.user_not_follower = User.objects.create_user(username='Geezer')
        cls.not_follow_client = Client()
        cls.not_follow_client.force_login(cls.user_not_follower)

        cls.test_follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        test_image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group_target,
            author=cls.user,
            image=test_image,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def check_post_fields(self, post):
        """Метод проверки полей поста"""
        post_text = post.text
        post_pub_date = post.pub_date
        post_author = post.author
        post_group = post.group
        post_image = post.image

        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group_target)
        self.assertEqual(post_image, self.post.image)

    def check_group_fields(self, group):
        """Метод проверки полей группы"""
        group_title = group.title
        group_description = group.description
        group_slug = group.slug

        self.assertEqual(group_title, self.group_target.title)
        self.assertEqual(group_description, self.group_target.description)
        self.assertEqual(group_slug, self.group_target.slug)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group_target.slug})
            ),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        self.assertIn('page', response.context)
        first_object = response.context['page'][0]

        self.check_post_fields(first_object)

    def test_group_page_shows_correct_context(self):
        """Шаблон group/slug сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group_target.slug})
        )
        self.assertIn('page', response.context)
        self.assertIn('group', response.context)
        first_object = response.context['page'][0]
        group_object = response.context['group']

        self.check_post_fields(first_object)
        self.check_group_fields(group_object)

    def test_new_post_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_shows_on_right_pages(self):
        """Новый пост отображается на нужных страницах"""
        pages = [
            '/',
            f'/group/{self.group_target.slug}/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.id}/'
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    self.assertEqual(len(response.context['page']), 1)
                else:
                    self.assertEqual(response.context['post'], self.post)

    def test_new_post_doesnt_show_on_other_groups_page(self):
        """Новый пост не отображается на странице другой группы"""
        response = self.authorized_client.get(reverse(
            'group', kwargs={'slug': self.group_empty.slug}
        ))
        self.assertEqual(len(response.context['page']), 0)

    def test_post_edit_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertIn('page', response.context)
        self.assertIn('author', response.context)
        post_object = response.context['page'][0]
        context_author = response.context['author']

        self.check_post_fields(post_object)
        self.assertEqual(context_author, self.user)
        self.assertEqual(context_author.username, self.user.username)

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username, 'post_id': self.post.id
            })
        )
        self.assertIn('post', response.context)
        self.assertIn('author', response.context)
        self.assertIn('count', response.context)

        post_object = response.context['post']
        context_author = response.context['author']
        context_count = response.context['count']
        count = Post.objects.filter(author=self.user).count()

        self.check_post_fields(post_object)
        self.assertEqual(context_author, self.user)
        self.assertEqual(count, context_count)

    def test_paginator(self):
        """Паджинатор работает правильно"""
        second_page_count = 2
        Post.objects.bulk_create([
            Post(
                text=f'Пост {i}',
                author=self.user,
                group=self.group_target,
            )
            for i in range(settings.PAGINATE_BY + second_page_count)
        ])
        urls = [
            '/',
            f'/group/{self.group_target.slug}/',
            f'/{self.user.username}/',
        ]
        pages = {
            '?page=1': settings.PAGINATE_BY,
            '?page=2': Post.objects.count() - settings.PAGINATE_BY,
        }
        for url in urls:
            for page, quantity in pages.items():
                with self.subTest():
                    response = self.authorized_client.get(url + page)
                    self.assertEqual(
                        len(response.context['page'].object_list), quantity
                    )

    def test_homepages_cache(self):
        """Кэширование главной страницы выполняется"""
        self.authorized_client.get(reverse('index'))
        key = make_template_fragment_key('index_page')
        index_page_cache = cache.get(key)
        self.assertIsNotNone(index_page_cache)

    def test_user_can_follow(self):
        """Пользователь может подписываться на других"""
        self.follower_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.user.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_follower,
                author=self.user
            ).exists()
        )
        test_follow = Follow.objects.get(
            user=self.user_follower,
            author=self.user
        )
        self.assertEqual(test_follow.user, self.user_follower)
        self.assertEqual(test_follow.author, self.user)

    def test_user_can_unfollow(self):
        """Пользователь может отписываться от других"""
        self.follower_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.test_follow.author.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_follower,
                author=self.user
            ).exists()
        )

    def test_new_post_shows_on_follow_page_of_followers(self):
        """Новый пост появляется в ленте подписчиков"""
        response = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 1)

        post = response.context['page'][0]
        self.check_post_fields(post)

    def test_new_post_doesnt_shows_on_follow_page_fo_other_users(self):
        """Новый пост не появляется в ленте других пользователей"""
        response = self.not_follow_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)
