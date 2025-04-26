from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound

from .models import Post, Category, Comment

# Create your views here.
from blogicum.settings import OBJ_ON_LIST_COUNT
from .forms import PostForm, EditProfileForm, CommentForm

User = get_user_model()


def get_the_page(post_list, request):
    paginator = Paginator(post_list, OBJ_ON_LIST_COUNT)
    page_num = request.GET.get('page')
    return paginator.get_page(page_num)


def index(request):
    template_name = 'blog/index.html'
    post_list = Post.objects.filter(
        Q(category__isnull=False)
        & Q(category__is_published=True)
        & Q(is_published=True)
        & Q(pub_date__lte=timezone.now())
    ).select_related('author', 'location')
    context = {'page_obj': get_the_page(post_list, request)}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        pk=post_id,
        # is_published=True,
        # category__is_published=True,
        # pub_date__lte=timezone.now()
    )
    if post.author != request.user:
        if (
            post.is_published is not True
            or post.category.is_published is not True
            or post.pub_date > timezone.now()
        ):
            return HttpResponseNotFound('Нет такого поста')
    form = CommentForm()
    comments = post.comments.order_by('created_at')
    context = {'post': post,
               'comments': comments,
               'form': form
               }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    template_name = 'blog/category.html'
    post_list = category.posts.filter(
        Q(is_published=True)
        & Q(pub_date__lte=timezone.now())
    ).select_related('author', 'location')
    context = {'category': category,
               'page_obj': get_the_page(post_list, request)}
    return render(request, template_name, context)


def profile_details(request, username):
    instance = get_object_or_404(User, username=username)
    if request.user.username == username:
        post_list = instance.posts.all()
    else:
        post_list = instance.posts.filter(
            Q(category__is_published=True)
            & Q(is_published=True)
            & Q(pub_date__lte=timezone.now())
        )
    context = {'profile': instance,
               'page_obj': get_the_page(post_list, request)}
    template_name = 'blog/profile.html'
    return render(request, template_name, context)


@login_required
def profile_edit(request):
    if request.user.is_authenticated:
        instance = request.user
    else:
        return HttpResponseNotFound("Это не твой профиль")
    form = EditProfileForm(request.POST or None,
                           instance=instance)
    if request.method == 'POST':
        if form.is_valid:
            form.save()
        return redirect('blog:profile', request.user.username)
    context = {'form': form}
    template_name = 'blog/user.html'
    return render(request, template_name, context)


@login_required
def post(request, id=None):
    if id is None:
        instance = None
    else:
        instance = get_object_or_404(Post, pk=id, author=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance
    )
    if request.method == 'POST' and 'delete' in request.path:
        instance.delete()
        return redirect('blog:index')
    elif request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        return redirect('blog:profile', request.user.username)
    else:
        template_name = 'blog/create.html'
        context = {'form': form,
                   'post': instance}
        return render(request, template_name, context)


def change_post(request, id):
    instance = get_object_or_404(Post, pk=id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance
    )
    if request.method == 'POST' and 'edit' in request.path:
        if (
            request.user.is_authenticated is False
            or request.user != instance.author
        ):
            return redirect('blog:post_detail', id)
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail', instance.pk)
    else:
        template_name = 'blog/create.html'
        context = {'form': form,
                   'post': instance}
        return render(request, template_name, context)


@login_required
def change_comment(request, post_id, comment_id):
    instance = get_object_or_404(
        Comment,
        post_id=post_id,
        author=request.user,
        pk=comment_id
    )
    form = CommentForm(request.POST or None,
                       instance=instance)
    if request.method == 'POST' and 'edit' in request.path:
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form,
               'comment': instance}
    template_name = 'blog/comment.html'
    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(
        Comment,
        post_id=post_id,
        author=request.user,
        pk=comment_id
    )
    if request.method == 'POST' and 'delete' in request.path:
        instance.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': instance}
    template_name = 'blog/comment.html'
    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    get_object_or_404(Post, pk=post_id)
    # instance = get_object_or_404(
    #     Comment,
    #     author=request.user,
    #     post_id=post_id
    # )
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = Post.objects.get(pk=post_id)
            comment.save()
        return redirect('blog:post_detail', post_id)
    form = CommentForm()
    context = {'form': form}
    template_name = 'blog/detail.html'
    return render(request, template_name, context)
