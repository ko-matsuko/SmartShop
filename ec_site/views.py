from django.shortcuts import render
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import View
from ec_site.models import ShoppingCategory,ShoppingItem
from ec_site.forms import UserLoginForm, SearchFormCategory, SearchFormKeyword


class IndexView(View):
    def get(self, request, *args, **kwargs):
        form_category = SearchFormCategory()
        form_keyword = SearchFormKeyword()

        context = {
            "form_category": form_category,
            "form_keyword": form_keyword,
        }
        return render(request, "ec_site/main.html",context)
    
    # def post(self, request, *args, **kwargs):
    #     if request["flag"]:

    
class SearchResult(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ec_site/search_result.html")
    
    def post(self, request, *args, **kwargs):
        form_category = SearchFormCategory(request.POST)
        form_keyword = SearchFormKeyword(request.POST)

        if not form_category.is_valid() or not form_keyword.is_valid():
            return render(request, "ec_site/main.html")
        
        category_name = form_category.cleaned_data.get("category_name")
        keyword = form_keyword.cleaned_data.get("keyword")

        category = ShoppingCategory.objects.get(name = category_name)
        # queryset = ShoppingItem.objects.filter(category = category.category_id, name__icontains = keyword)
        queryset = ShoppingItem.objects.filter(category = category.category_id)


        print(category.category_id, queryset, end="\n")

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
    def get(self, request):
        return render(request, "ec_site/cart.html")
    
    def post(self, request, pk):
        queryset = ShoppingItem.objects.get(pk=pk)
        item_amount = request.POST["amount"]
        charge = int(queryset.price)*int(item_amount)

        print(queryset.price, item_amount, end="")

        context = {
            "item": queryset,
            "amount": item_amount,
            "charge": charge,
        }
        return render(request, "ec_site/cart.html", context)

class UserLogin(View):
    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        context = {
            "form": form
        }
        return render(request, "ec_site/login.html", context)
    
    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)

        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "ec_site/login.html", context)
        
        name = form.cleaned_data["name"]
        flag = True
        context = {
            "name": name,
            "flag": flag,
        }
        return render(request, "ec_site/main.html", context)