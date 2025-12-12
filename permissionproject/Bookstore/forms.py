
from django.forms import ModelForm
from Bookstore.models import Chat, Book, User
from django import forms


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('message',)


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'publisher', 'year', 'uploaded_by', 'desc', 'pdf1', 'pdf2', 'cover')        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')