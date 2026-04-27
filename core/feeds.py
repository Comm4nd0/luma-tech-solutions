from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import BlogPost


class BlogFeed(Feed):
    title = f"{settings.SITE_NAME} blog"
    link = reverse_lazy("blog")
    description = (
        "Practical write-ups on networking, security, smart-home automation "
        "and software from Luma Tech Solutions."
    )
    feed_copyright = f"© {settings.SITE_NAME}"

    def items(self):
        return BlogPost.published.all()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.published_at

    def item_categories(self, item):
        return [item.get_pillar_display()]

    def item_author_name(self, item):
        return item.author
