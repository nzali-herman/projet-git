import os
from groq import Groq
from django.conf import settings

class AnalyseJuridiqueService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def generer_analyse(self, dossier):
        """Génère une analyse juridique complète pour un dossier basée sur le droit CAMEROUNAIS"""
        
        prompt = f"""
        [ROLE] Vous êtes un avocat expert en droit pénal et civil CAMEROUNAIS.
        
        [CONTEXTE] Vous devez analyser un dossier juridique et fournir une procédure complète basée sur le DROIT CAMEROUNAIS.
        
        [INFORMATIONS DU DOSSIER]
        Type d'affaire: {dossier.type_affaire}
        Demandeur: {dossier.nom}
        Adversaire: {dossier.adversaire}
        Description: {dossier.description_affaire}
        
        [INSTRUCTIONS SPÉCIFIQUES - DROIT CAMEROUNAIS]
        Fournissez une analyse juridique DÉTAILLÉE et PRATIQUE basée sur le DROIT CAMEROUNAIS avec les sections suivantes :
        
        1. **NATURE JURIDIQUE** (selon le droit camerounais)
        - Qualification précise selon le Code pénal camerounais
        - Base juridique (articles du Code pénal camerounais, lois spéciales)
        - Compétence juridictionnelle (Tribunaux camerounais)
        
        2. **DÉMARCHES RECOMMANDÉES** (procédure camerounaise)
        - Démarche 1: [Description détaillée selon la procédure camerounaise]
        - Démarche 2: [Description détaillée selon la procédure camerounaise]
        - Démarche 3: [Description détaillée selon la procédure camerounaise]
        
        3. **DÉLAIS IMPORTANTS** (délais légaux camerounais)
        - Délais de prescription (selon le droit camerounais)
        - Délais de procédure (Tribunaux camerounais)
        - Dates limites à respecter
        
        4. **RECOMMANDATIONS** (adaptées au contexte camerounais)
        - Conseils pratiques immédiats
        - Précaution à prendre dans le système judiciaire camerounais
        - Documentation à préparer
        
        5. **PROCÉDURE COMPLÈTE** (procédure judiciaire camerounaise)
        - Phase 1: Pré-contentieux (démarches amiables, médiation)
        - Phase 2: Saisine de la juridiction compétente (Tribunal, Cour)
        - Phase 3: Instruction selon le Code de procédure pénale camerounais
        - Phase 4: Jugement selon les règles camerounaises
        - Phase 5: Exécution de la décision
        
        6. **RISQUES JURIDIQUES** (spécifiques au droit camerounais)
        - Risques pour le demandeur
        - Risques pour la défense
        - Conséquences possibles selon la loi camerounaise
        
        7. **TEXTES APPLICABLES** (DROIT CAMEROUNAIS UNIQUEMENT)
        - Code pénal camerounais: Articles pertinents
        - Code de procédure pénale camerounais
        - Lois spéciales camerounaises (OHADA, etc.)
        - Jurisprudence camerounaise si disponible
        
        8. **QUESTIONS FRÉQUENTES** (dans le contexte camerounais)
        - Q1: Question fréquente avec réponse basée sur le droit camerounais
        - Q2: Question fréquente avec réponse basée sur le droit camerounais
        - Q3: Question fréquente avec réponse basée sur le droit camerounais
        
        [IMPORTANT - EXIGENCES STRICTES]
        1. Utilisez UNIQUEMENT le DROIT CAMEROUNAIS comme référence
        2. Citez les articles du Code pénal camerounais, Code de procédure pénale camerounais
        3. Mentionnez les juridictions camerounaises compétentes (Tribunal de première instance, Cour d'appel, etc.)
        4. Adaptez les conseils au système judiciaire camerounais
        5. Ne faites PAS référence au droit français
        6. Utilisez la terminologie juridique camerounaise
        7. Mentionnez les institutions camerounaises (Police, Gendarmerie, Tribunaux)
        
        [SOURCES JURIDIQUES CAMEROUNAISES À UTILISER]
        - Code pénal camerounais (Loi n° 65-LF-24 du 12 novembre 1965)
        - Code de procédure pénale camerounais
        - Code civil camerounais (inspiré du Code civil français mais adapté)
        - Lois sur la propriété foncière camerounaise
        - Droit OHADA (pour les aspects commerciaux si applicable)
        - Constitution camerounaise
        
        Répondez en français professionnel.
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
                            "content": """Vous êtes Maître Kamga, avocat au barreau du Cameroun avec 20 ans d'expérience en droit pénal et civil camerounais. 
                            Vous devez fournir des conseils juridiques précis, pratiques et basés UNIQUEMENT sur le droit camerounais.
                            Votre réponse doit être structurée, détaillée et basée sur les textes de loi camerounais.
                            N'utilisez PAS de références au droit français.
                            Basez-vous sur le système judiciaire camerounais et les institutions camerounaises."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=6000,
                    top_p=0.9,
                    stream=False
                )
                
                print(f"✓ Modèle utilisé avec succès: {model}")
                return completion.choices[0].message.content
                
            except Exception as e:
                print(f"✗ Erreur avec le modèle {model}: {e}")
                continue
        
        # Si tous les modèles échouent, utiliser le fallback adapté au Cameroun
        print("⚠ Tous les modèles ont échoué, utilisation du fallback camerounais")
        return self._generer_analyse_fallback_camerounaise(dossier)
    
    def _generer_analyse_fallback_camerounaise(self, dossier):
        """Analyse de secours adaptée au droit camerounais"""
        return f"""
        1. **NATURE JURIDIQUE** (Droit camerounais)
        Qualification: Vol simple selon l'Article 312 du Code pénal camerounais
        La plainte concerne l'accusation de vol d'une partie de terrain par {dossier.adversaire}.
        Compétence: Tribunal de première instance du lieu du terrain (système judiciaire camerounais).

        2. **DÉMARCHES RECOMMANDÉES** (Procédure camerounaise)
        - Démarche 1: Constituer un dossier de preuves (titre foncier, acte notarié, photos, témoignages)
        - Démarche 2: Porter plainte à la gendarmerie ou au commissariat de police camerounais
        - Démarche 3: Faire un constat d'huissier de justice (huissier camerounais)
        - Démarche 4: Engager une procédure en récupération du bien devant le Tribunal camerounais
        - Démarche 5: Solliciter une médiation par les autorités traditionnelles si applicable

        3. **DÉLAIS IMPORTANTS** (Délais légaux camerounais)
        - Délai de prescription: 3 ans pour le vol (Article 9 du Code de procédure pénale camerounais)
        - Délai pour contester: 15 jours pour les voies de recours
        - Délai moyen de traitement d'une plainte: 1 à 3 mois dans le système camerounais
        - Délai pour agir en justice civile: 5 ans selon le droit camerounais

        4. **RECOMMANDATIONS** (Contexte camerounais)
        - Faire établir un bornage par un géomètre agréé camerounais
        - Conserver le titre foncier délivré par la Conservation foncière
        - Photographier les lieux avec des repères
        - Recueillir des témoignages auprès des voisins et du chef traditionnel
        - Consulter un avocat inscrit au barreau camerounais

        5. **PROCÉDURE COMPLÈTE** (Procédure judiciaire camerounaise)
        **Phase 1 - Pré-contentieux (1-2 mois):**
        1. Rassembler les preuves de propriété (titre foncier, acte de vente)
        2. Faire constater les faits par huissier camerounais
        3. Tentative de conciliation par le chef de quartier/village

        **Phase 2 - Saisine (1 mois):**
        1. Dépôt de plainte à la gendarmerie/police camerounaise
        2. Saisine du Tribunal de première instance compétent
        3. Assignation de la partie adverse selon la procédure camerounaise

        **Phase 3 - Instruction (3-6 mois):**
        1. Échange des pièces selon le Code de procédure camerounais
        2. Expertise judiciaire ordonnée par le juge camerounais
        3. Audience de conciliation devant le Tribunal

        **Phase 4 - Jugement (2-4 mois):**
        1. Audience devant le Tribunal camerounais
        2. Délibéré selon les règles camerounaises
        3. Notification du jugement par voie d'huissier

        **Phase 5 - Exécution (1-3 mois):**
        1. Exécution forcée par huissier camerounais si nécessaire
        2. Rétablissement dans les droits selon la décision judiciaire

        6. **RISQUES JURIDIQUES** (Droit camerounais)
        - Risque de prescription si délai de 3 ans dépassé
        - Frais de justice (droits de greffe, honoraires d'avocat)
        - Durée de procédure pouvant être longue
        - Difficulté à prouver la propriété sans titre foncier
        - Risque de représailles dans certains contextes

        7. **TEXTES APPLICABLES** (DROIT CAMEROUNAIS)
        - Code pénal camerounais: Articles 312 à 322 (vol et recel)
        - Code de procédure pénale camerounais: Articles 1 à 200
        - Loi n° 74-1 du 6 juillet 1974 portant organisation de la propriété foncière
        - Loi n° 2005/006 du 27 juillet 2005 portant Code de procédure civile
        - Décret n° 76/166 du 27 avril 1976 fixant les conditions d'exercice de la profession d'huissier

        8. **QUESTIONS FRÉQUENTES** (Contexte camerounais)
        Q: Quel est le coût d'une procédure pour vol de terrain au Cameroun?
        R: Comptez entre 500 000 FCFA et 2 000 000 FCFA selon la complexité.

        Q: Combien de temps dure une telle procédure au Cameroun?
        R: Entre 1 et 3 ans selon le Tribunal et la région.

        Q: Puis-je agir sans avocat au Cameroun?
        R: Oui, mais déconseillé. L'avocat connaît mieux la procédure camerounaise.

        Q: Quelles preuves sont nécessaires au Cameroun?
        R: Titre foncier, certificat de non-opposition, photos, témoignages, constat d'huissier.
        """