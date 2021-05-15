from django.test import TestCase

from posts.models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug='test-group'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=User.objects.create(username='test_User')
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostsModelTest.post
        field_verboses = {
            'text': 'Текст записи',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostsModelTest.post
        field_help_texts = {
            'text': 'Поделитесь чем-нибудь',
            'group': 'Выберите группу, чтобы разместить запись в ней',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str(self):
        """Метод __str__ моделей Post и Group работает правильно."""
        post = PostsModelTest.post
        group = PostsModelTest.group
        expected_post_name = post.text[:15]
        expected_group_name = group.title
        expected_str = {
            expected_post_name: str(post),
            expected_group_name: str(group),
        }
        for expected_name, result_str in expected_str.items():
            with self.subTest(expected_name=expected_name):
                self.assertEqual(expected_name, result_str)
