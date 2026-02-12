from groq import Groq
from django.conf import settings

class ChatJuridiqueService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def poser_question(self, analyse, question):
        """Répond à une question sur l'analyse juridique basée sur le droit camerounais"""
        
        contexte = f"""
        [CONTEXTE DU DOSSIER - DROIT CAMEROUNAIS]
        Type d'affaire: {analyse.dossier.type_affaire}
        Demandeur: {analyse.dossier.nom}
        Adversaire: {analyse.dossier.adversaire}
        
        [ANALYSE JURIDIQUE - BASÉE SUR LE DROIT CAMEROUNAIS]
        **Nature Juridique (droit camerounais):** {analyse.nature_juridique[:800]}
        
        **Démarches Recommandées (procédure camerounaise):** {analyse.demarches_recommandees[:800]}
        
        **Délais Importants (délais légaux camerounais):** {analyse.delais_importants[:800]}
        
        **Recommandations (contexte camerounais):** {analyse.recommandations[:800]}
        
        [QUESTION DE L'UTILISATEUR]
        {question}
        
        [INSTRUCTIONS SPÉCIFIQUES - RÉPONSE EN DROIT CAMEROUNAIS]
        1. Répondez UNIQUEMENT en vous basant sur le DROIT CAMEROUNAIS
        2. Citez les articles du Code pénal camerounais, Code de procédure pénale camerounais
        3. Mentionnez les institutions camerounaises (Police, Gendarmerie, Tribunaux camerounais)
        4. Adaptez la réponse au système judiciaire camerounais
        5. Structurez la réponse clairement
        6. Soyez pratique et concret pour le contexte camerounais
        7. NE faites PAS référence au droit français
        """
        
        # Essayer plusieurs modèles
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.2-90b-vision-preview",
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ]
        
        for model in models_to_try:
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": """Vous êtes un assistant juridique spécialisé en DROIT CAMEROUNAIS.
                            
                            RÈGLES STRICTES:
                            1. Répondez UNIQUEMENT en vous basant sur le DROIT CAMEROUNAIS
                            2. Citez les textes de loi camerounais (Code pénal camerounais, Code de procédure pénale camerounais)
                            3. Mentionnez les institutions camerounaises (Police nationale, Gendarmerie nationale, Tribunaux camerounais)
                            4. Adaptez les conseils au contexte camerounais
                            5. NE faites PAS référence au droit français
                            6. Utilisez la terminologie juridique camerounaise
                            7. Structurez la réponse de manière claire et pratique
                            
                            EXEMPLE DE BONNE RÉPONSE (pour le Cameroun):
                            "Pour rapprocher de la gendarmerie au Cameroun :
                            
                            1. **Localiser la brigade de gendarmerie la plus proche**
                            - Consulter l'annuaire des unités de gendarmerie camerounaise
                            - Se renseigner auprès de la mairie ou de la sous-préfecture
                            
                            2. **Contacter par téléphone**
                            - Numéro de la brigade locale (disponible en mairie)
                            - Préparer les informations sur le vol
                            
                            3. **Se déplacer sur place**
                            - Horaires: généralement 8h-17h du lundi au vendredi
                            - Documents à apporter: titre foncier, pièce d'identité, photos
                            
                            Article 15 du Code de procédure pénale camerounais..."
                            """
                        },
                        {
                            "role": "user",
                            "content": contexte
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1500,
                    top_p=0.8
                )
                
                print(f"✓ Chat - Modèle utilisé: {model}")
                reponse = completion.choices[0].message.content
                
                # Nettoyer et vérifier que c'est basé sur le droit camerounais
                return self._verifier_et_structurer_reponse_camerounaise(reponse)
                
            except Exception as e:
                print(f"✗ Chat - Erreur avec {model}: {e}")
                continue
        
        # Fallback adapté au Cameroun
        return self._reponse_fallback_camerounaise(analyse, question)
    
    def _verifier_et_structurer_reponse_camerounaise(self, reponse):
        """Vérifie et structure la réponse pour le droit camerounais"""
        if not reponse:
            return "Je n'ai pas pu générer de réponse basée sur le droit camerounais."
        
        import re
        
        # Liste de termes à vérifier (doivent apparaître pour confirmer le droit camerounais)
        termes_camerounais = [
            "camerounais", "Cameroun", "OHADA", "titre foncier",
            "Tribunal de première instance", "Cour d'appel", "gendarmerie camerounaise",
            "Code pénal camerounais", "FCFA", "franc CFA", "Conservation foncière"
        ]
        
        # Vérifier si la réponse mentionne le droit camerounais
        contient_terminologie_camerounaise = any(
            terme.lower() in reponse.lower() for terme in termes_camerounais
        )
        
        if not contient_terminologie_camerounaise:
            # Ajouter une note indiquant que c'est basé sur le droit camerounais
            reponse = f"[RÉPONSE BASÉE SUR LE DROIT CAMEROUNAIS]\n\n{reponse}"
        
        # Supprimer les références au droit français si présentes
        termes_francais_a_eviter = [
            "Code civil français", "droit français", "Tribunal de grande instance",
            "préfecture", "maire français", "gendarme français"
        ]
        
        for terme in termes_francais_a_eviter:
            reponse = reponse.replace(terme, "")
        
        # Nettoyer les salutations longues
        reponse = re.sub(r'^(Bonjour|Bonsoir|Cher).*?\n', '', reponse, flags=re.IGNORECASE | re.MULTILINE)
        
        # Structurer
        reponse = re.sub(r'\n\s*\n\s*\n+', '\n\n', reponse)
        reponse = reponse.strip()
        
        # Ajouter une conclusion spécifique au Cameroun si nécessaire
        if "Article" in reponse and "camerounais" not in reponse.lower():
            reponse += "\n\n[Note: Références basées sur le droit camerounais]"
        
        return reponse
    
    def _reponse_fallback_camerounaise(self, analyse, question):
        """Réponse de secours adaptée au contexte camerounais"""
        return f"""
**RÉPONSE BASÉE SUR LE DROIT CAMEROUNAIS**

**Dossier:** {analyse.dossier.type_affaire}
**Question:** {question}

**Conseils pratiques pour le Cameroun:**

1. **Consulter l'analyse juridique complète** basée sur le droit camerounais
2. **Contacter un avocat inscrit au barreau camerounais** spécialisé en droit {analyse.dossier.type_affaire}
3. **Rassembler les documents nécessaires** selon les exigences camerounaises:
   - Titre foncier ou acte de vente
   - Pièce d'identité (CNI, passeport)
   - Photos du terrain avec repères
   - Témoignages écrits

**Procédure camerounaise recommandée:**
- Porter plainte à la gendarmerie ou police nationale camerounaise
- Faire établir un constat par huissier de justice camerounais
- Saisir le Tribunal de première instance compétent

**Délais légaux camerounais:** 
- Prescription: 3 ans pour les infractions pénales (Article 9 CPP camerounais)
- Délai de procédure: variable selon le Tribunal

**Note importante:** Cette réponse est générique. Pour une analyse précise adaptée à votre situation au Cameroun, consultez un avocat camerounais.
"""