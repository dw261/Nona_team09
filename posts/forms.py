from django import forms
from posts.models import groupsPost, sharingPost

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = groupsPost
        fields = [
            'category',
            'title',
            'content',
            'min_members',
            'price_per',
            'location',
            'deadline',
            'link',
        ]
        widgets = {
            'category'   : forms.Select(attrs={'class': 'form-select'}),
            'title'      : forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목'}),
            'content'    : forms.Textarea(attrs={'class': 'form-control', 'placeholder': '내용', 'rows': 5}),
            'min_members': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price_per'  : forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'location'   : forms.TextInput(attrs={'class': 'form-control', 'placeholder': '거래 장소'}),
            'deadline'   : forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'link'       : forms.URLInput(attrs={'class': 'form-control', 'placeholder': '판매 링크 (선택)'}),
        }


class SharingPostForm(forms.ModelForm):
    class Meta:
        model = sharingPost
        fields = [
            'category',
            'title',
            'content',
            'quantity',
            'location',
            'trade_time',
            'deadline',
        ]
        widgets = {
            'category'  : forms.Select(attrs={'class': 'form-select'}),
            'title'     : forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목'}),
            'content'   : forms.Textarea(attrs={'class': 'form-control', 'placeholder': '내용', 'rows': 5}),
            'quantity'  : forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'location'  : forms.TextInput(attrs={'class': 'form-control', 'placeholder': '거래 장소'}),
            'trade_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'deadline'  : forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }