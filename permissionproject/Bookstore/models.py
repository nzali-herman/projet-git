from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone


#User = get_user_model()
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_utilisateur=models.BooleanField(db_default=False)
    is_consultant=models.BooleanField(default=False)
    class Meta:
        swappable='AUTH_USER_MODEL'
class Book(models.Model):
    title=models.CharField(max_length=100)  
    author=models.CharField(max_length=100) 
    year=models.CharField(max_length=100) 
    publisher=models.CharField(max_length=200) 
    desc=models.CharField(max_length=100)  
    uploaded_by=models.CharField(max_length=100, null=True, blank=True)     
    user_id=models.CharField(max_length=100, null=True, blank=True)
    pdf1=models.FileField(upload_to='pdfs/', null=True, blank=True)
    pdf2 = models.FileField(upload_to='pdfs/', null=True, blank=True)  # Allows NULL temporarily
    
    cover=models.ImageField(upload_to='covers/', null=True, blank=True)

    def __str__(self):
       return self.title
   
def delete(self, *args, **kwargs):
    # Supprimer les fichiers PDF
    if self.pdf1:
        self.pdf1.delete()
    if self.pdf2:
        self.pdf2.delete()
    if self.pdf3:
        self.pdf3.delete()
    if self.pdf4:
        self.pdf4.delete()

    # Supprimer la couverture
    if self.cover:
        self.cover.delete()

    # Appeler la méthode `delete` du modèle parent
    super().delete(*args, **kwargs)

    
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now=True, null=True)
    
    def get_posted_at_local(self):
        if self.posted_at:
            # Convertir posted_at en heure locale
            return self.posted_at.astimezone(timezone.get_current_timezone())
        return None




    def __str__(self):
        return str(self.message)
class DeleteRequest(models.Model):
    delete_request = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.delete_request
    


class Feedback(models.Model):
    feedback = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.feedback