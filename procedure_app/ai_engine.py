import os
import sys

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
import fitz
import requests
from django.conf import settings
import hashlib
import time
import mimetypes
from pathlib import Path
import re

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
            cls._instance._max_context_length = 5
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
        
        # Sinon, mode démo
        return self._demo_response(message, doc_id, api_error=not self._api_working)
    
    def _get_local_response(self, message_lower, doc_id=None):
        """Gère les réponses locales sans appel API"""
        
        # Salutations
        if any(word in message_lower for word in ["bonjour", "bonsoir", "salut", "hello", "hi", "coucou", "yo", "hey"]):
            context = ""
            if doc_id and doc_id in self.active_documents:
                doc_data = self.active_documents[doc_id]
                if isinstance(doc_data, dict) and 'text' in doc_data:
                    word_count = len(doc_data['text'].split())
                    filename = doc_data.get('filename', 'un document')
                    return f"👋 Bonsoir !\n\nJ'ai analysé ton document '{filename}' ({word_count} mots).\n\nPose-moi n'importe quelle question dessus ! 😊"
            
            return "👋 Bonsoir !\n\nJe suis ton assistant IA. Comment puis-je t'aider aujourd'hui ? 😊"
        
        # Remerciements
        if any(word in message_lower for word in ["merci", "thank you", "thanks", "merci beaucoup", "merci bien"]):
            return "Je t'en prie ! 😊\n\nN'hésite pas si tu as d'autres questions !"
        
        # Au revoir
        if any(word in message_lower for word in ["au revoir", "bye", "goodbye", "à plus", "ciao", "à bientôt"]):
            return "À bientôt ! Reviens quand tu veux. 👋😊"
        
        # Présentation de l'assistant
        if any(word in message_lower for word in ["tu es qui", "qui es-tu", "c'est quoi ton nom", "ton nom", "tu t'appelles"]):
            return "Je suis ton assistant IA ! 😊\n\nTu peux me donner un nom si tu veux, sinon appelle-moi simplement 'Assistant'.\n\nJe suis là pour t'aider à analyser des documents et répondre à tes questions !"
        
        # Vérification de présence
        if any(word in message_lower for word in ["ça va", "comment ça va", "comment vas-tu", "tu vas bien"]):
            return "Ça va bien, merci ! 😄\n\nEt toi, comment vas-tu ?\n\nDis-moi comment je peux t'aider !"
        
        # Réponse à "okay"
        if message_lower in ["ok", "okay", "d'accord", "oké"]:
            return "Super ! 😊\n\nQue veux-tu savoir ou faire maintenant ?"
        
        # Réponse à "très fort"
        if "très fort" in message_lower or "très bien" in message_lower:
            return "Merci ! 😊\n\nJe fais de mon mieux pour être utile !\n\nN'hésite pas si tu as d'autres questions !"
        
        return None
    
    def _get_ai_response(self, message, doc_id=None):
        """Obtient une réponse de l'IA Groq avec gestion de contexte"""
        # Récupérer le contexte du document si disponible
        context = ""
        filename = ""
        if doc_id and doc_id in self.active_documents:
            doc_data = self.active_documents[doc_id]
            if isinstance(doc_data, dict) and 'text' in doc_data:
                context = doc_data['text']
                filename = doc_data.get('filename', 'le document')
        
        # Ajouter le message actuel au contexte de conversation
        self._conversation_context.append({"role": "user", "content": message})
        if len(self._conversation_context) > self._max_context_length * 2:
            self._conversation_context = self._conversation_context[-(self._max_context_length * 2):]
        
        # Préparer le message pour l'API avec instruction de formatage
        system_message = self._create_system_message(context, filename)
        
        # Appeler l'API
        response_text = self._call_groq_api(system_message, message, context)
        
        # Ajouter la réponse au contexte
        self._conversation_context.append({"role": "assistant", "content": response_text})
        
        # Formater la réponse pour qu'elle soit naturelle et bien structurée
        return self._format_response_natural(response_text)
    
    def _create_system_message(self, context, filename):
        """Crée le message système selon le contexte"""
        format_instructions = """
FORMATAGE IMPORTANT :
1. Utilise des PARAGRAPHES COURTS
2. Va À LA LIGNE entre les idées principales
3. Utilise des sauts de ligne pour aérer le texte
4. Évite les longs blocs de texte compacts
5. Structure ta réponse clairement
6. Pour les listes, utilise des tirets ou astérisques
"""
        
        if context:
            return f"""Tu es un assistant conversationnel français très naturel.

CONTEXTE DU DOCUMENT :
- Nom du document : {filename}
- Contenu : {context[:5000] if len(context) > 5000 else context}

INSTRUCTIONS IMPORTANTES :
1. Réponds de manière NATURELLE et CONVERSATIONNELLE
2. Utilise "je", "tu", des expressions courantes
3. Si la question concerne le document, réponds en t'appuyant sur son contenu
4. Si la question n'est pas liée au document, réponds avec tes connaissances générales
5. Évite les formules comme "selon le document" ou "le document dit que"
6. Sois bref, direct et utile
7. Si tu ne sais pas, dis-le simplement
8. Reste dans le contexte de la conversation

{format_instructions}

Pour les définitions, sois précis et clair"""
        else:
            return f"""Tu es un assistant conversationnel français très naturel.

INSTRUCTIONS IMPORTANTES :
1. Réponds de manière NATURELLE et CONVERSATIONNELLE
2. Utilise "je", "tu", des expressions courantes
3. Sois direct, utile et précis
4. Pour les définitions, donne des explications claires
5. Si tu ne sais pas quelque chose, dis-le simplement
6. Reste dans le contexte de la conversation

{format_instructions}"""
    
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
            
            # Ajouter le contexte de conversation récent
            for msg in self._conversation_context[-(self._max_context_length * 2):]:
                messages.append(msg)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": user_message})
            
            data = {
                "model": self._groq_model,
                "messages": messages,
                "max_tokens": 800,
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
                import re
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
        """Formate la réponse pour qu'elle soit naturelle et bien structurée"""
        if not text:
            return text
        
        # Nettoyer la réponse
        text = text.strip()
        
        # Supprimer les références inutiles au document
        patterns_to_remove = [
            r'^En tant qu[^\n]*assistant[^\n]*,\s*',
            r'^Selon (le|ce) document[^\n]*,\s*',
            r'^D\'après (le|ce) document[^\n]*,\s*',
            r'^Le document[^\n]*indique que[^\n]*,\s*',
            r'^Je vois que (le|ce) document[^\n]*,\s*',
            r'^Après analyse[^\n]*,\s*',
            r'^Dans (le|ce) document[^\n]*,\s*',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remplacer les formules formelles
        replacements = [
            (r"peut être défini comme", "c'est"),
            (r"est défini comme", "c'est"),
            (r"se réfère à", "c'est"),
            (r"correspond à", "c'est"),
            (r"le document mentionne que", ""),
            (r"selon le document", ""),
            (r"d'après le document", ""),
            (r"dans le contexte du document", ""),
        ]
        
        for old, new in replacements:
            text = re.sub(old, new, text, flags=re.IGNORECASE)
        
        # S'assurer que la réponse commence bien
        if text and len(text) > 0:
            text = re.sub(r'^[,\s]+', '', text)
            if text:
                text = text[0].upper() + text[1:]
        
        # AMÉLIORATION CRITIQUE : Structurer le texte avec des sauts de ligne
        
        # 1. Remplacer les points suivis d'un espace par point + saut de ligne (sauf pour les abréviations)
        text = re.sub(r'\.\s+', '.\n\n', text)
        
        # 2. Remplacer les points d'exclamation et d'interrogation
        text = re.sub(r'!\s+', '!\n\n', text)
        text = re.sub(r'\?\s+', '?\n\n', text)
        
        # 3. Pour les listes, mettre chaque élément sur une nouvelle ligne
        text = re.sub(r'\*\s+', '\n• ', text)
        text = re.sub(r'-\s+', '\n- ', text)
        
        # 4. Après les deux-points, sauter une ligne pour les longues explications
        text = re.sub(r':\s+(?=[A-Z])', ':\n\n', text)
        
        # 5. Diviser les longues phrases (plus de 150 caractères) en paragraphes
        sentences = text.split('\n\n')
        formatted_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 150:
                # Essayer de couper après une virgule ou un point-virgule
                parts = re.split(r'[,;]\s+', sentence)
                if len(parts) > 1:
                    formatted_sentences.extend(parts)
                else:
                    formatted_sentences.append(sentence)
            else:
                formatted_sentences.append(sentence)
        
        text = '\n\n'.join(formatted_sentences)
        
        # 6. Nettoyer les sauts de ligne multiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 7. Ajouter un point final si manquant (sauf si ça finit par ! ? ...)
        if text and not text.endswith(('.', '!', '?', '...')):
            text = text + '.'
        
        # 8. Supprimer les espaces multiples
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 9. Assurer que chaque ligne commence par une majuscule
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 0:
                if line[0].islower() and len(line) > 1:
                    line = line[0].upper() + line[1:]
                formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        return text.strip()
    
    def _get_rate_limit_message(self, minutes, seconds):
        """Génère un message sur la limite de taux"""
        return f"""⚠️ **Oups ! J'ai atteint ma limite quotidienne.**

Il me faut encore {minutes} minutes {int(seconds)} secondes avant de pouvoir répondre normalement.

**En attendant :**
1. Tu peux poser des questions simples
2. Je vais te répondre en mode basique
3. La limite se réinitialise automatiquement

Désolé pour ce contretemps ! 😊"""
    
    def _demo_response(self, message, doc_id=None, api_error=False):
        """Réponses de démonstration conversationnelles"""
        message_lower = message.lower().strip()
        
        # Récupérer le contexte si disponible
        context = ""
        filename = ""
        if doc_id and doc_id in self.active_documents:
            doc_data = self.active_documents[doc_id]
            if isinstance(doc_data, dict) and 'text' in doc_data:
                context = doc_data['text']
                filename = doc_data.get('filename', 'le document')
        
        # Questions sur le contenu du document
        if context:
            if any(word in message_lower for word in ["de quoi parle", "c'est quoi", "quel est le sujet", "parle de quoi", "résume", "résumé"]):
                preview = self._get_document_preview(context)
                return f"📄 **À propos de '{filename}' :**\n\n{preview}\n\nVeux-tu que je te parle d'un point spécifique ? 😊"
            
            if any(word in message_lower for word in ["conclusion", "en conclusion", "pour conclure"]):
                conclusion = self._find_conclusion(context)
                if conclusion:
                    return f"📝 **Conclusion de '{filename}' :**\n\n{conclusion}"
                else:
                    return f"Je n'ai pas trouvé de section 'conclusion' dans '{filename}'.\n\nMais je peux te faire un résumé si tu veux ! 😊"
        
        # Réponse par défaut avec document
        if context:
            word_count = len(context.split())
            return f"🤔 Je vois que tu me parles de quelque chose, mais je suis en mode basique.\n\nTon document '{filename}' fait {word_count} mots.\n\nPour des réponses précises, pose ta question plus simplement ou attends que l'IA soit disponible ! 😊"
        
        # Réponse par défaut sans document
        return f"🤔 '{message}'\n\nJe suis en mode basique pour l'instant.\n\nPour des réponses plus précises, pose ta question quand l'IA sera disponible ! 😊"
    
    def _get_document_preview(self, context):
        """Donne un aperçu intelligent du document"""
        lines = context.split('\n')
        meaningful_lines = []
        
        for line in lines[:15]:
            line_stripped = line.strip()
            if line_stripped and len(line_stripped) > 20:
                meaningful_lines.append(line_stripped[:200])
                if len(meaningful_lines) >= 5:
                    break
        
        if meaningful_lines:
            preview = '\n'.join(meaningful_lines)
            if len(context) > 1000:
                preview += "\n\n... [document plus long]"
            return preview
        
        return "Document chargé mais contenu non analysable en mode démo."
    
    def _find_conclusion(self, context):
        """Cherche une conclusion dans le document"""
        conclusion_keywords = [
            "conclusion", "en conclusion", "pour conclure", 
            "en résumé", "pour résumer", "finalement", "en définitive"
        ]
        
        context_lower = context.lower()
        
        for keyword in conclusion_keywords:
            idx = context_lower.find(keyword)
            if idx != -1:
                conclusion_start = max(0, idx - 50)
                conclusion = context[conclusion_start:conclusion_start + 600]
                return conclusion
        
        return None
    
    # Les méthodes d'extraction de texte et autres restent identiques...
    def _extract_text_from_pdf(self, file_path):
        """Extrait COMPLÈTEMENT le texte d'un fichier PDF"""
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
                print("⚠️ Aucun texte extrait, tentative avec OCR...")
                full_text = self._try_alternative_pdf_extraction(file_path)
            
            print(f"✅ Extraction PDF terminée: {len(full_text)} caractères")
            return full_text, total_pages
            
        except Exception as e:
            print(f"❌ Erreur grave lors de l'extraction du PDF: {str(e)}")
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")
    
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
                    text, pages = self._extract_text_from_pdf(file_path)
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
                elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']:
                    text, pages = self._extract_text_from_image(file_path)
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
                '.jpg': 'Image',
                '.png': 'Image',
                '.jpeg': 'Image'
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

**💬 Pose-moi n'importe quelle question sur ce document !**

Exemples de questions :
• "De quoi ça parle ?"
• "Explique-moi le concept principal"
• "Quelle est la conclusion ?"
• "Définis les termes importants"

Je suis là pour t'aider ! 😊"""
            else:
                return f"""✅ **Document importé !**

**📄 Fichier :** {filename}
**📁 Type :** {file_type}
**📊 Statistiques :**
• Pages : {pages}
• Mots : {word_count}
• Caractères : {char_count}

**⚠️ Mode basique activé**

Pour des analyses détaillées, attends que l'IA soit disponible !"""
            
        except PermissionError:
            return f"❌ Erreur : Permission refusée pour lire le fichier"
        except MemoryError:
            return f"❌ Erreur : Mémoire insuffisante"
        except Exception as e:
            error_msg = str(e)
            return f"❌ Erreur : {error_msg[:200]}"
    
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
    
    def _extract_text_from_image(self, file_path):
        """Tente d'extraire le texte d'une image (OCR)"""
        try:
            try:
                import pytesseract
                from PIL import Image
            except ImportError:
                raise Exception("Pour traiter les images, installez: pip install pytesseract pillow")
            
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img, lang='fra+eng')
                
                if not text.strip():
                    raise Exception("Aucun texte détecté dans l'image")
                
                approx_pages = max(1, len(text) // 3000)
                return text, approx_pages
            except Exception as e:
                raise Exception(f"Erreur OCR: {str(e)}")
        except Exception as e:
            raise Exception(f"Impossible d'extraire le texte de l'image: {str(e)}")
    
    def get_document_info(self, doc_id):
        """Récupère les informations d'un document chargé"""
        if doc_id in self.active_documents:
            doc_info = self.active_documents[doc_id].copy()
            if 'text' in doc_info:
                text = doc_info['text']
                lines = text.split('\n')
                preview_lines = []
                for line in lines[:10]:
                    if line.strip() and len(line.strip()) > 20:
                        preview_lines.append(line[:200])
                
                doc_info['text_preview'] = '\n'.join(preview_lines) + "..." if len(text) > 1000 else text
                doc_info['sentences'] = len(re.findall(r'[.!?]+', text))
            return doc_info
        return None
    
    def clear_document(self, doc_id):
        """Supprime un document de la mémoire"""
        if doc_id in self.active_documents:
            filename = self.active_documents[doc_id].get('filename', 'Document inconnu')
            del self.active_documents[doc_id]
            print(f"🗑️ Document supprimé : {filename}")
            return True
        return False
    
    def clear_all_documents(self):
        """Supprime tous les documents de la mémoire"""
        count = len(self.active_documents)
        self.active_documents.clear()
        self._conversation_context.clear()
        print(f"🗑️ Tous les documents supprimés ({count} documents)")
        return count
    
    def list_documents(self):
        """Liste tous les documents actifs"""
        documents = []
        for doc_id, doc_data in self.active_documents.items():
            if isinstance(doc_data, dict):
                documents.append({
                    'id': doc_id,
                    'filename': doc_data.get('filename', 'Sans nom'),
                    'type': doc_data.get('extension', '?').replace('.', '').upper(),
                    'pages': doc_data.get('pages', 0),
                    'words': doc_data.get('words', 0),
                    'size': f"{doc_data.get('file_size', 0)/1024:.1f} KB",
                    'time': time.strftime('%H:%M:%S', time.localtime(doc_data.get('timestamp', 0)))
                })
            else:
                documents.append({
                    'id': doc_id,
                    'filename': 'Document texte',
                    'type': 'TXT',
                    'preview': str(doc_data)[:100] + "..." if len(str(doc_data)) > 100 else str(doc_data)
                })
        return documents
    
    def get_document_text(self, doc_id, max_length=None):
        """Récupère le texte d'un document avec une longueur limitée"""
        if doc_id in self.active_documents:
            doc_data = self.active_documents[doc_id]
            if isinstance(doc_data, dict) and 'text' in doc_data:
                text = doc_data['text']
                if max_length and len(text) > max_length:
                    return text[:max_length] + f"\n\n... [{len(text) - max_length} caractères tronqués]"
                return text
            elif isinstance(doc_data, str):
                if max_length and len(doc_data) > max_length:
                    return doc_data[:max_length] + f"\n\n... [{len(doc_data) - max_length} caractères tronqués]"
                return doc_data
        return ""
    
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
            'conversation_context': len(self._conversation_context)
        }
        
        if self._rate_limit_hit:
            current_time = time.time()
            if current_time < self._rate_limit_reset:
                wait_seconds = self._rate_limit_reset - current_time
                status['rate_limit_reset_in'] = f"{int(wait_seconds/60)}m{int(wait_seconds%60)}s"
        
        return status
    
    def get_supported_formats(self):
        """Retourne la liste des formats supportés"""
        return {
            'PDF': ['.pdf'],
            'Word': ['.docx', '.doc'],
            'Excel': ['.xlsx', '.xls', '.ods'],
            'Texte': ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml'],
            'CSV': ['.csv'],
            'HTML': ['.html', '.htm'],
            'RTF': ['.rtf'],
            'Images': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']
        }

ai_engine = SmartAIAssistant()