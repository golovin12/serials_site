from django import forms


class Search_Form(forms.Form):
    search = forms.CharField(label='Поиск')
