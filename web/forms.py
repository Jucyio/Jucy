from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class FeedbackForm(forms.Form):
    title = forms.CharField(label='Feedback title', max_length=100)
    content = forms.CharField(label='Feedback content', max_length=100)

class AnswerForm(forms.Form):
    content = forms.CharField(label='Answer content', max_length=100)

class _EmailForm(forms.ModelForm):
    user = None
    def __init__(self, *args, **kwargs):
        super(_EmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

class EmailForm(_EmailForm):
    class Meta:
        model = User
        fields = ('email',)

class EmailPasswordForm(_EmailForm):
    def __init__(self, *args, **kwargs):
        super(EmailPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = User.objects.get(email=email)
            if not self.user.check_password(password):
                raise forms.ValidationError(_('Please enter a correct username and password. Note that both fields may be case-sensitive.'),
                                            code='invalid_login')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email', 'password')
