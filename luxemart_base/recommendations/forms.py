# recommendations/forms.py
# BRANCHE : feature/auth-onboarding — Personne A

from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control', 'autocomplete': 'given-name'}),
        label='Prénom'
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control', 'autocomplete': 'family-name'}),
        label='Nom'
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control', 'autocomplete': 'username'}),
        label="Nom d'utilisateur"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-control', 'autocomplete': 'email'}),
        label='Email'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe (min. 8 caractères)', 'class': 'form-control'}),
        label='Mot de passe',
        min_length=8
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe', 'class': 'form-control'}),
        label='Confirmer le mot de passe'
    )
    accept_terms = forms.BooleanField(
        required=True,
        label="J'accepte les conditions d'utilisation",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        if len(username) < 3:
            raise forms.ValidationError("Le nom d'utilisateur doit avoir au moins 3 caractères.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1', '')
        p2 = cleaned.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-control', 'autocomplete': 'email'}),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': 'form-control'}),
        label='Mot de passe'
    )


class VerifyCodeForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-control'}),
        label='Votre email'
    )
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'class': 'form-control code-input',
            'maxlength': '6',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'autocomplete': 'one-time-code'
        }),
        label='Code de vérification (6 chiffres)'
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit():
            raise forms.ValidationError("Le code doit contenir uniquement des chiffres.")
        return code


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Prénom'
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nom'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label='Photo de profil'
    )
