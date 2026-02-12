from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User




# Create your models here.

# classe de differentes rôle utilisateur #
class User(AbstractUser):
    est_administrateur = models.BooleanField(default=False)
    est_consultant = models.BooleanField(default=False)
    est_client = models.BooleanField(default=False)
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'
# classe d'ajout des pièces de dossiers #     
from django.contrib.auth import get_user_model


User = get_user_model()

class Dossier(models.Model):
    nom = models.CharField(max_length=100)  
    contact = models.CharField(max_length=100) 
    type_affaire = models.CharField(max_length=100) 
    adversaire = models.CharField(max_length=200) 
    description_affaire = models.TextField()  # Changé en TextField pour plus de contenu
    
    telecharger_par = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dossiers')
    couverture_dossier = models.ImageField(upload_to='covers/', null=True, blank=True)
    
   
    def __str__(self):
        return self.nom


# Ajouter après la classe Dossier existante


class AnalyseJuridique(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='analyses_juridiques')
    nature_juridique = models.TextField(default='')
    demarches_recommandees = models.TextField(default='')
    delais_importants = models.TextField(default='')
    recommandations = models.TextField(default='')
    procedure_complete = models.TextField(default='')
    risques_juridiques = models.TextField(blank=True, default='')
    textes_applicables = models.TextField(blank=True, default='')
    questions_frequentes = models.TextField(blank=True, default='')
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analyse pour {self.dossier.nom}"

class ChatQuestion(models.Model):
    analyse = models.ForeignKey(AnalyseJuridique, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(default='')
    reponse = models.TextField(default='')
    date_question = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q: {self.question[:50]}..."



# Ajoutez ces modèles après votre modèle Dossier existant



# classe pour les pièces jointes #
class PieceJointe(models.Model):
    dossier = models.ForeignKey(
        'Dossier', 
        on_delete=models.CASCADE, 
        related_name='pieces_jointes'  # nom plus clair
    )
    fichier = models.FileField(upload_to='pieces_jointes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    depuis_formulaire_ajout_piecejointe_dossier_par_admin = models.BooleanField(default=False)  # <-- nouveau

    def __str__(self):
        return f"Pièce - {self.fichier.name}"
   
   # Propriété pour afficher la date en format français
    @property
    
    def uploaded_fr(self):
        return self.uploaded_at.strftime("%d/%m/%Y %H:%M")
   
# classe pour les avis des clients  #

class Feedback(models.Model):
    avis = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.feedback   
   
      
# class pour conversation pour chaque client # 
class Conversation(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation avec {self.client.username}"
    
# class de chat pour chaque client #
class Chat(models.Model):
    conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        related_name='messages',
        
    )
    dossier = models.ForeignKey(
    'Dossier',
    on_delete=models.CASCADE,
    related_name='chats',
    null=True,
    blank=True  # permet aux anciennes lignes de passer
     )


    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)


    @property
    def uploaded_fr2(self):
        return self.posted_at.strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"{self.sender.username} : {self.message[:20]}"
    
    
# class de demande de suppression d'un dossier #
class DeleteRequest(models.Model):
    delete_request = models.CharField(max_length=100, null=True, blank=True)

def __str__(self):
    return self.delete_request