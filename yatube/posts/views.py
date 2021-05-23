from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, GroupForm
from .models import Follow, Group, Post, User


def index(request):
    """Show last posts on the homepage"""
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    """Show posts on the group's page"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    """Create new post"""
    form = PostForm(request.POST or None, files=request.FILES or None,)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Show user's profile"""
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    count = user.posts.count()
    followers = Follow.objects.filter(author=user).count()
    followings = Follow.objects.filter(user=user).count()

    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=user).exists():
            following = True

    return render(
        request,
        'users/profile.html',
        {'author': user,
         'page': page,
         'paginator': paginator,
         'count': count,
         'followers': followers,
         'followings': followings,
         'following': following,
         }
    )


def post_view(request, username, post_id):
    """Show post"""
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id,
        author__username=username
    )
    user = post.author
    count = user.posts.count()
    comments = post.comments.all()
    followers = Follow.objects.filter(author=user).count()
    followings = Follow.objects.filter(user=user).count()

    form = CommentForm()

    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=user).exists():
            following = True

    return render(
        request,
        'post.html',
        {'post': post,
         'author': user,
         'count': count,
         'comments': comments,
         'form': form,
         'followers': followers,
         'followings': followings,
         'following': following,
         }
    )


@login_required
def post_edit(request, username, post_id):
    """Edit existing post"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', post_id=post.id, username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect('post', post_id=post.id, username=username)
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    """Add comment"""
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id,
        author__username=username
    )
    author = post.author
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = author
        comment.post = post
        comment.save()

    return redirect('post', post_id=post.id, username=username)


@login_required
def follow_index(request):
    """Show my subscription's"""
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    """Follow user"""
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Unfollow user"""
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('profile', username=username)


@login_required
def group_create(request):
    """Create new group"""
    form = GroupForm(request.POST or None)

    if form.is_valid():
        group = form.save()
        return redirect('group', slug=group.slug)

    return render(request, 'group_create.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
