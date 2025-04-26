from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path("", views.index, name='index'),
    path("posts/create/", views.post, name='create_post'),
    path("posts/<int:id>/edit/", views.change_post, name='edit_post'),
    path("profile/edit/", views.profile_edit, name='edit_profile'),
    path(
        "posts/<int:id>/delete/",
        views.post,
        name='delete_post'
    ),
    path("profile/<slug:username>/", views.profile_details, name='profile'),
    path("posts/<int:post_id>/", views.post_detail, name='post_detail'),
    path("<slug:category_slug>/", views.category_posts, name='category_posts'),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.change_comment,
        name='edit_comment'
    ),
    path(
        "posts/<int:post_id>/comment/",
        views.add_comment,
        name='add_comment'
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name='delete_comment'
    ),
]
