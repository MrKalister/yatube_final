from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


User = get_user_model()


def call_paginator(post_list, request, post_in_page=10):
    paginator = Paginator(post_list, post_in_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': call_paginator(post_list, request),
        'title': title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': call_paginator(post_list, request),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    profile = get_object_or_404(User, username=username)
    post_list = profile.posts.all()
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=profile
    ).exists():
        following = True
    context = {
        'profile': profile,
        'following': following,
        'page_obj': call_paginator(post_list, request)
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    coments_list = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': coments_list
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method != 'POST':
        context = {
            'form': form,
            'is_edit': False
        }
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, {'form': form, 'is_edit': False})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('Posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    if post.author != request.user:
        return redirect('Posts:post_detail', post.pk)
    if request.method != "POST":
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, context)
    form.save()
    return redirect('Posts:post_detail', post_id)


def post_del(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('Posts:profile', request.user)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('Posts:post_detail', post_id)
    return redirect('Posts:post_detail', post_id)


@login_required
def follow_index(request):
    '''
    Выводит посты авторов
    на которых подписан текущий пользователь.
    '''
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': call_paginator(post_list, request),
        'title': 'Избранные авторы',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    '''Функция подписки на автора.'''
    author = get_object_or_404(User, username=username)
    follower = request.user
    follower_list = Follow.objects.filter(author=author, user=follower)
    if follower_list.exists() or follower == author:
        return redirect('Posts:index')
    Follow.objects.create(
        author=author,
        user=follower
    )
    return redirect('Posts:profile', username)


@login_required
def profile_unfollow(request, username):
    '''Функция отписки от автора.'''
    author = get_object_or_404(User, username=username)
    follower = request.user
    follower_list = Follow.objects.filter(author=author, user=follower)
    if not follower_list.exists():
        return redirect('Posts:index')
    follower_list.delete()
    return redirect('Posts:profile', username)
