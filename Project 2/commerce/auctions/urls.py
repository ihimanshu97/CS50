from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist/<int:listing_id>", views.edit_watchlist, name="edit_watchlist"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("watchlist/", views.view_watchlist, name="view_watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category")
]
