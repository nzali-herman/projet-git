from django.forms import ModelForm
from django import forms
from procedure_app.models import  User, Dossier, PieceJointe, Chat


 #  classe pour le formulaire qui recupère les inforations des cleints#
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        

 #  classe pour le formulaire qui recupère les inforations des dossiers# 
class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = [
            'nom',
            'contact',
            'type_affaire',
            'adversaire',
            'description_affaire',
            
        ]

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'type_affaire': forms.TextInput(attrs={'class': 'form-control'}),
            'adversaire': forms.TextInput(attrs={'class': 'form-control'}),
            'description_affaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        
class PieceJointeUpdateForm(forms.ModelForm):
    class Meta:
        model = PieceJointe
        fields = ['fichier']
            
            
            
# formulaire pour chat #
class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('message',)