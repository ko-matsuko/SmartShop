from django.shortcuts import render
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import View
from django.urls import reverse
from ec_site.models import ShoppingCategory,ShoppingItem, ShoppingItemsIncart, AccountUser, ShoppingPurchase, ShoppingPurchaseDetail
from ec_site.forms import UserLoginForm, SearchFormCategory, SearchFormKeyword, CreateUserForm, UpdateUserForm, AdminLoginForm, AdminItemForm
from django.db.models import Prefetch
from datetime import datetime
from ec_site.forms import UserLoginForm, SearchFormCategory, SearchFormKeyword, CreateUserForm, UpdateUserForm, AdminLoginForm
from django.db.models import Q, Prefetch
from django.db.models import Sum
from django.db.models import F
import random

class IndexView(View):
    def get(self, request, *args, **kwargs):
        queryset = ShoppingCategory.objects.all()
        ranking = (ShoppingPurchaseDetail.objects
                .values("item", "item__name")
                .annotate(total_amount=Sum("amount"))
                .order_by("-total_amount")
                )
        context = {
            "category_list": queryset,
            "item_list": ShoppingItem.objects.all().order_by("item_id"),
            "ranking":ranking,
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
        context = {
            "category_list": ShoppingCategory.objects.all(),  # ヘッダーのカテゴリ選択を全カテゴリ表示
        }
        return render(request, "ec_site/search_result.html", context)
    
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
            "item_list": queryset,
            "category_list": ShoppingCategory.objects.all(),  # ヘッダーのカテゴリ選択を全カテゴリ表示
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

        context = {
            "user":queryset,
        }
        return render(request, "ec_site/userInfo.html",context)


class PurchaseHistory(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('/ec_site/userLogin')

        user_id = request.session["user_id"]
        purchase_list = ShoppingPurchase.objects.filter(user__user_id=user_id, cancel=False).order_by("-booked_date").prefetch_related(Prefetch("shoppingpurchasedetail_set", queryset=ShoppingPurchaseDetail.objects.select_related("item")))

        context = {
            "purchase_list": purchase_list,
        }
        return render(request, "ec_site/purchaseHistory.html", context)

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
    

class BuyItem(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")
        user = AccountUser.objects.get(user_id=user_id)
        cart = ShoppingItemsIncart.objects.filter(user_id=user_id)

        total = 0
        for c in cart:
            c.subtotal = c.item.price * c.amount  # 小計を追加
            total += c.subtotal

        context = {
            "cart": cart,
            "total": total,
            "address": user.address,  # お届け先の初期値に登録済み住所を使用
        }

        return render(request, "ec_site/buyItem.html", context)

    def post(self, request, *args, **kwargs):
        # セッションからログインユーザーID取得
        user_id = request.session.get("user_id")
        user = AccountUser.objects.get(user_id=user_id)
        cart = ShoppingItemsIncart.objects.filter(user_id=user_id)

        total = 0
        for c in cart:
            c.subtotal = c.item.price * c.amount  # 小計を追加
            total += c.subtotal

        context = {
            "cart": cart,
            "total": total,
            "address": user.address,  # お届け先の初期値に登録済み住所を使用
        }

        return redirect("ec_site:recommend_items")
    
class RecommendItems(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")
        cart = ShoppingItemsIncart.objects.filter(user_id=user_id)

        # カート内商品のIDを取得（おすすめ候補から除外するため）
        cart_item_ids = [c.item.item_id for c in cart]

        # カート内と同じカテゴリの商品を候補に（カテゴリフィールドがない場合は全商品から）
        recommend_items = (
            ShoppingItem.objects
            .exclude(item_id__in=cart_item_ids)
            .filter(stock__gt=0)
            .order_by("?")[:4]  # ランダムに最大4件
        )

        context = {
            "recommend_items": recommend_items,
        }
        return render(request, "ec_site/recommendItems.html", context)

    def post(self, request, *args, **kwargs):
        # おすすめ商品をカートに追加
        user_id = request.session.get("user_id")
        user = AccountUser.objects.get(user_id=user_id)

        selected_ids = request.POST.getlist("add_items")  # チェックされた商品ID群
        for item_id in selected_ids:
            item = ShoppingItem.objects.get(item_id=item_id)
            cart_entry, created = ShoppingItemsIncart.objects.get_or_create(
                user=user,
                item=item,
                defaults={"amount": 1},
            )
            if not created:
                cart_entry.amount += 1
                cart_entry.save()

        # おすすめをスキップまたは追加後、注文確定へ
        return redirect("ec_site:buy_item_commit_get")

class BuyItemCommitGet(View):
    """注文確定前の最終確認画面（GET）"""
    def get(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")
        user = AccountUser.objects.get(user_id=user_id)
        cart = ShoppingItemsIncart.objects.filter(user_id=user_id)

        total = 0
        for c in cart:
            c.subtotal = c.item.price * c.amount
            total += c.subtotal

        context = {
            "cart": cart,
            "total": total,
            "address": user.address,
        }
        return render(request, "ec_site/buyItem.html", context)
    
class BuyItemCommit(View):
    RANKS = {
        "plain":   {"mascot": "plain.png",   "title": "ご注文を承りました",
                    "message": "ご注文を受け付けました。"},
        "smile":   {"mascot": "welcome.png", "title": "ご注文ありがとうございます",
                    "message": "ご注文を受け付けました。"},
        "delight": {"mascot": "thanks.png",  "title": "たくさんのお買い上げありがとうございます！",
                    "message": "またのご利用を心よりお待ちしております。"},
        "premium": {"mascot": "premium.png", "title": "特別なお客様へ、<br>最大級のありがとうを。",
                    "message": "SmartShopより心ばかりの感謝を込めて。"},
    }

    def rank_for(self, total):
        if total <= 5000:
            return "plain"
        elif total <= 20000:
            return "smile"
        elif total <= 50000:
            return "delight"
        return "premium"

    def post(self, request, *args, **kwargs):
        new_purchase = ShoppingPurchase()
        user_id=request.session.get("user_id")
        user= AccountUser.objects.get(user_id = user_id)
        

        today_str = datetime.now().strftime("%Y%m%d")
        count_today = ShoppingPurchase.objects.filter(purchase_id__startswith=today_str).count()
        sequence = str(count_today + 1).zfill(2)
        purchase_id_str = f"{today_str}{sequence}"
        new_purchase.purchase_id = int(purchase_id_str)
        new_purchase.user = user
        new_purchase.destination = request.POST["address"]
        new_purchase.save()
        
        cart_items = ShoppingItemsIncart.objects.filter(user=user)
        total = 0
        for cart_item in cart_items:
            total += cart_item.item.price * cart_item.amount  # 購入金額の合計
            item = cart_item.item
            item.stock -= cart_item.amount

            if item.stock < 0:
                item.stock = 0

            item.save()

        ShoppingItemsIncart.objects.filter(user=user).delete()

        rank = self.rank_for(total)  # 金額からランク判定
        context={
            "purchase":new_purchase,
            "total": total,
            "rank": rank,
        }
        context.update(self.RANKS[rank])
        return render(request, "ec_site/buyItemCommit.html", context)


class AdminItemList(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        category_list = ShoppingCategory.objects.all()
        queryset = ShoppingItem.objects.all().order_by("item_id")

        keyword = request.GET.get("keyword", "")
        category_id = request.GET.get("category", "0")

        if keyword:
            queryset = queryset.filter(name__icontains=keyword)

        if category_id != "0":
            queryset = queryset.filter(category_id=category_id)

        context = {
            "category_list": category_list,
            "item_list": queryset,
            "keyword": keyword,
            "selected_category": category_id,
        }
        return render(request, "ec_site/adminItemList.html", context)
    
class AdminRecommendUpdate(View):
    def post(self, request, pk, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        item = ShoppingItem.objects.get(pk=pk)

        # チェックON時だけ "on" が来る
        item.recommended = "recommended" in request.POST
        item.save()

        keyword = request.POST.get("keyword", "")
        category = request.POST.get("category", "0")
        return redirect(f"/ec_site/adminItemList/?keyword={keyword}&category={category}")

class AdminItemDelete(View):
    def post(self, request, pk, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        item = ShoppingItem.objects.get(pk=pk)
        item.delete()

        keyword = request.POST.get("keyword", "")
        category = request.POST.get("category", "0")
        return redirect(f"/ec_site/adminItemList/?keyword={keyword}&category={category}")

class AdminItemCreate(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        form = AdminItemForm()
        return render(request, "ec_site/adminItemCreate.html", {"form": form})

    def post(self, request, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        form = AdminItemForm(request.POST)
        if not form.is_valid():
            return render(request, "ec_site/adminItemCreate.html", {"form": form})

        item = ShoppingItem()
        item.category_id = form.cleaned_data["category"].category_id
        item.name = form.cleaned_data["name"]
        item.manufacturer = form.cleaned_data["manufacturer"]
        item.color = form.cleaned_data["color"]
        item.price = form.cleaned_data["price"]
        item.stock = form.cleaned_data["stock"]
        item.recommended = form.cleaned_data["recommended"]
        
        last_item = ShoppingItem.objects.order_by('-item_id').first()
        if last_item:
            item.item_id = last_item.item_id + 1
        else:
            item.item_id = 1

        item.save()

        return redirect("/ec_site/adminItemList/")

class AdminItemUpdate(View):
    def get(self, request, pk, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        item = ShoppingItem.objects.get(pk=pk)
        initial_data = {
            "category": item.category_id,
            "name": item.name,
            "manufacturer": item.manufacturer,
            "color": item.color,
            "price": item.price,
            "stock": item.stock,
            "recommended": item.recommended,
        }
        form = AdminItemForm(initial=initial_data)
        context = {
            "form": form,
            "item_id": item.item_id,
        }
        return render(request, "ec_site/adminItemUpdate.html", context)

    def post(self, request, pk, *args, **kwargs):
        if not request.session.get("is_admin_login"):
            return redirect("/ec_site/adminLogin/")

        item = ShoppingItem.objects.get(pk=pk)
        form = AdminItemForm(request.POST)

        if not form.is_valid():
            return render(request, "ec_site/adminItemUpdate.html", {
                "form": form,
                "item_id": item.item_id,
            })

        item.category_id = form.cleaned_data["category"].category_id
        item.name = form.cleaned_data["name"]
        item.manufacturer = form.cleaned_data["manufacturer"]
        item.color = form.cleaned_data["color"]
        item.price = form.cleaned_data["price"]
        item.stock = form.cleaned_data["stock"]
        item.recommended = form.cleaned_data["recommended"]
        item.save()

        return redirect("/ec_site/adminItemList/")


class AdminLogout(View):
    def get(self, request, *args, **kwargs):
        request.session.flush()
        return redirect("/ec_site/adminLogin/")

class AdminPurchaseLog(View):
    def get(self, request, *args, **kwargs):
        status = request.GET.get("status", "active")  # active / canceled

        purchase_list = ShoppingPurchase.objects.all().order_by("-booked_date").prefetch_related(
            Prefetch(
                "shoppingpurchasedetail_set",
                queryset=ShoppingPurchaseDetail.objects.select_related("item")
            )
        )

        if status == "canceled":
            purchase_list = purchase_list.filter(cancel=True)
        else:
            purchase_list = purchase_list.filter(cancel=False)

        for purchase in purchase_list:
            for d in purchase.shoppingpurchasedetail_set.all():
                d.total_price = d.item.price * d.amount

        context = {
            "purchase_list": purchase_list,
            "status": status,
        }
        return render(request, "ec_site/adminPurchaseLog.html", context)

    def post(self, request, *args, **kwargs):

        cancel_id = request.POST.get("cancel_id")
        status = request.POST.get("status", "active")

        if cancel_id:
            purchase = ShoppingPurchase.objects.prefetch_related(
                Prefetch(
                    "shoppingpurchasedetail_set",
                    queryset=ShoppingPurchaseDetail.objects.select_related("item")
                )
            ).filter(purchase_id=cancel_id).first()

            # まだキャンセルされていないときだけ実行
            if purchase and not purchase.cancel:
                for detail in purchase.shoppingpurchasedetail_set.all():
                    # 在庫を戻す
                    ShoppingItem.objects.filter(
                        item_id=detail.item.item_id
                    ).update(stock=F("stock") + detail.amount)

                # キャンセルフラグを立てる
                purchase.cancel = True
                purchase.save()

                
        keyword = request.POST.get("keyword", "").strip()

        purchase_list = ShoppingPurchase.objects.all().order_by("-booked_date").prefetch_related(
            Prefetch(
                "shoppingpurchasedetail_set",
                queryset=ShoppingPurchaseDetail.objects.select_related("item")
            )
        )

        if status == "canceled":
            purchase_list = purchase_list.filter(cancel=True)
        else:
            purchase_list = purchase_list.filter(cancel=False)

        for purchase in purchase_list:
            for d in purchase.shoppingpurchasedetail_set.all():
                d.total_price = d.item.price * d.amount

        if keyword:
            purchase_list = purchase_list.filter(
                Q(purchase_id__icontains=keyword) |
                Q(destination__icontains=keyword) |
                Q(user__name__icontains=keyword) |
                Q(shoppingpurchasedetail__item__name__icontains=keyword)
            ).distinct()

        context = {
            "keyword": keyword,
            "purchase_list": purchase_list,
            "status": status,
        }
        return render(request, "ec_site/adminPurchaseLog.html", context)
