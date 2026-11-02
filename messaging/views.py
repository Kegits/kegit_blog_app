from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import DirectMessageForm, StartConversationForm
from .models import Conversation, DirectMessage


@login_required
def inbox(request):
    latest_messages = DirectMessage.objects.filter(
        conversation_id=OuterRef('pk')
    ).order_by('-sent_at')
    conversations = (
        Conversation.objects.filter(
            Q(first_user=request.user) | Q(second_user=request.user)
        )
        .select_related('first_user', 'second_user')
        .annotate(
            latest_message_body=Subquery(latest_messages.values('body')[:1]),
            latest_message_sender_id=Subquery(
                latest_messages.values('sender_id')[:1]
            ),
            latest_message_sent_at=Subquery(
                latest_messages.values('sent_at')[:1]
            ),
        )
        .annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__read_at__isnull=True)
                & ~Q(messages__sender=request.user),
            )
        )
        .order_by('-updated_at')
    )
    conversation_rows = [
        {
            'conversation': conversation,
            'other_user': conversation.other_user(request.user),
        }
        for conversation in conversations
    ]
    return render(
        request,
        'messaging/inbox.html',
        {
            'conversation_rows': conversation_rows,
            'start_form': StartConversationForm(),
        },
    )


@login_required
@require_POST
def start_conversation(request, username=None):
    form = StartConversationForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Enter a valid username to start a chat.')
        return redirect('messaging:inbox')

    requested_username = username or form.cleaned_data['username'].strip()
    recipient = get_object_or_404(
        User,
        username__iexact=requested_username,
        is_active=True,
    )
    if recipient.pk == request.user.pk:
        messages.error(request, 'Choose another user to start a private chat.')
        return redirect('messaging:inbox')

    conversation, _created = Conversation.get_or_create_between(
        request.user,
        recipient,
    )
    return redirect('messaging:conversation', pk=conversation.pk)


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.filter(
            Q(first_user=request.user) | Q(second_user=request.user)
        ).select_related('first_user', 'second_user'),
        pk=pk,
    )

    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.body = message.body.strip()
            if not message.body:
                form.add_error('body', 'Write a message before sending.')
            else:
                message.conversation = conversation
                message.sender = request.user
                message.save()
                return redirect('messaging:conversation', pk=conversation.pk)
    else:
        form = DirectMessageForm()
        conversation.messages.filter(
            read_at__isnull=True,
        ).exclude(sender=request.user).update(read_at=timezone.now())

    recent_messages = list(
        conversation.messages.select_related('sender')
        .order_by('-sent_at')[:100]
    )
    recent_messages.reverse()
    return render(
        request,
        'messaging/conversation.html',
        {
            'conversation': conversation,
            'other_user': conversation.other_user(request.user),
            'direct_messages': recent_messages,
            'message_form': form,
        },
    )


@login_required
@require_POST
def send_message_to_user(request, username):
    recipient = get_object_or_404(
        User,
        username__iexact=username,
        is_active=True,
    )
    if recipient.pk == request.user.pk:
        messages.error(request, 'You cannot start a chat with yourself.')
        return redirect('user-posts', username=recipient.username)

    conversation, _created = Conversation.get_or_create_between(
        request.user,
        recipient,
    )
    return redirect('messaging:conversation', pk=conversation.pk)
