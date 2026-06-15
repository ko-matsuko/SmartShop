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
        return cleaned_data
        
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
    
class CreateUserForm(forms.Form):
    user_id = forms.CharField(label = "会員ID:", max_length=128)
    password = forms.CharField(label = "パスワード:", max_length=256)
    password_check = forms.CharField(label = "パスワード:", max_length=256)
    name = forms.CharField(label="お名前:", max_length=128)
    address = forms.CharField(label="ご住所:", max_length=256)

    def clean_user_id(self):
        user_id = self.cleaned_data["user_id"]
        
        if AccountUser.objects.filter(user_id = user_id).exists():
            raise forms.ValidationError("そのユーザIDは既に存在します")
        return user_id
    
    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('password_check')

        if AccountUser.objects.filter(user_id = user_id).exists():
            raise forms.ValidationError("そのユーザIDは既に存在します")
        
        if password1 != password2:
            raise forms.ValidationError("パスワードと確認用パスワードが一致しません")
        
        return cleaned_data
    

