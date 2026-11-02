from typing import Optional
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CommentForm
from .mentions import MENTION_PATTERN
from .models import MentionNotification, Post, PostComment

# Create your views here.
# <app>/<model>_<viewtype>.html

class PostListView(ListView):
    model = Post
    template_name = 'portfolio/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        return (
            Post.objects.select_related('author', 'author__profile')
            .annotate(
                comment_count=Count('comments'),
                latest_comment_at=Max('comments__created_at'),
            )
            .order_by(*self.ordering)
        )


class UserPostListView(ListView):
    model = Post
    template_name = 'portfolio/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        self.profile_user = get_object_or_404(
            User.objects.select_related('profile'),
            username=self.kwargs.get('username'),
        )
        return (
            Post.objects.filter(author=self.profile_user)
            .select_related('author', 'author__profile')
            .annotate(
                comment_count=Count('comments'),
                latest_comment_at=Max('comments__created_at'),
            )
            .order_by('-date_posted')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user.profile
        return context


class PostDetailView(DetailView):
    model = Post

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'comments__author',
            'comments__mentions',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = kwargs.get('comment_form') or CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url ='/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'portfolio/about.html', {'title':'About'})


@require_GET
def comment_preview(request, pk):
    post = get_object_or_404(
        Post.objects.annotate(comment_count=Count('comments')),
        pk=pk,
    )
    comments = (
        PostComment.objects.filter(post=post)
        .select_related('author', 'author__profile')
        .prefetch_related('mentions')
        .order_by('-created_at')[:3]
    )
    return render(
        request,
        'portfolio/_comment_preview.html',
        {'post': post, 'comments': comments},
    )


@login_required
@require_POST
def create_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'portfolio/post_detail.html',
            {
                'object': post,
                'comment_form': form,
            },
            status=400,
        )

    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.body = comment.body.strip()
    if not comment.body:
        form.add_error('body', 'Write a comment before posting.')
        return render(
            request,
            'portfolio/post_detail.html',
            {
                'object': post,
                'comment_form': form,
            },
            status=400,
        )

    mentioned_usernames = {
        match.group(1)
        for match in MENTION_PATTERN.finditer(comment.body)
    }

    with transaction.atomic():
        comment.save()
        mentioned_users = list(
            User.objects.filter(
                username__in=mentioned_usernames,
                is_active=True,
            )
        )
        comment.mentions.set(mentioned_users)
        MentionNotification.objects.bulk_create(
            [
                MentionNotification(recipient=mentioned_user, comment=comment)
                for mentioned_user in mentioned_users
                if mentioned_user != request.user
            ]
        )

    messages.success(request, 'Your comment was posted.')
    return redirect(post.get_absolute_url())


@login_required
def notifications(request):
    user_notifications = (
        MentionNotification.objects.filter(recipient=request.user)
        .select_related('comment__post', 'comment__author')
        .prefetch_related('comment__mentions')
    )
    return render(
        request,
        'portfolio/notifications.html',
        {'notifications': user_notifications[:100]},
    )


@login_required
@require_POST
def open_notification(request, pk):
    notification = get_object_or_404(
        MentionNotification.objects.filter(recipient=request.user)
        .select_related('comment__post'),
        pk=pk,
    )
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=['read_at'])
    return redirect(notification.comment.post.get_absolute_url())