from django.db import models

# Create your models here.
class AccountUser(models.Model):
    class Meta:
        db_table = "account_user"
        indexes = [
            models.Index(fields=["user_id"]),
        ]

    user_id = models.CharField(verbose_name="会員ID", max_length=128, primary_key=True)
    password = models.CharField(verbose_name="パスワード", max_length=256)
    name = models.CharField(verbose_name="名前",max_length=128)
    address = models.CharField(verbose_name="住所",max_length=256)

    def __str__(self):
        return self.user_id



class ShoppingCategory(models.Model):
    class Meta:
        db_table = "shopping_category"
        indexes = [
            models.Index(fields=["category_id"]),
        ]

    category_id = models.IntegerField(verbose_name="カテゴリID", primary_key=True)
    name = models.CharField(verbose_name="カテゴリ名", max_length=256)
    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    class Meta:
        db_table = "shopping_item"
        indexes = [
            models.Index(fields=["item_id"]),
        ]

    item_id = models.IntegerField(verbose_name="商品ID", primary_key=True)
    name = models.CharField(verbose_name="商品名",max_length=128)
    manufacturer = models.CharField(verbose_name="メーカー名",max_length=32)
    color = models.CharField(verbose_name="商品の色",max_length=16)
    price = models.IntegerField(verbose_name="価格")
    stock = models.IntegerField(verbose_name="在庫数")
    recommended = models.BooleanField(verbose_name="オススメ", max_length=1, default=False)
    category = models.ForeignKey(ShoppingCategory, verbose_name="カテゴリID", on_delete=models.CASCADE)


class ShoppingItemsIncart(models.Model):
    class Meta:
        db_table = "shopping_itemsincart"

    amount = models.IntegerField(verbose_name="数量")
    booked_date = models.DateTimeField(verbose_name="登録日", auto_now_add=True)
    item = models.ForeignKey(ShoppingItem,verbose_name="商品ID", on_delete=models.CASCADE)
    user = models.ForeignKey(AccountUser, verbose_name="会員ID", on_delete=models.CASCADE)
    

class ShoppingPurchase(models.Model):
    class Meta:
        db_table = "shopping_purchase"
        indexes = [
            models.Index(fields=["purchase_id"]),
        ]

    purchase_id = models.IntegerField(verbose_name="注文ID", primary_key=True)
    destination = models.CharField(verbose_name="配送先", max_length=256)
    booked_date = models.DateTimeField(verbose_name="注文日", auto_now_add=True)
    cancel = models.BooleanField(verbose_name="キャンセル", default=False)
    user = models.ForeignKey(AccountUser, verbose_name="注文者", on_delete=models.CASCADE)

class ShoppingPurchaseDetail(models.Model):
    class Meta:
        db_table = "shopping_purchasedetail"
        indexes = [
            models.Index(fields=["purchase_detail_id"]),
        ]
    
    purchase_detail_id = models.IntegerField(verbose_name="注文詳細ID", primary_key=True)
    amount = models.IntegerField(verbose_name="注文数")
    item = models.ForeignKey(ShoppingItem,verbose_name="商品ID", on_delete=models.CASCADE)
    purchase = models.ForeignKey(ShoppingPurchase,verbose_name="注文ID", on_delete=models.CASCADE)


class AdministratorAdmin(models.Model):
    class Meta:
        db_table = "administrator_admin"
        indexes = [
            models.Index(fields=["admin_id"]),
        ]

    admin_id = models.CharField(verbose_name="管理者ID", max_length=128, primary_key=True)
    password = models.CharField(verbose_name="パスワード", max_length=256)




