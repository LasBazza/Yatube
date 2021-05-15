from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Show page about author"""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Show page about technologies"""
    template_name = 'about/tech.html'
