from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import User, Feedback, Dossier, PieceJointe, Chat, Conversation, DeleteRequest
from django.contrib import messages, auth
from django.contrib.auth import authenticate, logout
from django.views import generic
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import UserForm, PieceJointeUpdateForm, DossierForm, ChatForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.





# fonction qui retourne la page register.html #

def register_page(request):
    return render(request, 'register.html')

# fonction qui retourne le dashboard de l'administrateur #

def dashboard_administrateur(request):
    dossier = Dossier.objects.all().count()
    utilisateur = User.objects.all().count()
    
     
    context = {'dossier':dossier, 'utilisateur':utilisateur} 
    return render(request, 'dashboard_admin/dashboard_admin.html', context)

# fonction qui retourne le dashboard du consultant #
def dashboard_consultant(request):
    return render(request, 'dashboard_consultant/dashboard_consultant.html')

# fonction qui retourne le dashboard du client #
def dashboard_client(request):
    return render(request, 'dashboard_client/dashboard_client.html')

# fonction qui retourne la page login.html #

def login_page(request):
    return render(request, 'login.html')

# fonction qui enregistre les données lors de l'inscription #
def register_view(request):
    if request.method == 'POST':
       username = request.POST['username'] 
       email = request.POST['email']
       password = request.POST['password']
       password = make_password(password)
       
       a = User(username=username, email=email, password=password)
       a.save()
       messages.success(request, 'Inscription réussie avec succès')
       return redirect('login_page')
    else:
        messages.error(request, "Inscription échouée. Veillez réessayer.")  
        return redirect('register_page') 
    
# fonction qui permet de se connecter selon le rôle l'utilisater #

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(
                request,
                "Nom d'utilisateur ou mot de passe incorrect."
            )
            return render(request, "login.html")

        if not user.is_active:
            messages.error(request, "Compte désactivé.")
            return render(request, "login.html")

        # Connexion
        auth.login(request, user)

        # Redirections par rôle
        if getattr(user, "est_administrateur", False) or user.is_superuser:
            return redirect("dashboard_administrateur")

        if getattr(user, "est_consultant", False):
            return redirect("dashboard_consultant")

        # Par défaut
        return redirect('client_view_list_dossier')

    # Requête GET
    return render(request, "login.html")
# fonction de déconnexion #
def logout_view(request):
    logout(request)
    return redirect('login_page')

###  dashboard administrateur de l'application ### 

# class qui permet a l'admin de voir la liste des utilisateur #
class admin_view_liste_clients(generic.ListView):
    model = User
    template_name = 'dashboard_admin/clients/liste_clients.html'
    context_object_name = 'clients'
    paginate_by = 5
    def get_queryset(self):
        return User.objects.order_by('-id')
    

    
    
    
    
# fonction de la page de creation de l'utilisateur #  
def create_user_form(request):
    choice = ['1', '0', 'client', 'administrateur', 'consultant']
    choice = {'choice': choice}
    return render(request, 'dashboard_admin/clients/ajouter_client.html', choice)  
    
# fonction qui permet de a l'admin de creer un utilicateur et l'attribuer un role #
def admin_create_user(request):
    choice = ['1', '0', 'client', 'administrateur', 'consultant']
    choice = {'choice': choice}
    if request.method == 'POST':
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            username=request.POST['username']
            userType=request.POST['userType']
            email=request.POST['email']
            password=request.POST['password']
            password = make_password(password)
            print("User Type")
            print(userType)
            if userType == "client":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, est_client=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('admin_view_liste_clients')
            elif userType == "administrateur":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, est_administrateur=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('admin_view_liste_clients')
            elif userType == "consultant":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, est_consultant=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('admin_view_liste_clients')    
            else:
                messages.error(request, "Erreur lors de la céation de l'utilisateur. Veillez réessayer.")
                return redirect('create_user_form')
    else:
        
        return redirect('create_user_form')

# fonction qui permet de voir les detailles des utilisateurs #
class admin_view_detail_user(DetailView):
    model = User
    template_name = 'dashboard_admin/clients/detail_client.html' 
    
# classe  qui permet a l'administrateur de midifier les information des clients #
class admin_edit_user(SuccessMessageMixin, UpdateView):
   model  = User
   form_class = UserForm
   template_name = 'dashboard_admin/clients/modifier_client.html'
   success_url = reverse_lazy('admin_view_liste_clients')
   success_message = "Les informations ont été modifiées avec siccèes."
   
# classe qui permet a l'administrateur de supprimer un utilisateur #
class admin_delete_user(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard_admin/clients/confirmer_suppression_client.html'
    success_url = reverse_lazy('admin_view_liste_clients')
    success_message = "Données supprimées avec succès"
   
# classe qui permet a l'administrateur de vor les avis 
class admin_view_avis(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'dashboard_admin/clients/avis_clients.html'
    context_object_name = 'feedbacks'
    def get_queryset(self):
        return Feedback.objects.order_by('id')
       
# classe qui permet a l'administrateur de voir les dossiers des clients #
class admin_view_list_dossiers_clients(LoginRequiredMixin, ListView):
    model = Dossier
    template_name = 'dashboard_admin/dossiers/liste_dossiers_clients.html'
    context_object_name = 'dossiers'
    
    def get_queryset(self):
        return Dossier.objects.order_by('-id')
    
# class qui permet a l'administrateur gerer les doissiers des clients #
class admin_namage_dossier(LoginRequiredMixin, ListView):
    model = Dossier
    template_name = "dashboard_admin/dossiers/gestion_dossiers.html"
    context_object_name = "dossiers"
    paginate_by = 3
    
    def get_queryset(self):
         return Dossier.objects.order_by('-id')
    
 # fonction qui permet a l'admin de voir les details du dossier #
   

def voir_detail_dossier(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)

    # grâce au related_name='pieces_jointes'
    pieces_jointes = dossier.pieces_jointes.all()

    context = {
        'dossier': dossier,
        'pieces_jointes': pieces_jointes,
    }

    return render(request, 'dashboard_admin/dossiers/gestion_dossier.html', context)
       
# class qui permet a l'administrateur de modofier un dossier #
class admin_edit_dossier(LoginRequiredMixin, UpdateView):
    model = Dossier
    form_class = DossierForm
    template_name = 'dashboard_admin/dossiers/modifier_dossier.html'
    success_url = reverse_lazy('admin_namage_dossier')
    success_message = "Le dossier a été modifié avec succès."

# fonction qui permet a l'administrateur de supprimer une piece jointe #
def supprimer_piece_jointe(request, pk):
    piece = get_object_or_404(PieceJointe, pk=pk)

    if request.method == 'POST':
        piece.fichier.delete(save=False)  # supprime le fichier du disque
        piece.delete()                     # supprime l'objet
        messages.success(request, "Pièce jointe supprimée avec succès.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

# fonction qui permet a l'administrateur de supprimer un dossier entier #
def supprimer_dossier_client(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)

    if request.method == 'POST':
        dossier.delete()  # supprime le fichier du disque
                        # supprime l'objet
        messages.success(request, "Dossier  supprimée avec succès.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
    
# fonction qui permet a l'administrateur d'ajouter les pièces jointes liées à un dossier #    
def ajouter_piece_jointe(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)

    if request.method == "POST":
        fichier = request.FILES.get("fichier")

        if fichier:
            PieceJointe.objects.create(
                dossier=dossier,
                fichier=fichier,
                depuis_formulaire_ajout_piecejointe_dossier_par_admin=True  # <-- marqué comme ajouté via ce formulaire
            )

    return redirect(request.META.get('HTTP_REFERER', '/'))


# class qui permet a l'administrateur de voir la liste des commentaires #
class admin_view_feedback_client(LoginRequiredMixin, ListView):
    model = Feedback
    
    template_name = 'dashboard_admin/clients/avis_clients.html'
    context_object_name = 'feedbacks'
    
    
    # paginate_by = 3

    def get_queryset(self):
        return Feedback.objects.order_by('-id')  
    
    
# class qui permet a l'admin de voir la liste des conversations #
class AdminConversationList(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'dashboard_admin/chats/conversations.html'
   
    


# admin repond à une conversation
@login_required
def admin_dossier_chat(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)

    # Une conversation par client
    conversation = get_object_or_404(
        Conversation,
        client=dossier.telecharger_par   # ⚠️ adapte si ton champ client s'appelle autrement
    )

    if request.method == "POST":
        msg = request.POST.get("message", "").strip()
        if msg:
            Chat.objects.create(
                conversation=conversation,
                dossier=dossier,
                sender=request.user,
                message=msg
            )
        return redirect('admin_dossier_chat', dossier_id=dossier.id)

    # 🔑 ICI EST LA CLÉ : filtrage PAR DOSSIER
    messages = Chat.objects.filter(
        conversation=conversation,
        dossier=dossier
    ).order_by('posted_at')

    return render(request, 'dashboard_admin/chats/conversations.html', {
        'dossier': dossier,
        'messages': messages
    })
    



# class qui permet a l'admin de voir les demandes de suppression de dossiers #
class admin_view_delete_request(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'dashboard_admin/dossiers/demande_suppression_dossier.html'
    context_object_name = 'feedbacks'
    
    

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')   
    
    
# function qui permet de supprimer une conversation #
def supprimer_chat_client(request, pk):
    chat = get_object_or_404(Chat, pk=pk)

    if request.method == 'POST':
        chat.delete()  # supprime le fichier du disque
                        # supprime l'objet
        messages.success(request, "message  supprimée avec succès.")

    return redirect(request.META.get('HTTP_REFERER', '/'))     

# views.py - Vue pour la modification
def modifier_chat_client(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    
    if request.method == 'POST':
        nouveau_message = request.POST.get('message')
        if nouveau_message and nouveau_message.strip():
            chat.message = nouveau_message.strip()
            chat.save()
            messages.success(request, "Message modifié avec succès.")
        else:
            messages.error(request, "Le message ne peut pas être vide.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
# dashboard du client # 



# fonction de la page de formulaire de dossier #
def client_view_page_dossier_form(request):
    return render(request, 'dashboard_client/dossiers/ajouter_dossier.html')


# fonction qui permet au client d'ajouter un dossier #

@login_required
def client_ajout_dossier(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        contact = request.POST['contact']
        type_affaire = request.POST['type_affaire']
        adversaire = request.POST['adversaire']
        description_affaire = request.POST['description_affaire']
        couverture_dossier = request.FILES.get('couverture_dossier', None)
       
        curent_user = request.user  # Objet User
       
        
      
        # Créer le dossier avec l'utilisateur actuel
        dossier = Dossier(
            nom=nom,
            contact=contact,
            type_affaire=type_affaire,
            adversaire=adversaire,
            description_affaire=description_affaire,
            couverture_dossier=couverture_dossier,
            telecharger_par=curent_user,
           
            
        )
        dossier.save()
        messages.success(request, 'Le dossier a été téléchargé avec succès.')
        return redirect('client_view_list_dossier')
    else:
        messages.error(request, 'Le dossier n’a pas été téléchargé avec succès.')
        return redirect('client_view_page_dossier_form')
   
# fonctionqui permet au client de voir la liste des dossiers recement ajouter #
class client_view_list_dossier(ListView):
    model = Dossier
    template_name = 'dashboard_client/dashboard_client.html'
    context_object_name = 'dossiers'
    

    def get_queryset(self):
        # Filtrer les livres pour l'utilisateur actuellement connecté
        return Dossier.objects.filter(telecharger_par=self.request.user).order_by('-id')
   
    



# fonction pour les pieces jointes associers au dossier #
def ajouter_pieces_jointes(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
   

    if request.method == 'POST':
        fichiers = request.FILES.getlist('fichiers')
        for fichier in fichiers:
            PieceJointe.objects.create(dossier=dossier, fichier=fichier)
               
            
        return redirect('client_view_list_dossier', )

# fonction pour envoyer les commentaires #

def client_send_feedback_form(request):
    return render(request, 'dashboard_client/clients/envoie_avis.html')

# fonction qui permet au client de laisser un avis #
@login_required
def client_send_feedback(request):
	if request.method == 'POST':
		feedback = request.POST['feedback']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		feedback = username + " "+ " dit  " + feedback 

		a = Feedback(avis=feedback)
		a.save()
		messages.success(request, 'Les commentaires ont été envoyés')
		return redirect('client_send_feedback_form')
	else:
	    messages.error(request, 'Les commentaires n ont pas été envoyés.')
       
       
#  fonction qui permet au client de creer une discussion #       


from django.shortcuts import render, redirect
from .models import Chat, Conversation
from django.contrib.auth.decorators import login_required



@login_required
def client_create_chat(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Récupération ou création d'une conversation pour ce client
    conversation, created = Conversation.objects.get_or_create(client=request.user)

    if request.method == "POST":
        msg_text = request.POST.get("message", "").strip()
        if msg_text:
            Chat.objects.create(
                conversation=conversation,
                dossier=dossier,
                sender=request.user,
                message=msg_text
            )
        return redirect('client_create_chat', dossier_id=dossier.id)

    # Récupération des messages liés à cette conversation et dossier
    messages = Chat.objects.filter(conversation=conversation, dossier=dossier).order_by('posted_at')
    
    return render(request, 'dashboard_client/chats/formulaire_chat.html', {
        "messages": messages,
        "dossier": dossier
    })

    
# class qui permet au client de voir la iste des discussions #  
class client_view_liste_chat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'dashboard_client/chats/liste_chat.html'
    
    
  
    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-posted_at')
    
    
    
# fonction de demende de suppression d'un dossier #    


    
# fonction qui permet au client de demander une suppression de dossier #
@login_required
def delete_request(request):
	if request.method == 'POST':
		book_id = request.POST['delete_request']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		user_request = username + " veut que le dossier avec l'ID  " + book_id + " soit supprimé."

		a = DeleteRequest(delete_request=user_request)
		a.save()
		messages.success(request, 'La demande a été envoyée')
		return redirect('client_view_list_dossier')
	else:
	    messages.error(request, 'La demande na pas été envoyée.')
     
     
     
	           
   # fonctions ia #          
            
from django.http import JsonResponse
import json
from .ai_engine import ai_engine  # Importez l'instance
from .models import PieceJointe  # Ajustez selon votre modèle
import os
import re
# ... vos autres vues ...

def vue_analyse_ia(request, pk):
    piece = get_object_or_404(PieceJointe, pk=pk)
    
    # Initialisation sécurisée
    doc_id = f"doc_{piece.id}"
    resultat = ""
    
    try:
        if not piece.fichier or not piece.fichier.name:
            resultat = "❌ Aucun fichier associé à cette pièce jointe."
        else:
            # CORRECTION ICI : Utiliser le chemin correct du fichier
            # piece.fichier est un objet FieldFile, on accède au fichier via son chemin
            file_path = piece.fichier.path
            
            if not os.path.exists(file_path):
                resultat = "❌ Le fichier n'existe pas sur le serveur."
            else:
                # Créer un ID unique
                safe_name = re.sub(r'[^\w\-_]', '', os.path.basename(piece.fichier.name)[:20].replace(' ', '_'))
                doc_id = f"doc_{piece.id}_{safe_name}"
                
                print(f"🚀 Début de l'analyse IA pour {doc_id}")
                resultat = ai_engine.process_document(file_path, doc_id)
                
                if not resultat:
                    resultat = "✅ Document analysé avec succès ! Posez vos questions."
                
                print(f"✅ Analyse terminée pour {doc_id}")
    
    except Exception as e:
        print(f"❌ Erreur dans vue_analyse_ia: {e}")
        import traceback
        traceback.print_exc()
        resultat = f"❌ Erreur lors de l'analyse : {type(e).__name__} - {str(e)[:200]}"
    
    return render(request, 'analyse_ia.html', {
        'piece': piece,
        'resume': resultat,
        'doc_id': doc_id
    })

from django.views import View

from django.views.decorators.csrf import csrf_exempt # <-- CETTE LIGNE MANQUAIT
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

# <-- DOIT ÊTRE JUSTE AVANT la fonction
@csrf_exempt  # <-- Fonctionne sur les fonctions
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({
            'reponse': 'Méthode non autorisée. Utilisez POST.',
            'success': False
        })
    
    try:
        # Lire les données JSON
        data = json.loads(request.body)
        
        question = data.get('question', '').strip()
        doc_id = data.get('doc_id', None)
        
        if not question:
            return JsonResponse({
                'reponse': 'Question vide', 
                'success': False
            })
        
        # Appeler l'IA
        ai_engine.initialize()
        reponse = ai_engine.chat(question, doc_id)
        
        return JsonResponse({
            'reponse': reponse,
            'success': True
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'reponse': 'Format JSON invalide', 
            'success': False
        })
    except Exception as e:
        return JsonResponse({
            'reponse': f'Erreur: {type(e).__name__}',
            'success': False
        })
        
        
        
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Dossier, AnalyseJuridique, ChatQuestion
from .services.groq_service import AnalyseJuridiqueService
from .services.chat_service import ChatJuridiqueService
import re

@login_required
def analyser_dossier_ia(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    if request.method == 'POST':
        try:
            service = AnalyseJuridiqueService()
            analyse_text = service.generer_analyse(dossier)
            
            if analyse_text:
                sections = _parser_reponse_ia(analyse_text)
                
                # Debug: Afficher les sections extraites
                print("=== SECTIONS PARSÉES ===")
                for key, value in sections.items():
                    print(f"{key}: {value[:100]}...")
                
                # Si aucune section n'a de contenu, utiliser le texte complet
                if not any(sections.values()):
                    sections['nature_juridique'] = analyse_text[:2000]
                
                analyse = AnalyseJuridique.objects.create(
                    dossier=dossier,
                    nature_juridique=sections.get('nature_juridique', ''),
                    demarches_recommandees=sections.get('demarches_recommandees', ''),
                    delais_importants=sections.get('delais_importants', ''),
                    recommandations=sections.get('recommandations', ''),
                    procedure_complete=sections.get('procedure_complete', ''),
                    risques_juridiques=sections.get('risques_juridiques', ''),
                    textes_applicables=sections.get('textes_applicables', ''),
                    questions_frequentes=sections.get('questions_frequentes', '')
                )
                
                messages.success(request, "Analyse juridique générée avec succès!")
                return redirect('voir_analyse_juridique', dossier_id=dossier_id)
            else:
                messages.error(request, "L'IA n'a pas pu générer d'analyse. Veuillez réessayer.")
                return render(request, 'analyser_dossier.html', {'dossier': dossier})
                
        except Exception as e:
            print(f"Erreur dans analyser_dossier_ia: {e}")
            messages.error(request, f"Une erreur est survenue: {str(e)}")
            return render(request, 'analyser_dossier.html', {'dossier': dossier})
    
    return render(request, 'analyser_dossier.html', {'dossier': dossier})

def _parser_reponse_ia(texte):
    """Parse la réponse de l'IA pour extraire les sections"""
    sections = {
        'nature_juridique': '',
        'demarches_recommandees': '',
        'delais_importants': '',
        'recommandations': '',
        'procedure_complete': '',
        'risques_juridiques': '',
        'textes_applicables': '',
        'questions_frequentes': ''
    }
    
    if not texte or not texte.strip():
        return sections
    
    texte = texte.strip()
    
    # Dictionnaire de mapping pour les titres de sections
    section_patterns = {
        'nature_juridique': [
            '1. NATURE JURIDIQUE', 'NATURE JURIDIQUE', '1. NATURE',
            '1. Nature juridique', 'Nature juridique'
        ],
        'demarches_recommandees': [
            '2. DÉMARCHES RECOMMANDÉES', 'DÉMARCHES RECOMMANDÉES', '2. DÉMARCHES',
            '2. Démarches recommandées', 'Démarches recommandées'
        ],
        'delais_importants': [
            '3. DÉLAIS IMPORTANTS', 'DÉLAIS IMPORTANTS', '3. DÉLAIS',
            '3. Délais importants', 'Délais importants'
        ],
        'recommandations': [
            '4. RECOMMANDATIONS', 'RECOMMANDATIONS', '4. RECOMMANDATIONS',
            '4. Recommandations', 'Recommandations'
        ],
        'procedure_complete': [
            '5. PROCÉDURE COMPLÈTE', 'PROCÉDURE COMPLÈTE', '5. PROCÉDURE',
            '5. Procédure complète', 'Procédure complète'
        ],
        'risques_juridiques': [
            '6. RISQUES JURIDIQUES', 'RISQUES JURIDIQUES', '6. RISQUES',
            '6. Risques juridiques', 'Risques juridiques'
        ],
        'textes_applicables': [
            '7. TEXTES APPLICABLES', 'TEXTES APPLICABLES', '7. TEXTES',
            '7. Textes applicables', 'Textes applicables'
        ],
        'questions_frequentes': [
            '8. QUESTIONS FRÉQUENTES', 'QUESTIONS FRÉQUENTES', '8. QUESTIONS',
            '8. Questions fréquentes', 'Questions fréquentes'
        ]
    }
    
    # Diviser en lignes
    lines = texte.split('\n')
    current_section = None
    section_started = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Rechercher si cette ligne est un titre de section
        found_section = False
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                if pattern in line_stripped.upper() or pattern in line_stripped:
                    current_section = section_name
                    section_started = True
                    found_section = True
                    break
            if found_section:
                break
        
        # Si ce n'est pas un titre, ajouter au contenu
        if not found_section and current_section and section_started:
            # Vérifier si c'est le début d'une nouvelle section sans titre explicite
            if line_stripped and len(line_stripped) < 100 and any(
                line_stripped.upper().startswith(f"{i}.") 
                for i in range(1, 9)
            ):
                # C'est probablement une nouvelle section, arrêter la précédente
                section_started = False
                continue
            
            if sections[current_section]:
                sections[current_section] += '\n' + line_stripped
            else:
                sections[current_section] = line_stripped
    
    # Nettoyer les sections
    for key in sections:
        if sections[key]:
            # Supprimer les numéros de début de ligne
            sections[key] = '\n'.join([
                line.strip() for line in sections[key].split('\n') 
                if line.strip() and not any(line.strip().startswith(f"{i}.") for i in range(1, 9))
            ]).strip()
    
    # Si aucune section n'est remplie, utiliser une approche plus simple
    if not any(sections.values()):
        # Essayer de diviser par les numéros
        parts = texte.split('\n\n')
        for i, part in enumerate(parts):
            if i == 0:
                sections['nature_juridique'] = part.strip()
            elif i == 1:
                sections['demarches_recommandees'] = part.strip()
            elif i == 2:
                sections['delais_importants'] = part.strip()
            elif i == 3:
                sections['recommandations'] = part.strip()
            elif i == 4:
                sections['procedure_complete'] = part.strip()
            elif i == 5:
                sections['risques_juridiques'] = part.strip()
            elif i == 6:
                sections['textes_applicables'] = part.strip()
            elif i == 7:
                sections['questions_frequentes'] = part.strip()
    
    return sections
@login_required
def voir_analyse_juridique(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    analyse = AnalyseJuridique.objects.filter(dossier=dossier).first()
    
    return render(request, 'voir_analyse.html', {
        'dossier': dossier,
        'analyse': analyse
    })

@login_required
def chat_analyse(request, analyse_id):
    analyse = get_object_or_404(AnalyseJuridique, id=analyse_id)
    
    if request.method == 'POST':
        question = request.POST.get('question', '')
        
        if question:
            chat_service = ChatJuridiqueService()
            reponse = chat_service.poser_question(analyse, question)
            
            ChatQuestion.objects.create(
                analyse=analyse,
                question=question,
                reponse=reponse
            )
            
            return JsonResponse({
                'success': True,
                'reponse': reponse
            })
    
    questions = ChatQuestion.objects.filter(analyse=analyse).order_by('date_question')
    
    return render(request, 'chat_analyse.html', {
        'analyse': analyse,
        'questions': questions
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import re
from .models import Dossier, AnalyseJuridique, ChatQuestion
from .services.groq_service import AnalyseJuridiqueService
from .services.chat_service import ChatJuridiqueService

@login_required
def analyser_dossier_ia(request, dossier_id):
    """Analyse un dossier avec l'IA"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    if request.method == 'POST':
        try:
            # Générer l'analyse avec l'IA
            service = AnalyseJuridiqueService()
            analyse_text = service.generer_analyse(dossier)
            
            if analyse_text:
                # Parser la réponse de l'IA
                sections = _parser_reponse_ia(analyse_text)
                
                # Supprimer les anciennes analyses pour ce dossier pour éviter les doublons
                AnalyseJuridique.objects.filter(dossier=dossier).delete()
                
                # Créer une nouvelle analyse
                analyse = AnalyseJuridique.objects.create(
                    dossier=dossier,
                    nature_juridique=sections.get('nature_juridique', ''),
                    demarches_recommandees=sections.get('demarches_recommandees', ''),
                    delais_importants=sections.get('delais_importants', ''),
                    recommandations=sections.get('recommandations', ''),
                    procedure_complete=sections.get('procedure_complete', ''),
                    risques_juridiques=sections.get('risques_juridiques', ''),
                    textes_applicables=sections.get('textes_applicables', ''),
                    questions_frequentes=sections.get('questions_frequentes', '')
                )
                
                messages.success(request, "Analyse juridique générée avec succès !")
                return redirect('voir_analyse_juridique', dossier_id=dossier_id)
            else:
                messages.error(request, "L'IA n'a pas pu générer d'analyse. Veuillez réessayer.")
                return render(request, 'analyser_dossier.html', {'dossier': dossier})
                
        except Exception as e:
            print(f"Erreur lors de l'analyse IA: {e}")
            messages.error(request, f"Erreur lors de l'analyse: {str(e)}")
            return render(request, 'analyser_dossier.html', {'dossier': dossier})
    
    return render(request, 'analyser_dossier.html', {'dossier': dossier})

def _parser_reponse_ia(texte):
    """Parse la réponse de l'IA pour extraire les sections"""
    sections = {
        'nature_juridique': '',
        'demarches_recommandees': '',
        'delais_importants': '',
        'recommandations': '',
        'procedure_complete': '',
        'risques_juridiques': '',
        'textes_applicables': '',
        'questions_frequentes': ''
    }
    
    if not texte or not texte.strip():
        return sections
    
    texte = texte.strip()
    
    # Recherche simple des sections
    lines = texte.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Détection des titres de sections (plus flexible)
        line_upper = line.upper()
        if '1. NATURE JURIDIQUE' in line_upper or 'NATURE JURIDIQUE' in line_upper:
            current_section = 'nature_juridique'
            continue
        elif '2. DÉMARCHES RECOMMANDÉES' in line_upper or 'DÉMARCHES RECOMMANDÉES' in line_upper:
            current_section = 'demarches_recommandees'
            continue
        elif '3. DÉLAIS IMPORTANTS' in line_upper or 'DÉLAIS IMPORTANTS' in line_upper:
            current_section = 'delais_importants'
            continue
        elif '4. RECOMMANDATIONS' in line_upper or 'RECOMMANDATIONS' in line_upper:
            current_section = 'recommandations'
            continue
        elif '5. PROCÉDURE COMPLÈTE' in line_upper or 'PROCÉDURE COMPLÈTE' in line_upper:
            current_section = 'procedure_complete'
            continue
        elif '6. RISQUES JURIDIQUES' in line_upper or 'RISQUES JURIDIQUES' in line_upper:
            current_section = 'risques_juridiques'
            continue
        elif '7. TEXTES APPLICABLES' in line_upper or 'TEXTES APPLICABLES' in line_upper:
            current_section = 'textes_applicables'
            continue
        elif '8. QUESTIONS FRÉQUENTES' in line_upper or 'QUESTIONS FRÉQUENTES' in line_upper:
            current_section = 'questions_frequentes'
            continue
        
        # Ajouter le contenu à la section courante
        if current_section and current_section in sections:
            if sections[current_section]:
                sections[current_section] += '\n' + line
            else:
                sections[current_section] = line
    
    # Si aucune section n'est trouvée, mettre tout dans nature_juridique
    if not any(sections.values()) and texte:
        sections['nature_juridique'] = texte
    
    return sections

@login_required
def voir_analyse_juridique(request, dossier_id):
    """Affiche l'analyse juridique d'un dossier"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Utiliser first() au lieu de get() pour éviter l'erreur
    analyse = AnalyseJuridique.objects.filter(dossier=dossier).first()
    
    # Si aucune analyse existe, rediriger vers la génération
    if not analyse:
        messages.info(request, "Aucune analyse disponible. Génération d'une analyse...")
        return redirect('analyser_dossier_ia', dossier_id=dossier_id)
    
    return render(request, 'voir_analyse.html', {
        'dossier': dossier,
        'analyse': analyse
    })

@login_required
def chat_analyse(request, analyse_id):
    """Interface de chat pour poser des questions sur l'analyse"""
    analyse = get_object_or_404(AnalyseJuridique, id=analyse_id)
    
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        
        if question:
            try:
                chat_service = ChatJuridiqueService()
                reponse = chat_service.poser_question(analyse, question)
                
                # Sauvegarder la question/réponse
                ChatQuestion.objects.create(
                    analyse=analyse,
                    question=question,
                    reponse=reponse
                )
                
                return JsonResponse({
                    'success': True,
                    'reponse': reponse
                })
            except Exception as e:
                print(f"Erreur dans le chat: {e}")
                return JsonResponse({
                    'success': False,
                    'reponse': "Désolé, une erreur est survenue. Veuillez réessayer."
                })
        
        return JsonResponse({
            'success': False,
            'reponse': "Veuillez saisir une question."
        })
    
    # GET : afficher l'historique
    questions = ChatQuestion.objects.filter(analyse=analyse).order_by('date_question')
    
    return render(request, 'chat_analyse.html', {
        'analyse': analyse,
        'questions': questions,
        'dossier': analyse.dossier
    })

@login_required
def regenerer_analyse(request, dossier_id):
    """Regénère l'analyse juridique"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Supprimer les anciennes analyses
    AnalyseJuridique.objects.filter(dossier=dossier).delete()
    
    messages.info(request, "Régénération de l'analyse en cours...")
    return redirect('analyser_dossier_ia', dossier_id=dossier_id)