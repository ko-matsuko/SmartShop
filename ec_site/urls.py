from django.urls import path
from . import views

app_name = "ec_site"

urlpatterns = [
    path("", views.IndexView.as_view()),
    # path("",views.IndexView.as_view(), name = "main"),
    path("userLogin/", views.UserLogin.as_view(), name="user_login"),
    path("searchResult/", views.SearchResult.as_view(), name="search_result"),
    path("itemDetail/<int:pk>", views.ItemDetail.as_view()),
    path("cart/<int:pk>", views.Cart.as_view(), name="cart"),
    # path("articleCreate/", views.ArticleCreate.as_view(), name="article_create"),
]
