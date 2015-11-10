from django import forms

class FeedbackForm(forms.Form):
    title = forms.CharField(label='Feedback title', max_length=100)
    content = forms.CharField(label='Feedback content', max_length=100)

class AnswerForm(forms.Form):
    content = forms.CharField(label='Answer content', max_length=100)
