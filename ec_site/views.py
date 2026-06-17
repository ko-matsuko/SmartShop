from django.shortcuts import render
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import View
from django.urls import reverse
from ec_site.models import ShoppingCategory,ShoppingItem, ShoppingItemsIncart, AccountUser, ShoppingPurchase, ShoppingPurchaseDetail
from ec_site.forms import UserLoginForm, SearchFormCategory, SearchFormKeyword, CreateUserForm, UpdateUserForm, AdminLoginForm
from django.db.models import Q, Prefetch

class IndexView(View):
    def get(self, request, *args, **kwargs):
        queryset = ShoppingCategory.objects.all()
        context = {
            "category_list": queryset,
        }
        return render(request, "ec_site/main.html", context)

    # def get(self, request, *args, **kwargs):
    #     form_category = SearchFormCategory()
    #     form_keyword = SearchFormKeyword()

    #     context = {
    #         "form_category": form_category,
    #         "form_keyword": form_keyword,
    #     }
    #     return render(request, "ec_site/main.html",context)
    
    # def post(self, request, *args, **kwargs):
    #     if request["flag"]:

    
class SearchResult(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ec_site/search_result.html")
    
    def post(self, request, *args, **kwargs):
        category_id = int(request.POST["category"])
        keyword = request.POST["keyword"]

        if category_id == 0:
            queryset = ShoppingItem.objects.filter(name__icontains = keyword)
            category_name = "すべて"
        else:
            queryset = ShoppingItem.objects.filter(category_id = category_id, name__icontains = keyword)
            category = ShoppingCategory.objects.get(category_id = category_id)
            category_name = category.name

        context = {
            "category": category_name,
            "keyword": keyword,
            "item_list": queryset
        }
        return render(request, "ec_site/search_result.html", context)
    
class ItemDetail(View):
    def get(self, request, pk):
        queryset = ShoppingItem.objects.get(pk=pk)

        stock_num_list = []
        if queryset.stock > 0:
            for i in range(0, queryset.stock):
                stock_num_list.append(i+1)

        context = {
            "item": queryset,
            "num_list": stock_num_list,
        }
        return render(request, "ec_site/item_detail.html", context)
    
class Cart(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('/ec_site/userLogin')
        else:
            item_incart = ShoppingItemsIncart.objects.filter(user_id = request.session["user_id"])

            item_list = []
            charge_total = 0
            for item in item_incart:
                item_detail = ShoppingItem.objects.get(item_id = item.item_id)

                item_dict = {
                    "item_id": item_detail.item_id,
                    "name":item_detail.name,
                    "color": item_detail.color,
                    "manufacturer":item_detail.manufacturer,
                    "price": item_detail.price,
                    "amount": item.amount
                }
                item_list.append(item_dict)
                charge_total += item.amount * item_detail.price

            context = {
                "item_list":item_list,
                "charge_total":charge_total
            }
            return render(request, "ec_site/cart.html",context)
    
    def post(self, request,  *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('/ec_site/userLogin')
        else:

            item_id = request.POST["item_id"]
            new_item = ShoppingItem.objects.get(item_id = item_id)
            item_amount = request.POST["amount"]

            if ShoppingItemsIncart.objects.filter(item_id = item_id, user_id = request.session["user_id"]).exists():
                cart_item = ShoppingItemsIncart.objects.get(item_id = item_id, user_id = request.session["user_id"])
            else:
                cart_item = ShoppingItemsIncart()
            cart_item.amount = item_amount
            cart_item.item_id = new_item.item_id
            cart_item.user_id = request.session["user_id"]
            cart_item.save()

            item_incart = ShoppingItemsIncart.objects.filter(user_id = request.session["user_id"])

            item_list = []
            charge_total = 0
            for item in item_incart:
                item_detail = ShoppingItem.objects.get(item_id = item.item_id)

                item_dict = {
                    "item_id": item.item_id,
                    "name":item_detail.name,
                    "color": item_detail.color,
                    "manufacturer":item_detail.manufacturer,
                    "price": item_detail.price,
                    "amount": item.amount
                }
                item_list.append(item_dict)
                charge_total += item.amount * item_detail.price

            context = {
                "item_list":item_list,
                "charge_total":charge_total
            }
            return render(request, "ec_site/cart.html",context)
    
class CartCorrect(View):
    def get(self, request, pk):
        cart_item = ShoppingItemsIncart.objects.get(item_id=pk, user_id=request.session["user_id"])
        item_detail = ShoppingItem.objects.get(item_id = cart_item.item_id)

        stock_num_list = []
        if item_detail.stock > 0:
            for i in range(0, item_detail.stock):
                stock_num_list.append(i+1)

        context = {
            "item_id": item_detail.item_id,
            "name":item_detail.name,
            "color": item_detail.color,
            "manufacturer":item_detail.manufacturer,
            "price": item_detail.price,
            "amount": cart_item.amount,
            "num_list": stock_num_list,
        }
        return render(request, "ec_site/cartCorrect.html", context)
    
    # def post(self, request, pk):
        
class CartDelete(View):
    def get(self, request,pk):
        cart_item = ShoppingItemsIncart.objects.get(item_id=pk, user_id=request.session["user_id"])
        item_detail = ShoppingItem.objects.get(item_id = cart_item.item_id)

        context = {
            "item_id": item_detail.item_id,
            "name":item_detail.name,
            "color": item_detail.color,
            "manufacturer":item_detail.manufacturer,
            "price": item_detail.price,
            "amount": cart_item.amount,
        }
        return render(request, "ec_site/cartDelete.html", context)
    
    def post(self, request, pk):
        cart_item = ShoppingItemsIncart.objects.get(item_id=pk, user_id=request.session["user_id"])
        cart_item.delete()

        return redirect(reverse("ec_site:cart"))

class UserLogin(View):
    def get(self, request, *args, **kwargs):
        if request.session.get('is_login', None):
            return redirect('/')
        
        login_form = UserLoginForm()
        return render(request, "ec_site/login.html", locals())
        
    def post(self, request, *args, **kwargs):
        login_form = UserLoginForm(request.POST)
        # message = '入力した内容を再度確認してください'
        if login_form.is_valid():
            user_id = login_form.cleaned_data.get('user_id')
            request.session['is_login'] = True
            request.session['user_id'] = user_id
            
            
            user = AccountUser.objects.get(user_id=user_id)
            request.session["name"] = user.name
            return redirect('/')
        else:
            context = {
                "login_form": login_form
            }
            return render(request, 'ec_site/login.html', context)
        
class UserLogout(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('/')
        request.session.flush()
        return redirect('/')
    
    
class UserInfo(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session["user_id"]
        queryset = AccountUser.objects.get(user_id = user_id)
        
        purchase_list = ShoppingPurchase.objects.filter(user__user_id=user_id, cancel=False).order_by("-booked_date").prefetch_related(Prefetch("shoppingpurchasedetail_set",queryset=ShoppingPurchaseDetail.objects.select_related("item")))


        context = {
            "purchase_list": purchase_list,
            "user":queryset,
        }
        return render(request, "ec_site/userInfo.html",context)

class UpdateUserInfo(View):
    def get(self, request, *args, **kwargs):
        user = AccountUser.objects.get(user_id = request.session["user_id"])
        initial_data = {
            "name":user.name,
            "address": user.address,
        }
        form = UpdateUserForm(initial_data)
        context = {
            "form": form,
            "user_id":user.user_id,
        }
        return render(request, "ec_site/updateUser.html",context)
    
    def post(self, request, *args, **kwargs):
        form = UpdateUserForm(request.POST)

        if not form.is_valid():
            context = {
                "form":form,
                "user_id":request.session["user_id"],
            }
            return render(request, "ec_site/updateUser.html",context)
        
        password = form.cleaned_data.get("password")
        name = form.cleaned_data.get("name")
        address = form.cleaned_data.get("address")

        context = {
            "user_id": request.session["user_id"],
            "password": password,
            "name": name,
            "address": address,
        }
        return render(request, "ec_site/updateUserConfirm.html",context)

class UpdateUserConfirm(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ec_site/updateUserConfirm.html")
    
    def post(self, request, *args, **kwargs):
        # form = CreateUserForm(request.POST)
        user = AccountUser()
        user.user_id = request.session["user_id"]
        user.password = request.POST["password"]
        user.name = request.POST["name"]
        user.address = request.POST["address"]
        user.save()

        request.session["name"] = user.name

        context = {
            "user_id": request.session["user_id"],
            "name": user.name,
            "address": user.address,
        }
        return render(request, "ec_site/updateUserCommit.html",context)



class RegisterUser(View):
    def get(self, request, *args, **kwargs):
        form = CreateUserForm()
        context = {
            "form": form
        }
        return render(request, "ec_site/registerUser.html",context)
    
    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)

        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "ec_site/registerUser.html",context)
        
        user = AccountUser()
        user.user_id = form.cleaned_data.get("user_id")
        user.password = form.cleaned_data.get("password")
        user.name = form.cleaned_data.get("name")
        user.address = form.cleaned_data.get("address")

        context = {
            "user_id": user.user_id,
            "password": user.password,
            "name": user.name,
            "address": user.address,
        }

        return render(request, "ec_site/check_registerUser.html", context)
        
class CheckRegisterUser(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ec_site/check_registerUser.html")
    
    def post(self, request, *args, **kwargs):
        # form = CreateUserForm(request.POST)
        user = AccountUser()
        user.user_id = request.POST["user_id"]
        user.password = request.POST["password"]
        user.name = request.POST["name"]
        user.address = request.POST["address"]
        user.save()

        context = {
            "name": user.name
        }
        return render(request, "ec_site/registerUserCommit.html",context)
        

class RegisterUserCommit(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ec_site/check_registerUser.html")
    
class WithdrawConfirm(View):
    def get(self, request, *args, **kwargs):
        user = AccountUser.objects.get(user_id = request.session["user_id"])
        name = user.name
        
        context = {
            "name": name,
        }
        return render(request,"ec_site/withdrawConfirm.html",context)
    
    def post(self, request, *args, **kwargs):
        user = AccountUser.objects.get(user_id = request.session["user_id"])
        name = user.name
        user.delete()
        request.session.flush()

        context = {
            "name": name
        }

        return render(request, "ec_site/withdrawCommit.html",context)

# 管理者ログイン機能
class AdminLogin(View):
    def get(self, request, *args, **kwargs):
        login_form = AdminLoginForm()
        return render(request, "ec_site/adminLogin.html", {"login_form": login_form})

    def post(self, request, *args, **kwargs):
        login_form = AdminLoginForm(request.POST)
        if login_form.is_valid():
            admin_id = login_form.cleaned_data.get("admin_id")

            # セッション管理
            request.session["is_admin_login"] = True
            request.session["admin_id"] = admin_id

            return redirect("/ec_site/adminMain/")
        else:
            return render(request, "ec_site/adminLogin.html", {"login_form": login_form})


class AdminMain(View):
    def get(self, request, *args, **kwargs):
        
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        return render(request, "ec_site/adminMain.html")

class AdminPurchaseLog(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session["user_id"]
        purchase_list = ShoppingPurchase.objects.filter(cancel=False).order_by("-booked_date").prefetch_related(Prefetch("shoppingpurchasedetail_set",queryset=ShoppingPurchaseDetail.objects.select_related("item")))
        user_list = AccountUser.objects.all()
        item_list = ShoppingItem.objects.all()
        context = {
            "purchase_list": purchase_list,
            "user_list": user_list,
            "item_list": item_list,
        }
        return render(request, "ec_site/adminPurchaseLog.html",context)

    def post(self, request, *args, **kwargs):
        
        keyword = request.POST.get("keyword", "").strip()
        purchase_list = ShoppingPurchase.objects.order_by("-booked_date").prefetch_related(
            Prefetch(
                "shoppingpurchasedetail_set",
                queryset=ShoppingPurchaseDetail.objects.select_related("item")
            )
        )

        if keyword:
           purchase_list = purchase_list.filter(
                Q(purchase_id__icontains=keyword) |
                Q(destination__icontains=keyword) |
                Q(user__name__icontains=keyword) |
                Q(shoppingpurchasedetail__item__name__icontains=keyword) |
                Q(shoppingpurchasedetail__item__manufacturer__icontains=keyword) |
                Q(shoppingpurchasedetail__item__color__icontains=keyword)
            ).distinct()
           
        context = {
            "keyword": keyword,
            "purchase_list": purchase_list,
        }
        return render(request, "ec_site/adminPurchaseLog.html", context)