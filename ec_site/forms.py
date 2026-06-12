from django import forms
from ec_site.models import AccountUser, ShoppingCategory

class UserLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    user_id = forms.CharField(label = "会員ID", max_length=128)
    password = forms.CharField(label = "ユーザパスワード", max_length=256)

    def clean(self):
        cleaned_data = super().clean()
        value_id = cleaned_data.get('user_id')
        value_pass = cleaned_data.get('password')
        if not AccountUser.objects.filter(user_id = value_id, password = value_pass).exists():
            raise forms.ValidationError("ユーザ名かパスワードが正しくありません。")
        
class SearchFormCategory(forms.Form):
    category_name = forms.ModelChoiceField(
        ShoppingCategory.objects.order_by('category_id'),
        label = 'カテゴリ', to_field_name="category_id", initial='1'
    )
    def clean_category_name(self):
        value = self.cleaned_data["category_name"]
        return value

class SearchFormKeyword(forms.Form):
    keyword = forms.CharField(label = "キーワード", max_length=36)
    def clean_keyword(self):
        value = self.cleaned_data["keyword"]

        # if len(value) < 4:
        #     raise forms.ValidationError("%(min_length)s 文字以上で入力してください", params={"min_length":4})
        return value


# class UserCreateForm(forms.Form):
#     name = forms.CharField(label = "ユーザ名", max_length=255)
#     password = forms.CharField(label = "ユーザパスワード", max_length=255)

#     def clean_password(self):
#         value = self.cleaned_data["password"]

#         if len(value) < 4:
#             raise forms.ValidationError("%(min_length)s 文字以上で入力してください", params={"min_length":4})
#         return value