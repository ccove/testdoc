from django import forms

class FileUploadForm(forms.Form):
    selvalue = (
        ('one','教 学 资 源'),
        ('two','课 程 内 容'),
        ('three','学 生 作 业'),
        ('four','普 通 文 档'),
        ('five','其 他 文 档'),
    )
    file_name = forms.CharField(label="文档名称", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(label="文档",widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    file_classify = forms.CharField(label="文档分类",max_length=32,widget=forms.widgets.Select(choices=selvalue))
