from django.urls import path
from . import views

app_name = "ec_site"

urlpatterns = [
    path("", views.IndexView.as_view()),
    path("searchResult/", views.SearchResult.as_view(), name="search_result"),
    path("itemDetail/<int:pk>", views.ItemDetail.as_view(), name = "item_detail"),
    path("cart/", views.Cart.as_view(), name="cart"),
    path("cartCorrect/<int:pk>", views.CartCorrect.as_view(), name="cart_correct"),
    path("cartDelete/<int:pk>/", views.CartDelete.as_view(), name="cart_delete"),
    path("userLogin/", views.UserLogin.as_view(), name="user_login"),
    path("userLogout/", views.UserLogout.as_view()),
    path("registerUser/", views.RegisterUser.as_view(), name="register_user"),
    path("checkRegiterUser/", views.CheckRegisterUser.as_view(), name="check_registerUser"),
    path("regiterUserCommit/",views.RegisterUserCommit.as_view(),name = "registerUserCommit"),
    path("userInfo/", views.UserInfo.as_view()),
    path("updateUserInfo/", views.UpdateUserInfo.as_view(), name="update_user"),
    path("updateUserConfirm/", views.UpdateUserConfirm.as_view(), name="update_user_confirm"),
    path("withdrawConfirm/", views.WithdrawConfirm.as_view(), name = "withdraw_confirm"),
    path("adminLogin/", views.AdminLogin.as_view(), name="admin_login"),
    path("adminMain/", views.AdminMain.as_view(), name="admin_main"),
    path("adminPurchaseLog/", views.AdminPurchaseLog.as_view(), name="admin_PurchaseLog"),
]
