from django.views.generic.base import TemplateView


class AboutTechView(TemplateView):
    """Show page about technologies"""
    template_name = 'about/tech.html'
