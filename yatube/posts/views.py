from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post, User


def paginator(page_number, post_list):
    post = Paginator(post_list, settings.NUMBER_OF_ENTRIES)
    page_obj = post.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator(request.GET.get('page'), post_list),
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': paginator(request.GET.get('page'), post_list),
    }
    return render(request, 'posts/group_list.html', context, )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.select_related('group')
    context = {
        'page_obj': paginator(request.GET.get('page'), post_list),
        'count_post': post_list.count,
        'author': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    context = {
        'post': post,
        'count_post': post.author.posts.count(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user == post.author:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': True})

    return redirect('posts:post_detail', post_id=post_id)
