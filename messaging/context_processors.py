from django.db.models import Q

from portfolio.models import MentionNotification

from .models import DirectMessage


def social_unread_counts(request):
    if not request.user.is_authenticated:
        return {'unread_message_count': 0, 'unread_mention_count': 0}

    unread_message_count = DirectMessage.objects.filter(
        Q(conversation__first_user=request.user)
        | Q(conversation__second_user=request.user),
        read_at__isnull=True,
    ).exclude(sender=request.user).count()
    unread_mention_count = MentionNotification.objects.filter(
        recipient=request.user,
        read_at__isnull=True,
    ).count()

    return {
        'unread_message_count': unread_message_count,
        'unread_mention_count': unread_mention_count,
    }
