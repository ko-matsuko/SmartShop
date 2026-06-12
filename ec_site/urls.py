from django.urls import path
from . import views

app_name = "ec_site"

urlpatterns = [
    path("", views.IndexView.as_view()),
    path("",views.IndexView.as_view(), name = "main"),
    path("searchResult/", views.SearchResult.as_view(), name="search_result"),
    path("itemDetail/<int:pk>", views.ItemDetail.as_view()),
    path("cart/<int:pk>", views.Cart.as_view(), name="cart"),
    path("userLogin/", views.UserLogin.as_view(), name="user_login"),
    path("registerUser/", views.RegisterUser.as_view(), name="register_user"),
    path("checkRegiterUser/", views.CheckRegisterUser.as_view(), name="check_registerUser"),
    path("regiterUserCommit/",views.RegisterUserCommit.as_view(),name = "registerUserCommit")
]
