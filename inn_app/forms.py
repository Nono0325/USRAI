from django import forms
from .models import Registration
from django.utils.html import strip_tags
import re

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'phone', 'email', 'gender', 'headcount']

    def __init__(self, *args, **kwargs):
        # View 層會將 course instance 傳遞進來，以利進行重複報名驗證
        self.course_instance = kwargs.pop('course_instance', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # [資安防護] 強制過濾所有 HTML 與 Scripts，防止 XSS 攻擊
            clean_name = strip_tags(name)
            if not clean_name.strip():
                raise forms.ValidationError("姓名不能為空或僅包含非法代碼。")
            return clean_name
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # [資安防護] 電話號碼只能輸入數字與特定常用符號
            if not re.match(r'^[\d\-+]+$', phone):
                raise forms.ValidationError("電話號碼格式有誤，僅開放輸入數字、減號(-)與加號(+)。")
            if len(phone) > 20:
                raise forms.ValidationError("電話號碼總長度不可超過 20 個字元。")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        
        # 取得表單實體化的該課程物件
        course = self.course_instance
        
        if course:
            # [佔位器防護] 檢查資料庫是否原本就有一樣電話或是 Email 的人對這個課程報名
            query = Registration.objects.filter(course=course)
            
            # 若電話或 Email 已存於該課程，則阻擋
            if phone and query.filter(phone=phone).exists():
                raise forms.ValidationError("此電話號碼已經成功報名過本課程，無法重複報名！")
            
            if email and query.filter(email=email).exists():
                raise forms.ValidationError("此 Email 已經成功報名過本課程，無法重複報名！")
                    
        return cleaned_data
