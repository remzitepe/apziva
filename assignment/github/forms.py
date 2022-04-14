from django import forms

class GithubKeywords(forms.Form):
    keyword = forms.CharField()
    candidate_num = forms.IntegerField()
    sorting = forms.CharField()
    sort_type = forms.CharField()
class StackoverflowKeywords(forms.Form):
    keyword = forms.CharField()
    candidate_num = forms.IntegerField()
