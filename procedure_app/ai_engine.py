import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Configurez le chemin vers votre projet Django
DJANGO_PROJECT_PATH = "/g/mes projets informatiques/gestion des procedures judiciaires/procedure_judiciaire"
if DJANGO_PROJECT_PATH not in sys.path:
    sys.path.append(DJANGO_PROJECT_PATH)

# Configurez Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procedure_judiciaire.settings')

try:
    import django
    django.setup()
    print("✅ Django correctement initialisé")
except Exception as e:
    print(f"⚠️ Erreur initialisation Django: {e}")

# Reste des imports
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    
import requests
from django.conf import settings
import hashlib
import time
import mimetypes
from pathlib import Path
import re
import json
from datetime import datetime

class SmartAIAssistant:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SmartAIAssistant, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance._groq_api_key = None
            cls._instance._groq_model = None
            cls._instance._api_working = False
            cls._instance._rate_limit_hit = False
            cls._instance._rate_limit_reset = 0
            cls._instance.active_documents = {}
            cls._instance._conversation_context = []
            cls._instance._max_context_length = 8  # Augmenté pour mieux suivre la conversation
            cls._instance._user_intent = None  # Pour comprendre l'intention de l'utilisateur
            cls._instance._conversation_state = "idle"  # idle, document_loaded, helping_with_legal
        return cls._instance
    
    def initialize(self):
        if self._initialized:
            return
        
        # Utilisation d'une variable d'environnement pour la sécurité
        import os
        self._groq_api_key = os.getenv("GROQ_API_KEY", "")

        # Si la variable n'est pas trouvée, on cherche dans Django settings
        if not self._groq_api_key:
            try:
                from django.conf import settings
                self._groq_api_key = getattr(settings, "GROQ_API_KEY", "")
            except:
                pass
        
        if not self._groq_api_key:
            print("⚠️ Mode démo: Aucune clé GROQ_API_KEY trouvée")
            self._api_working = False
        else:
            print(f"✅ Clé Groq détectée: {self._groq_api_key[:15]}...")
            
            # Détecter un modèle valide
            self._groq_model = self._detect_valid_model()
            
            if self._groq_model:
                self._api_working = True
                print(f"✅ API Groq fonctionnelle avec modèle: {self._groq_model}")
            else:
                self._api_working = False
                print("❌ Aucun modèle Groq valide trouvé")
        
        self._initialized = True
    
    def _detect_valid_model(self):
        """Détecte un modèle Groq valide"""
        models_to_try = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "gemma2-9b-it",
        ]
        
        print("🔍 Détection des modèles Groq...")
        for model in models_to_try:
            if self._test_model(model):
                print(f"✅ Modèle détecté: {model}")
                return model
        
        print("❌ Aucun modèle valide trouvé")
        return None
    
    def _test_model(self, model):
        """Teste si un modèle spécifique fonctionne"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": "Bonjour"}],
                "max_tokens": 5
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"  ❌ {model} : Erreur - {str(e)[:50]}")
            return False
    
    def chat(self, message, doc_id=None):
        if not self._initialized:
            self.initialize()
        
        message_lower = message.lower().strip()
        
        # Détecter l'intention de l'utilisateur
        self._detect_user_intent(message_lower)
        
        # Gestion des réponses locales (sans API) pour les cas simples
        local_response = self._get_local_response(message_lower, doc_id)
        if local_response:
            return local_response
        
        # Vérifier si la limite de taux est active
        current_time = time.time()
        if self._rate_limit_hit and current_time < self._rate_limit_reset:
            wait_minutes = int((self._rate_limit_reset - current_time) / 60)
            wait_seconds = int((self._rate_limit_reset - current_time) % 60)
            return self._get_rate_limit_message(wait_minutes, wait_seconds)
        
        # Si l'API Groq est fonctionnelle, l'utiliser
        if self._api_working and self._groq_api_key and self._groq_model:
            try:
                response = self._get_ai_response(message, doc_id)
                return response
            except Exception as e:
                print(f"Erreur API: {e}")
                return self._demo_response(message, doc_id, api_error=True)
        
        # Sinon, mode démo avec améliorations
        return self._demo_response(message, doc_id, api_error=not self._api_working)
    
    def _detect_user_intent(self, message_lower):
        """Détecte l'intention de l'utilisateur pour mieux répondre"""
        # Détecter les intentions juridiques
        legal_keywords = [
            'viol', 'plainte', 'déposer', 'dossier', 'justice', 
            'accusation', 'tribunal', 'avocat', 'policier', 'gendarmerie',
            'agression', 'victime', 'accusé', 'témoin', 'preuve',
            'déclaration', 'procès', 'jugement', 'condamnation'
        ]
        
        if any(keyword in message_lower for keyword in legal_keywords):
            self._user_intent = "legal_help"
            self._conversation_state = "helping_with_legal"
        elif 'document' in message_lower or 'fichier' in message_lower or 'pdf' in message_lower:
            self._user_intent = "document_help"
            if self.active_documents:
                self._conversation_state = "document_loaded"
        elif any(word in message_lower for word in ["bonjour", "bonsoir", "salut", "hello"]):
            self._user_intent = "greeting"
        elif any(word in message_lower for word in ["merci", "thanks"]):
            self._user_intent = "thanks"
        elif any(word in message_lower for word in ["au revoir", "bye", "à bientôt"]):
            self._user_intent = "goodbye"
        else:
            self._user_intent = "general_conversation"
    
    def _get_local_response(self, message_lower, doc_id=None):
        """Gère les réponses locales sans appel API - AMÉLIORÉ"""
        
        # Salutations - plus intelligentes
        greetings = ["bonjour", "bonsoir", "salut", "hello", "hi", "coucou"]
        if any(word in message_lower for word in greetings):
            context = ""
            time_of_day = "Bonsoir" if 18 <= datetime.now().hour < 24 else "Bonjour"
            
            if doc_id and doc_id in self.active_documents:
                doc_data = self.active_documents[doc_id]
                if isinstance(doc_data, dict) and 'text' in doc_data:
                    word_count = len(doc_data['text'].split())
                    filename = doc_data.get('filename', 'un document')
                    return f"👋 {time_of_day} !\n\nJ'ai analysé votre document **'{filename}'** ({word_count} mots).\n\nComment puis-je vous aider avec ce document aujourd'hui ?"
            
            if self._user_intent == "legal_help":
                return f"👋 {time_of_day} !\n\nJe comprends que vous avez besoin d'aide pour une affaire juridique. Je suis là pour vous aider.\n\nPouvez-vous me donner plus de détails sur votre situation ?"
            
            return f"👋 {time_of_day} !\n\nJe suis votre assistant IA spécialisé. Comment puis-je vous aider aujourd'hui ?"
        
        # Remerciements
        if any(word in message_lower for word in ["merci", "thank you", "thanks", "merci beaucoup", "merci bien"]):
            return "Je vous en prie ! C'est un plaisir de vous aider. 😊\n\nN'hésitez pas si vous avez d'autres questions !"
        
        # Au revoir
        if any(word in message_lower for word in ["au revoir", "bye", "goodbye", "à plus", "ciao", "à bientôt", "adieu"]):
            return "À bientôt ! N'hésitez pas à revenir si vous avez besoin d'aide. Bonne journée ! 👋"
        
        # Présentation de l'assistant
        if any(word in message_lower for word in ["tu es qui", "qui es-tu", "c'est quoi ton nom", "ton nom", "tu t'appelles", "présente toi"]):
            return "Je suis votre assistant IA spécialisé en analyse de documents et aide juridique.\n\nJe peux vous aider à :\n• Analyser vos documents\n• Comprendre des situations juridiques\n• Préparer des déclarations\n• Répondre à vos questions\n\nAppelez-moi simplement 'Assistant' !"
        
        # Vérification de présence
        if any(word in message_lower for word in ["ça va", "comment ça va", "comment vas-tu", "tu vas bien", "comment tu vas"]):
            return "Je vais bien, merci ! Toujours prêt à vous aider. 😊\n\nEt vous, comment allez-vous aujourd'hui ?"
        
        # Réponse à "okay"
        if message_lower in ["ok", "okay", "d'accord", "oké", "entendu", "compris"]:
            return "Parfait ! 😊\n\nQue souhaitez-vous faire maintenant ?"
        
        # Réponse positive
        if any(word in message_lower for word in ["très fort", "très bien", "excellent", "super", "bravo", "magnifique"]):
            return "Merci beaucoup ! Je fais de mon mieux pour vous aider. 😊\n\nN'hésitez pas si vous avez d'autres questions !"
        
        # Demande d'aide
        if any(word in message_lower for word in ["aide", "help", "aide moi", "aide-moi", "j'ai besoin d'aide"]):
            if self._user_intent == "legal_help":
                return self._provide_legal_help(message_lower)
            else:
                return """🆘 **Je peux vous aider avec :**

1. **📄 Analyse de documents** (PDF, Word, Excel, etc.)
2. **⚖️ Questions juridiques** 
3. **📝 Rédaction de déclarations**
4. **🔍 Recherche d'informations**

**Pour commencer :**
- Décrivez-moi votre situation
- Envoyez-moi un document à analyser
- Posez-moi une question spécifique

Je suis là pour vous aider ! 😊"""
        
        # Questions sur le viol/dépot de plainte (intention juridique détectée)
        if self._user_intent == "legal_help" and any(word in message_lower for word in ["viol", "agression", "plainte", "déposer"]):
            return self._provide_legal_help(message_lower)
        
        return None
    
    def _provide_legal_help(self, message_lower):
        """Fournit une aide juridique de base"""
        if "viol" in message_lower or "agression sexuelle" in message_lower:
            return """⚖️ **AIDE POUR DÉPÔT DE PLAINTE - CAS DE VIOL**

Je comprends que vous souhaitez déposer une plainte pour viol. Voici comment je peux vous aider :

**📝 ÉTAPES IMPORTANTES :**

1. **Consultez un médecin immédiatement** pour :
   • Faire constater les blessures
   • Obtenir un certificat médical
   • Préserver les preuves ADN

2. **Rendez-vous à la police/gendarmerie** avec :
   • Votre pièce d'identité
   • Les preuves disponibles
   • Les coordonnées des témoins

3. **Pour préparer votre déclaration**, décrivez-moi :
   • Les faits précis (date, heure, lieu)
   • La relation avec l'agresseur
   • Les témoins éventuels
   • Les preuves disponibles

**💡 Je peux vous aider à :**
• Structurer votre récit
• Identifier les éléments importants
• Préparer une déclaration claire

**Souhaitez-vous que je vous aide à rédiger votre déclaration ?**"""
        
        elif "histoire" in message_lower or "récit" in message_lower or "déclaration" in message_lower:
            return """📝 **PRÉPARATION DE VOTRE DÉCLARATION**

Pour vous aider à rédiger une déclaration claire et précise, j'ai besoin de quelques informations :

**📋 INFORMATIONS NÉCESSAIRES :**

1. **Vos coordonnées** (nom, prénom, adresse, téléphone)
2. **Les faits** :
   • Date et heure exactes
   • Lieu précis
   • Circonstances détaillées
   • Description de l'agresseur

3. **Les conséquences** :
   • Blessures physiques
   • Traumatismes psychologiques
   • Impact sur votre vie

4. **Les preuves** :
   • Certificats médicaux
   • Témoins
   • Photos/messages
   • Objets pertinents

**✍️ Pour commencer :**
Pouvez-vous me décrire les faits dans l'ordre chronologique ?
Je vais vous aider à structurer votre récit pour qu'il soit clair et convaincant."""
        
        return """⚖️ **ASSISTANCE JURIDIQUE**

Je comprends que vous avez besoin d'aide pour une affaire juridique. 

**Je peux vous aider à :**
• Préparer vos déclarations
• Comprendre les procédures
• Organiser vos idées
• Identifier les éléments importants

**Pour mieux vous aider, pouvez-vous :**
1. Me décrire brièvement votre situation
2. Me dire ce que vous souhaitez accomplir
3. Me préciser si vous avez déjà des documents

Je suis là pour vous accompagner dans vos démarches. 😊"""
    
    def _get_ai_response(self, message, doc_id=None):
        """Obtient une réponse de l'IA Groq avec gestion de contexte améliorée"""
        # Récupérer le contexte du document si disponible
        context = ""
        filename = ""
        if doc_id and doc_id in self.active_documents:
            doc_data = self.active_documents[doc_id]
            if isinstance(doc_data, dict) and 'text' in doc_data:
                context = doc_data['text'][:4000]  # Limiter la longueur
                filename = doc_data.get('filename', 'le document')
        
        # Ajouter le message actuel au contexte de conversation
        self._conversation_context.append({
            "role": "user", 
            "content": message,
            "timestamp": time.time()
        })
        
        # Limiter la longueur du contexte mais garder plus d'historique
        if len(self._conversation_context) > self._max_context_length * 2:
            # Garder les messages les plus récents mais aussi garder un peu d'historique
            self._conversation_context = self._conversation_context[-(self._max_context_length * 2):]
        
        # Préparer le message pour l'API avec instruction de formatage améliorée
        system_message = self._create_system_message(context, filename)
        
        # Appeler l'API
        response_text = self._call_groq_api(system_message, message, context)
        
        # Ajouter la réponse au contexte
        self._conversation_context.append({
            "role": "assistant", 
            "content": response_text,
            "timestamp": time.time()
        })
        
        # Formater la réponse pour qu'elle soit naturelle et bien structurée
        return self._format_response_natural(response_text)
    
    def _create_system_message(self, context, filename):
        """Crée le message système selon le contexte - AMÉLIORÉ"""
        
        # Instructions de base
        base_instructions = """Tu es un assistant conversationnel français très compétent et utile.
        
TON STYLE :
• Professionnel mais chaleureux
• Clair et direct
• Empathique quand c'est nécessaire
• Structuré dans tes réponses

FORMAT DE RÉPONSE :
• Utilise des paragraphes courts
• Va à la ligne entre les idées
• Sois précis et concis
• Utilise des listes à puces quand c'est utile
• Évite les blocs de texte trop longs"""
        
        # Instructions spécifiques selon le contexte
        if self._user_intent == "legal_help":
            base_instructions += """

CONTEXTE JURIDIQUE DÉTECTÉ :
L'utilisateur a besoin d'aide pour une affaire juridique, possiblement un viol.

TON APPROCHE :
1. Sois empathique et professionnel
2. Donne des conseils pratiques et concrets
3. Aide à structurer les déclarations
4. Encourage à consulter des professionnels si nécessaire
5. Ne donne pas de conseils juridiques précis (tu n'es pas avocat)

EXEMPLE DE RÉPONSE UTILE :
"Je comprends que vous souhaitez déposer une plainte. Pour vous aider, je vais vous guider pour structurer votre déclaration. Commençons par les faits : pouvez-vous me décrire ce qui s'est passé, en précisant la date, l'heure et le lieu ?" """
        
        if context:
            return f"""{base_instructions}

DOCUMENT DE L'UTILISATEUR :
• Nom : {filename}
• Extrait : {context[:2000]}

RÈGLES SPÉCIFIQUES :
• Réponds en fonction du document si la question le concerne
• Sinon, utilise tes connaissances générales
• Ne commence pas par "Selon le document..."
• Sois naturel, comme dans une conversation"""
        else:
            return base_instructions
    
    def _call_groq_api(self, system_message, user_message, context):
        """Appelle l'API Groq avec gestion d'erreurs"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._groq_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Préparer les messages pour l'API
            messages = [{"role": "system", "content": system_message}]
            
            # Ajouter le contexte de conversation récent (formatté)
            for msg in self._conversation_context[-(self._max_context_length * 2):]:
                # Ne pas inclure les timestamps dans le message
                clean_msg = {"role": msg["role"], "content": msg["content"]}
                messages.append(clean_msg)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": user_message})
            
            data = {
                "model": self._groq_model,
                "messages": messages,
                "max_tokens": 1000,  # Augmenté pour des réponses plus complètes
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.1
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                return response_text
                
            elif response.status_code == 429:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '')
                print(f"⚠️ Limite de taux: {error_msg[:100]}")
                
                # Extraire le temps d'attente
                wait_match = re.search(r'try again in (\d+)m(\d+\.\d+)s', error_msg)
                if wait_match:
                    minutes = int(wait_match.group(1))
                    seconds = float(wait_match.group(2))
                    self._rate_limit_reset = time.time() + (minutes * 60 + seconds)
                    self._rate_limit_hit = True
                
                raise Exception("Rate limit reached")
                
            else:
                error_msg = response.json().get('error', {}).get('message', 'Erreur inconnue')
                raise Exception(f"Erreur API ({response.status_code}): {error_msg}")
                
        except Exception as e:
            print(f"❌ Erreur API Groq: {e}")
            raise
    
    def _format_response_natural(self, text):
        """Formate la réponse pour qu'elle soit naturelle et bien structurée - AMÉLIORÉ"""
        if not text:
            return text
        
        # Nettoyer la réponse
        text = text.strip()
        
        # Supprimer les références trop formelles
        patterns_to_remove = [
            r'^En tant qu[^\n]*assistant[^\n]*,\s*',
            r'^Selon (le|ce) document[^\n]*,\s*',
            r'^D\'après (le|ce) document[^\n]*,\s*',
            r'^Le document[^\n]*indique que[^\n]*,\s*',
            r'^Je vois que (le|ce) document[^\n]*,\s*',
            r'^Après analyse[^\n]*,\s*',
            r'^Dans (le|ce) document[^\n]*,\s*',
            r'^En réponse à votre question[^\n]*,\s*',
            r'^Bonjour,\s*',
            r'^Cher utilisateur,\s*',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remplacer les formules formelles par des versions plus naturelles
        replacements = [
            (r"peut être défini comme", "c'est"),
            (r"est défini comme", "c'est"),
            (r"se réfère à", "c'est"),
            (r"correspond à", "c'est"),
            (r"le document mentionne que", ""),
            (r"selon le document", ""),
            (r"d'après le document", ""),
            (r"dans le contexte du document", ""),
            (r"je pense que", "je crois que"),
            (r"il est important de noter que", "notez que"),
            (r"d'une part", "premièrement"),
            (r"d'autre part", "deuxièmement"),
        ]
        
        for old, new in replacements:
            text = re.sub(old, new, text, flags=re.IGNORECASE)
        
        # S'assurer que la réponse commence bien
        if text and len(text) > 0:
            text = re.sub(r'^[,\s]+', '', text)
            if text:
                # Capitaliser la première lettre
                text = text[0].upper() + text[1:]
        
        # AMÉLIORATION CRITIQUE : Meilleure structuration du texte
        
        # 1. Séparer les phrases longues
        sentences = re.split(r'([.!?]+\s+)', text)
        if len(sentences) > 1:
            # Recombiner avec des sauts de ligne
            formatted_text = ''
            for i in range(0, len(sentences)-1, 2):
                if i+1 < len(sentences):
                    sentence = sentences[i] + sentences[i+1]
                    # Si la phrase est longue, la mettre sur sa propre ligne
                    if len(sentence.strip()) > 100:
                        formatted_text += sentence.strip() + '\n\n'
                    else:
                        formatted_text += sentence.strip() + ' '
            
            text = formatted_text.strip()
        
        # 2. Gérer les listes
        # Convertir les listes numérotées
        text = re.sub(r'(\d+)\.\s+', r'\1. ', text)
        # Convertir les listes à puces
        text = re.sub(r'^[\-\*•]\s+', '• ', text, flags=re.MULTILINE)
        
        # 3. Après les deux-points, sauter une ligne pour les explications
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            if ':' in line and len(line) > 50:
                parts = line.split(':', 1)
                formatted_lines.append(parts[0] + ':')
                if parts[1].strip():
                    formatted_lines.append(parts[1].strip())
            else:
                formatted_lines.append(line)
        text = '\n'.join(formatted_lines)
        
        # 4. Nettoyer les sauts de ligne multiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 5. Ajouter un point final si manquant (sauf pour les questions)
        if text and not text.endswith(('.', '!', '?', '...', ':', '»')):
            # Vérifier si c'est une question
            if not any(text.strip().endswith(mark) for mark in ['?', '!']):
                text = text.rstrip() + '.'
        
        # 6. Supprimer les espaces multiples
        text = re.sub(r'[ \t]{2,}', ' ', text)
        
        # 7. Assurer que chaque ligne commence proprement
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Ne pas capitaliser les éléments de liste
                if line.startswith(('• ', '- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ')):
                    formatted_lines.append(line)
                else:
                    # Capitaliser la première lettre si nécessaire
                    if line and line[0].islower() and len(line) > 1:
                        line = line[0].upper() + line[1:]
                    formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        # 8. S'assurer qu'il n'y a pas d'espace avant la ponctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        return text.strip()
    
    def _get_rate_limit_message(self, minutes, seconds):
        """Génère un message sur la limite de taux"""
        return f"""⚠️ **Limite temporaire atteinte**

Je pourrai répondre normalement dans **{minutes} minutes {int(seconds)} secondes**.

**En attendant :**
• Je peux répondre à des questions simples
• Vous pouvez m'envoyer des documents
• La limite se réinitialise automatiquement

Désolé pour ce contretemps ! 😊"""
    
    def _demo_response(self, message, doc_id=None, api_error=False):
        """Réponses de démonstration conversationnelles - AMÉLIORÉ"""
        message_lower = message.lower().strip()
        
        # Récupérer le contexte si disponible
        context = ""
        filename = ""
        word_count = 0
        
        if doc_id and doc_id in self.active_documents:
            doc_data = self.active_documents[doc_id]
            if isinstance(doc_data, dict) and 'text' in doc_data:
                context = doc_data['text']
                filename = doc_data.get('filename', 'le document')
                word_count = len(context.split())
        
        # Gestion spéciale pour les intentions juridiques
        if self._user_intent == "legal_help":
            if "viol" in message_lower or "plainte" in message_lower:
                return self._provide_legal_help(message_lower)
        
        # Questions sur le contenu du document
        if context:
            # Résumé du document
            if any(word in message_lower for word in ["de quoi parle", "c'est quoi", "quel est le sujet", "parle de quoi", "résume", "résumé", "synthèse", "explique"]):
                preview = self._get_document_preview(context)
                return f"""📄 **À propos de votre document '{filename}' :**

{preview}

**📊 Statistiques :**
• Mots : {word_count}
• Pages : {self.active_documents[doc_id].get('pages', 1)}

**💡 Pour en savoir plus :**
Posez-moi des questions spécifiques sur le contenu !"""
            
            # Conclusion
            if any(word in message_lower for word in ["conclusion", "en conclusion", "pour conclure", "finalement"]):
                conclusion = self._find_conclusion(context)
                if conclusion:
                    return f"""📝 **Points clés de '{filename}' :**

{conclusion}

Souhaitez-vous que j'approfondisse un point particulier ? 😊"""
                else:
                    return f"""Je n'ai pas trouvé de section de conclusion claire dans '{filename}'.

**Je peux :**
• Vous faire un résumé personnalisé
• Répondre à des questions spécifiques
• Analyser des aspects particuliers

Que préférez-vous ? 😊"""
            
            # Questions sur des termes spécifiques
            if "définis" in message_lower or "définition" in message_lower or "qu'est-ce que" in message_lower:
                term = message_lower.replace("définis", "").replace("définition", "").replace("qu'est-ce que", "").strip()
                if term and len(term) > 2:
                    # Chercher le terme dans le document
                    lines = context.split('\n')
                    relevant_lines = []
                    for line in lines[:50]:  # Chercher dans les 50 premières lignes
                        if term in line.lower():
                            relevant_lines.append(line[:200])
                            if len(relevant_lines) >= 3:
                                break
                    
                    if relevant_lines:
                        return f"""🔍 **Occurrences de '{term}' dans votre document :**

{chr(10).join(f"• {line}" for line in relevant_lines)}

**💡 Conseil :**
Pour une définition précise, précisez le contexte ou consultez un dictionnaire spécialisé."""
        
        # Réponse selon l'intention détectée
        if self._user_intent == "legal_help":
            return self._provide_legal_help(message_lower)
        
        # Réponse par défaut avec document
        if context:
            if api_error:
                return f"""🤖 **Mode basique activé**

Votre document **'{filename}'** a été importé ({word_count} mots).

**Pour des analyses complètes :**
1. Vérifiez votre connexion internet
2. Assurez-vous que la clé API Groq est configurée
3. Réessayez dans quelques minutes

**En attendant, vous pouvez :**
• Poser des questions simples sur le document
• Demander un résumé
• Explorer les fonctionnalités de base

Je suis là pour vous aider ! 😊"""
            else:
                # Réponse générique mais utile
                if "?" in message or any(word in message_lower for word in ["comment", "pourquoi", "quand", "où", "qui", "quoi"]):
                    return f"""🤔 **Votre question :** "{message}"

Votre document **'{filename}'** contient {word_count} mots.

**En mode basique, je peux :**
• Vous donner un aperçu du document
• Chercher des termes spécifiques
• Vous aider à comprendre la structure

**Pour une réponse plus précise :**
Posez une question plus simple ou attendez que l'IA soit disponible.

Que souhaitez-vous savoir sur votre document ? 😊"""
                else:
                    return f"""📚 **Document chargé : '{filename}'**

📊 **Statistiques :**
• Mots : {word_count}
• Pages : {self.active_documents[doc_id].get('pages', 1)}

💬 **Posez-moi une question sur ce document :**
• "De quoi parle ce document ?"
• "Quels sont les points importants ?"
• "Cherchez [mot-clé] dans le document"
• "Faites-moi un résumé"

Je suis là pour vous aider ! 😊"""
        
        # Réponse par défaut sans document
        if api_error:
            return f"""🤖 **Problème de connexion détecté**

Vous avez dit : "{message}"

**Pour une meilleure expérience :**
1. Vérifiez votre connexion internet
2. Configurez une clé API Groq valide
3. Réessayez dans quelques instants

**Je peux quand même :**
• Répondre à des questions simples
• Vous aider avec les fonctionnalités de base
• Vous expliquer comment configurer l'IA

Que souhaitez-vous faire ? 😊"""
        else:
            # Réponse intelligente selon le type de question
            if "?" in message or any(word in message_lower for word in ["comment", "pourquoi", "quand", "où", "qui", "quoi"]):
                return f"""❓ **Question :** "{message}"

**En mode démo, mes capacités sont limitées.**

**Pour des réponses détaillées :**
1. Envoyez-moi un document à analyser
2. Configurez une clé API Groq
3. Posez des questions plus spécifiques

**Je peux quand même :**
• Vous expliquer mes fonctionnalités
• Répondre à des questions simples
• Vous aider à démarrer

Que souhaitez-vous savoir ? 😊"""
            else:
                return f"""🤖 **Assistant IA**

Vous avez dit : "{message}"

**Pour des interactions plus avancées :**
1. Envoyez-moi un document (PDF, Word, etc.)
2. Configurez l'IA pour des réponses détaillées
3. Posez des questions précises

**En attendant, je peux :**
• Vous aider à comprendre mes capacités
• Répondre à des questions de base
• Vous guider dans vos démarches

Comment puis-je vous aider aujourd'hui ? 😊"""
    
    def _get_document_preview(self, context):
        """Donne un aperçu intelligent du document"""
        if not context:
            return "Document vide ou non analysable."
        
        # Prendre les premières lignes significatives
        lines = context.split('\n')
        meaningful_lines = []
        
        for line in lines[:15]:
            line_stripped = line.strip()
            if line_stripped and len(line_stripped) > 15:
                meaningful_lines.append(line_stripped[:150])
                if len(meaningful_lines) >= 5:
                    break
        
        if meaningful_lines:
            preview = '\n'.join(meaningful_lines)
            if len(context) > 1000:
                preview += "\n\n... [document complet disponible]"
            return preview
        
        # Si pas de lignes significatives, prendre un extrait
        if len(context) > 300:
            return context[:300] + "..."
        else:
            return context
    
    def _find_conclusion(self, context):
        """Cherche une conclusion dans le document"""
        conclusion_keywords = [
            "conclusion", "en conclusion", "pour conclure", 
            "en résumé", "pour résumer", "finalement", "en définitive",
            "ainsi", "par conséquent", "en somme", "au final"
        ]
        
        context_lower = context.lower()
        
        for keyword in conclusion_keywords:
            idx = context_lower.find(keyword)
            if idx != -1:
                # Prendre un contexte plus large
                start_idx = max(0, idx - 100)
                end_idx = min(len(context), idx + 500)
                conclusion = context[start_idx:end_idx]
                
                # Nettoyer
                conclusion = re.sub(r'\s+', ' ', conclusion)
                conclusion = conclusion.strip()
                
                if len(conclusion) > 50:
                    return conclusion
        
        # Si pas de conclusion trouvée, prendre les derniers paragraphes
        paragraphs = context.split('\n\n')
        if len(paragraphs) >= 3:
            last_paragraphs = paragraphs[-3:]
            return '\n\n'.join(last_paragraphs)[:800]
        elif paragraphs:
            return paragraphs[-1][:800]
        
        return None
    
    # Les autres méthodes restent similaires mais je vais ajouter quelques améliorations...
    
    def process_document(self, file_path, doc_id=None):
        """Traite n'importe quel type de document et extrait son texte COMPLET"""
        try:
            if not os.path.exists(file_path):
                return f"❌ Erreur : Le fichier n'existe pas : {file_path}"
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return f"❌ Erreur : Le fichier est vide"
            
            if file_size > 50 * 1024 * 1024:
                return f"❌ Erreur : Le fichier est trop volumineux (> 50 MB)"
            
            file_info = self._detect_file_type(file_path)
            filename = file_info['name']
            extension = file_info['extension']
            
            print(f"📄 Début du traitement : {filename} ({extension}, {file_size/1024:.1f} KB)")
            
            text = ""
            pages = 1
            
            try:
                if extension in ['.pdf']:
                    if FITZ_AVAILABLE:
                        text, pages = self._extract_text_from_pdf(file_path)
                    else:
                        # Fallback sans fitz
                        try:
                            import PyPDF2
                            text, pages = self._extract_text_from_pdf_pypdf2(file_path)
                        except ImportError:
                            raise Exception("PyMuPDF ou PyPDF2 requis pour les PDF. Installez: pip install PyMuPDF")
                elif extension in ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.py', '.js', '.html', '.css']:
                    text, pages = self._extract_text_from_txt(file_path)
                elif extension in ['.docx', '.doc']:
                    text, pages = self._extract_text_from_docx(file_path)
                elif extension in ['.csv']:
                    text, pages = self._extract_text_from_csv(file_path)
                elif extension in ['.xlsx', '.xls', '.ods']:
                    text, pages = self._extract_text_from_excel(file_path)
                elif extension in ['.html', '.htm']:
                    text, pages = self._extract_text_from_html(file_path)
                elif extension in ['.rtf']:
                    text, pages = self._extract_text_from_rtf(file_path)
                else:
                    try:
                        text, pages = self._extract_text_from_txt(file_path)
                    except:
                        return f"❌ Format non supporté : {extension}"
            except Exception as extract_error:
                return f"❌ Erreur d'extraction pour {filename}: {str(extract_error)}"
            
            if not text.strip():
                return f"❌ Aucun texte n'a pu être extrait du fichier {filename}"
            
            text = self._clean_extracted_text(text)
            
            word_count = len(text.split())
            char_count = len(text)
            
            if not doc_id:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:10]
                doc_id = f"doc_{file_hash}_{int(time.time())}"
            
            self.active_documents[doc_id] = {
                'text': text,
                'pages': pages,
                'words': word_count,
                'chars': char_count,
                'filename': filename,
                'extension': extension,
                'file_size': file_size,
                'file_type': file_info['mime_type'] or f"Type: {extension}",
                'timestamp': time.time(),
                'file_path': file_path
            }
            
            print(f"✅ Document traité : {pages} pages, {word_count} mots, {char_count} caractères")
            
            if not self._initialized:
                self.initialize()
            
            file_type_names = {
                '.pdf': 'PDF',
                '.docx': 'Word',
                '.doc': 'Word',
                '.txt': 'Texte',
                '.csv': 'CSV',
                '.xlsx': 'Excel',
                '.xls': 'Excel',
                '.html': 'HTML',
                '.htm': 'HTML',
                '.rtf': 'RTF',
            }
            
            file_type = file_type_names.get(extension, extension.upper().replace('.', ''))
            
            if self._api_working and not self._rate_limit_hit:
                return f"""🎉 **Document analysé avec succès !**

**📄 Fichier :** {filename}
**📁 Type :** {file_type}
**📊 Statistiques :**
• Pages : {pages}
• Mots : {word_count}
• Caractères : {char_count}

**💬 Je suis prêt à répondre à vos questions sur ce document !**

Exemples de questions :
• "Résume-moi ce document"
• "De quoi parle-t-il principalement ?"
• "Explique-moi les concepts importants"
• "Quelle est la conclusion ?"

Je suis là pour vous aider ! 😊"""
            else:
                return f"""✅ **Document importé avec succès !**

**📄 Fichier :** {filename}
**📁 Type :** {file_type}
**📊 Statistiques :**
• Pages : {pages}
• Mots : {word_count}
• Caractères : {char_count}

**⚠️ Mode basique activé**

Pour des analyses détaillées, vous pouvez :
1. Poser des questions simples sur le document
2. Demander un résumé
3. Chercher des informations spécifiques

Je ferai de mon mieux pour vous aider ! 😊"""
            
        except Exception as e:
            error_msg = str(e)
            return f"❌ Erreur : {error_msg[:200]}"
    
    def _extract_text_from_pdf(self, file_path):
        """Extrait COMPLÈTEMENT le texte d'un fichier PDF avec fitz"""
        try:
            doc = fitz.open(file_path)
            full_text = ""
            total_pages = len(doc)
            
            print(f"📖 Extraction PDF: {total_pages} pages à traiter...")
            
            for i, page in enumerate(doc, 1):
                try:
                    text = page.get_text()
                    if text and text.strip():
                        full_text += f"\n\n--- PAGE {i}/{total_pages} ---\n\n"
                        full_text += text.strip()
                    
                    if i % 10 == 0 or i == total_pages:
                        print(f"  📄 Page {i}/{total_pages} extraite")
                        
                except Exception as page_error:
                    print(f"  ⚠️ Erreur page {i}: {str(page_error)[:50]}")
                    full_text += f"\n\n--- PAGE {i} (ERREUR D'EXTRACTION) ---\n\n"
            
            doc.close()
            
            if not full_text.strip():
                print("⚠️ Aucun texte extrait, tentative alternative...")
                full_text = self._try_alternative_pdf_extraction(file_path)
            
            print(f"✅ Extraction PDF terminée: {len(full_text)} caractères")
            return full_text, total_pages
            
        except Exception as e:
            print(f"❌ Erreur grave lors de l'extraction du PDF: {str(e)}")
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")
    
    def _extract_text_from_pdf_pypdf2(self, file_path):
        """Extrait le texte d'un PDF avec PyPDF2 (fallback)"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                total_pages = len(pdf_reader.pages)
                
                for i, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            full_text += f"\n\n--- PAGE {i}/{total_pages} ---\n\n"
                            full_text += text.strip()
                    except Exception as page_error:
                        print(f"  ⚠️ Erreur page {i}: {str(page_error)[:50]}")
                        full_text += f"\n\n--- PAGE {i} (ERREUR D'EXTRACTION) ---\n\n"
                
                return full_text, total_pages
        except ImportError:
            raise Exception("PyPDF2 n'est pas installé. Utilisez: pip install PyPDF2")
        except Exception as e:
            raise Exception(f"Erreur PyPDF2: {str(e)}")
    
    def _try_alternative_pdf_extraction(self, file_path):
        """Tente une extraction alternative du PDF"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
        except:
            return "[Document PDF - Texte non extractible avec les méthodes standards]"
    
    def _clean_extracted_text(self, text):
        """Nettoie le texte extrait"""
        if not text:
            return text
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.replace('\x00', '').replace('\xff', '').replace('\xfe', '')
        
        return text.strip()
    
    def _extract_text_from_txt(self, file_path):
        """Extrait le texte d'un fichier texte"""
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    
                    print(f"✅ Texte extrait avec encodage {encoding}: {len(text)} caractères")
                    approx_pages = max(1, len(text) // 3000)
                    return text, approx_pages
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"⚠️ Erreur avec encodage {encoding}: {str(e)[:50]}")
                    continue
            
            raise Exception("Aucun encodage ne fonctionne")
            
        except Exception as e:
            raise Exception(f"Erreur de lecture: {str(e)}")
    
    def _detect_file_type(self, file_path):
        """Détecte le type de fichier"""
        file_extension = Path(file_path).suffix.lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            'path': file_path,
            'name': Path(file_path).name,
            'extension': file_extension,
            'mime_type': mime_type
        }
    
    def _extract_text_from_docx(self, file_path):
        """Extrait le texte d'un fichier DOCX (Word)"""
        try:
            try:
                import docx
            except ImportError:
                raise Exception("Installez 'python-docx' avec: pip install python-docx")
            
            doc = docx.Document(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text.strip())
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            full_text.append(cell.text.strip())
            
            text = "\n".join(full_text)
            approx_pages = max(1, len(text) // 3000)
            
            return text, approx_pages
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du DOCX: {str(e)}")
    
    def _extract_text_from_csv(self, file_path):
        """Extrait le texte d'un fichier CSV"""
        try:
            import csv
            
            text_lines = []
            
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        csv_reader = csv.reader(f)
                        for i, row in enumerate(csv_reader):
                            if any(cell.strip() for cell in row):
                                text_lines.append(f"Ligne {i+1}: {' | '.join(row)}")
                    break
                except UnicodeDecodeError:
                    continue
            
            text = "\n".join(text_lines)
            approx_pages = max(1, len(text) // 3000)
            
            return text, approx_pages
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du CSV: {str(e)}")
    
    def _extract_text_from_excel(self, file_path):
        """Extrait le texte d'un fichier Excel"""
        try:
            try:
                import pandas as pd
            except ImportError:
                raise Exception("Installez 'pandas' avec: pip install pandas")
            
            excel_file = pd.ExcelFile(file_path)
            all_text = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    all_text.append(f"=== Feuille: {sheet_name} ({len(df)} lignes) ===")
                    
                    if len(df.columns) > 0:
                        all_text.append("En-têtes: " + " | ".join(df.columns.astype(str)))
                    
                    for i, row in df.head(100).iterrows():
                        row_text = " | ".join([str(cell) for cell in row if pd.notna(cell)])
                        if row_text.strip():
                            all_text.append(f"Ligne {i+1}: {row_text}")
                    
                    all_text.append("")
                    
                except Exception as e:
                    all_text.append(f"⚠️ Erreur feuille '{sheet_name}': {str(e)}")
            
            text = "\n".join(all_text)
            approx_pages = max(1, len(text) // 3000)
            
            return text, approx_pages
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction d'Excel: {str(e)}")
    
    def _extract_text_from_html(self, file_path):
        """Extrait le texte d'un fichier HTML"""
        try:
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                raise Exception("Installez 'beautifulsoup4' avec: pip install beautifulsoup4")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()
            
            text = soup.get_text()
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            approx_pages = max(1, len(text) // 3000)
            
            return text, approx_pages
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction d'HTML: {str(e)}")
    
    def _extract_text_from_rtf(self, file_path):
        """Extrait le texte d'un fichier RTF"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            text = content
            text = re.sub(r'\\[a-z]+\d*', ' ', text)
            text = re.sub(r'\\\'[0-9a-f]{2}', ' ', text)
            text = re.sub(r'\{.*?\}', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            approx_pages = max(1, len(text) // 3000)
            
            return text, approx_pages
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction de RTF: {str(e)}")
    
    # Les autres méthodes utilitaires...
    
    def get_api_status(self):
        """Retourne l'état de l'API"""
        if not self._initialized:
            self.initialize()
        
        status = {
            'initialized': self._initialized,
            'api_working': self._api_working,
            'rate_limit_hit': self._rate_limit_hit,
            'groq_model': self._groq_model,
            'has_api_key': bool(self._groq_api_key),
            'active_documents': len(self.active_documents),
            'conversation_context': len(self._conversation_context),
            'user_intent': self._user_intent,
            'conversation_state': self._conversation_state
        }
        
        if self._rate_limit_hit:
            current_time = time.time()
            if current_time < self._rate_limit_reset:
                wait_seconds = self._rate_limit_reset - current_time
                status['rate_limit_reset_in'] = f"{int(wait_seconds/60)}m{int(wait_seconds%60)}s"
        
        return status

ai_engine = SmartAIAssistant()