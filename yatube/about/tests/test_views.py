from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_static_pages_exist_at_desired_location(self):
        """Страницы /about/author и /about/tech доступны любому пользователю"""
        pages = (
            '/about/author/',
            '/about/tech/',
        )
        for url in pages:
            with self.subTest(url=url):
                response = AboutPagesTest.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
