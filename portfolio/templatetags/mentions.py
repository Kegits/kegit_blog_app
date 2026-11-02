from django import template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from portfolio.mentions import MENTION_PATTERN

register = template.Library()


@register.filter
def render_mentions(comment):
    mentioned_users = {
        user.username.casefold(): user
        for user in comment.mentions.all()
    }
    parts = []
    position = 0

    for match in MENTION_PATTERN.finditer(comment.body):
        user = mentioned_users.get(match.group(1).casefold())
        if user is None:
            continue

        parts.append(format_html('{}', comment.body[position:match.start()]))
        parts.append(
            format_html(
                '<a class="comment-mention" href="{}">@{}</a>',
                reverse('user-posts', kwargs={'username': user.username}),
                match.group(1),
            )
        )
        position = match.end()

    parts.append(format_html('{}', comment.body[position:]))
    return mark_safe(''.join(parts))
