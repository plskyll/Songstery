from django.contrib.sitemaps import Sitemap
from .models import Book, Chapter


class BookSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Book.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class ChapterSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Chapter.objects.filter(is_approved=True).select_related('book')

    def location(self, obj):
        return obj.get_absolute_url()
