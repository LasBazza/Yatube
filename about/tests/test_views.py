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

        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')

    def test_static_pages_exist_at_desired_location(self):
        """Страница /about/tech доступны любому пользователю"""

        response = AboutPagesTest.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
