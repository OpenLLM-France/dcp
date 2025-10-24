#!/usr/bin/env python3

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


tasks = {
    "Traduction du français vers l'anglais": {
        "public": True,
        "meta": {
            "feedback": [
                {
                    "id": "non_relevant",
                    "text": "non pertinente pour la requête"
                },
                {
                    "id": "fact_incorrect",
                    "text": "factuellement incorrecte"
                },
                {
                    "id": "gram_incorrect",
                    "text": "grammaticalement incorrect"
                },
                {
                    "id": "form_incorrect",
                    "text": "n'est pas conforme au format demandé"
                },
                {
                    "id": "diff_to_read",
                    "text": "difficile à lire",
                    "children": {
                        "select": "single",
                        "values": [
                            { "id": "too_short", "text": "trop brève" },
                            { "id": "too_long", "text": "trop verbeuse" }
                        ]
                    }
                },
                {
                    "id": "non_acceptable",
                    "text": "n'est pas acceptable",
                    "children": {
                        "select": "multi",
                        "values": [
                            { "id": "biased", "text": "biaisée" },
                            { "id": "toxic", "text": "toxique" },
                            { "id": "offensive", "text": "offensif" },
                            { "id": "harmful", "text": "dangereux" },
                            { "id": "personal_info", "text": "rélève des information personnelles" },
                            { "id": "non_accept_other", "text": "une autre raison" }
                        ]
                    }
                }
            ]
        },
        "prompts": [
            {
                "text": "Veuillez traduire ce texte en anglais :\n\nLa cuisine française est réputée dans le monde entier pour sa finesse et sa diversité. Avec ses nombreuses spécialités régionales comme le cassoulet, la bouillabaisse, ou le bœuf bourguignon, elle représente un patrimoine culturel important. La gastronomie française a d'ailleurs été inscrite au patrimoine culturel immatériel de l'UNESCO en 2010.",
                "generations": [
                    {
                        "params": '{"model": "ChatGPT"}',
                        "text": "French cuisine is renowned worldwide for its finesse and diversity. With its numerous regional specialties such as cassoulet, bouillabaisse, or beef bourguignon, it represents an important cultural heritage. French gastronomy was inscribed on UNESCO's Intangible Cultural Heritage list in 2010.",
                    },
                    {
                        "params": '{"model": "Claude"}',
                        "text": "French cuisine is famous around the world for its refinement and diversity. With its many regional specialties like cassoulet, bouillabaisse, or beef bourguignon, it represents an important cultural heritage. French gastronomy was actually added to UNESCO's Intangible Cultural Heritage list in 2010.",
                    },
                ],
            },
            {
                "text": "Veuillez traduire ce texte en anglais :\n\nLe vignoble français, avec ses nombreuses appellations et terroirs, produit certains des vins les plus prestigieux au monde. Des régions comme le Bordelais, la Bourgogne, la Champagne et la vallée du Rhône sont connues internationalement pour la qualité de leurs crus. La tradition viticole française remonte à l'époque romaine et reste un pilier de l'économie et de la culture nationale.",
                "generations": [
                    {
                        "params": '{"model": "ChatGPT"}',
                        "text": "The French vineyard, with its numerous appellations and terroirs, produces some of the most prestigious wines in the world. Regions such as Bordeaux, Burgundy, Champagne, and the Rhône Valley are internationally known for the quality of their wines. The French winemaking tradition dates back to the Roman era and remains a pillar of the national economy and culture.",
                    },
                    {
                        "params": '{"model": "Claude"}',
                        "text": "The French vineyard, with its numerous appellations and terroirs, produces some of the most prestigious wines in the world. Regions like Bordeaux, Burgundy, Champagne, and the Rhône Valley are internationally renowned for the quality of their vintages. French winemaking tradition dates back to Roman times and remains a cornerstone of the national economy and culture.",
                    },
                ],
            },
        ],
    },
    "Développement Python - fonction avancée": {
        "public": True,
        "meta": {
            "feedback": [
                {
                    "id": "non_relevant",
                    "text": "non pertinente pour la requête"
                },
                {
                    "id": "fact_incorrect",
                    "text": "factuellement incorrecte"
                },
                {
                    "id": "gram_incorrect",
                    "text": "grammaticalement incorrect"
                },
                {
                    "id": "form_incorrect",
                    "text": "n'est pas conforme au format demandé"
                },
                {
                    "id": "diff_to_read",
                    "text": "difficile à lire",
                    "children": {
                        "select": "single",
                        "values": [
                            { "id": "too_short", "text": "trop brève" },
                            { "id": "too_long", "text": "trop verbeuse" }
                        ]
                    }
                },
                {
                    "id": "non_acceptable",
                    "text": "n'est pas acceptable",
                    "children": {
                        "select": "multi",
                        "values": [
                            { "id": "biased", "text": "biaisée" },
                            { "id": "toxic", "text": "toxique" },
                            { "id": "offensive", "text": "offensif" },
                            { "id": "harmful", "text": "dangereux" },
                            { "id": "personal_info", "text": "rélève des information personnelles" },
                            { "id": "non_accept_other", "text": "une autre raison" }
                        ]
                    }
                }
            ]
        },
        "prompts": [
            {
                "text": "Écrivez une fonction Python qui trie une liste de dictionnaires par une clé spécifique. La fonction doit permettre le tri ascendant ou descendant.",
                "generations": [
                    {
                        "params": '{"model": "ChatGPT"}',
                        "text": "def trier_dictionnaires(liste_dicts, cle, ordre_ascendant=True):\n    \"\"\"\n    Trie une liste de dictionnaires selon une clé spécifique.\n    \n    Args:\n        liste_dicts: Liste de dictionnaires à trier\n        cle: Clé utilisée pour le tri\n        ordre_ascendant: Si True, tri ascendant, sinon descendant\n        \n    Returns:\n        Liste triée de dictionnaires\n    \"\"\"\n    if not liste_dicts:\n        return []\n        \n    # Vérifier si la clé existe dans tous les dictionnaires\n    if not all(cle in d for d in liste_dicts):\n        raise KeyError(f\"La clé '{cle}' n'existe pas dans tous les dictionnaires\")\n    \n    return sorted(liste_dicts, key=lambda x: x[cle], reverse=not ordre_ascendant)\n\n# Exemple d'utilisation\nif __name__ == \"__main__\":\n    personnes = [\n        {\"nom\": \"Dubois\", \"age\": 32, \"ville\": \"Paris\"},\n        {\"nom\": \"Martin\", \"age\": 25, \"ville\": \"Lyon\"},\n        {\"nom\": \"Bernard\", \"age\": 45, \"ville\": \"Marseille\"}\n    ]\n    \n    print(\"Tri par âge (ascendant):\")\n    print(trier_dictionnaires(personnes, \"age\"))\n    \n    print(\"Tri par nom (descendant):\")\n    print(trier_dictionnaires(personnes, \"nom\", False))",
                    },
                    {
                        "params": '{"model": "Claude"}',
                        "text": "def tri_par_cle(liste_dicts, cle, ascendant=True):\n    \"\"\"\n    Trie une liste de dictionnaires selon une clé spécifiée.\n    \n    Arguments:\n        liste_dicts (list): La liste de dictionnaires à trier\n        cle (str): La clé selon laquelle trier\n        ascendant (bool): Si True, tri ascendant; si False, tri descendant\n        \n    Retourne:\n        list: La liste triée de dictionnaires\n    \n    Lève:\n        KeyError: Si la clé n'existe pas dans tous les dictionnaires\n        TypeError: Si l'entrée n'est pas une liste de dictionnaires\n    \"\"\"\n    # Validation des entrées\n    if not isinstance(liste_dicts, list):\n        raise TypeError(\"L'entrée doit être une liste\")\n    \n    if not liste_dicts:\n        return []\n    \n    if not all(isinstance(item, dict) for item in liste_dicts):\n        raise TypeError(\"Tous les éléments doivent être des dictionnaires\")\n    \n    # Vérifier si la clé existe dans tous les dictionnaires\n    if not all(cle in d for d in liste_dicts):\n        raise KeyError(f\"La clé '{cle}' n'existe pas dans tous les dictionnaires\")\n    \n    # Trier la liste\n    return sorted(liste_dicts, key=lambda x: x[cle], reverse=not ascendant)\n\n# Exemple d'utilisation\nif __name__ == \"__main__\":\n    etudiants = [\n        {\"nom\": \"Dupont\", \"note\": 15, \"classe\": \"Terminale\"},\n        {\"nom\": \"Lambert\", \"note\": 18, \"classe\": \"Première\"},\n        {\"nom\": \"Moreau\", \"note\": 12, \"classe\": \"Terminale\"}\n    ]\n    \n    print(\"Tri par note (ascendant):\")\n    print(tri_par_cle(etudiants, \"note\"))\n    \n    print(\"Tri par nom (descendant):\")\n    print(tri_par_cle(etudiants, \"nom\", False))",
                    },
                ],
            }
        ],
    },
    "Analyse de données commerciales": {
        "public": True,
        "meta": {
            "feedback": [
                {
                    "id": "non_relevant",
                    "text": "non pertinente pour la requête"
                },
                {
                    "id": "fact_incorrect",
                    "text": "factuellement incorrecte"
                },
                {
                    "id": "gram_incorrect",
                    "text": "grammaticalement incorrect"
                },
                {
                    "id": "form_incorrect",
                    "text": "n'est pas conforme au format demandé"
                },
                {
                    "id": "diff_to_read",
                    "text": "difficile à lire",
                    "children": {
                        "select": "single",
                        "values": [
                            { "id": "too_short", "text": "trop brève" },
                            { "id": "too_long", "text": "trop verbeuse" }
                        ]
                    }
                },
                {
                    "id": "non_acceptable",
                    "text": "n'est pas acceptable",
                    "children": {
                        "select": "multi",
                        "values": [
                            { "id": "biased", "text": "biaisée" },
                            { "id": "toxic", "text": "toxique" },
                            { "id": "offensive", "text": "offensif" },
                            { "id": "harmful", "text": "dangereux" },
                            { "id": "personal_info", "text": "rélève des information personnelles" },
                            { "id": "non_accept_other", "text": "une autre raison" }
                        ]
                    }
                }
            ]
        },
        "prompts": [
            {
                "text": "Analysez ces données de vente d'une chaîne de boulangeries françaises et fournissez des insights:\n\nProduit        2021        2022        2023\nBaguettes      €120K       €125K       €128K\nCroissants     €85K        €95K        €110K\nPains spéciaux €45K        €60K        €75K\nPâtisseries    €90K        €100K       €115K",
                "generations": [
                    {
                        "params": '{"model": "ChatGPT"}',
                        "text": "Analyse des ventes de la boulangerie (2021-2023):\n\n1. Croissance globale: Les ventes ont augmenté pour tous les produits sur la période de trois ans, indiquant une croissance stable de l'entreprise.\n\n2. Produits phares: Les baguettes restent le produit le plus vendu, mais leur croissance est la plus modeste (+6,7% sur 3 ans).\n\n3. Tendances par catégorie:\n   - Pains spéciaux: Croissance la plus forte (+66,7% sur 3 ans), reflétant potentiellement un intérêt croissant pour les produits artisanaux/spéciaux.\n   - Croissants: Forte progression (+29,4% sur 3 ans), peut-être due à une amélioration de la qualité ou à une demande accrue.\n   - Pâtisseries: Croissance constante (+27,8% sur 3 ans), indiquant un marché solide.\n\n4. Répartition des ventes en 2023:\n   - Baguettes: 30% des ventes\n   - Croissants: 26% des ventes\n   - Pains spéciaux: 17% des ventes\n   - Pâtisseries: 27% des ventes\n\nRecommandations:\n- Continuer à développer la gamme de pains spéciaux qui montre la plus forte croissance\n- Analyser les raisons de la faible croissance des baguettes (concurrence, prix, qualité)\n- Envisager d'étendre la gamme de pâtisseries qui représente une part importante des ventes",
                    },
                    {
                        "params": '{"model": "Claude"}',
                        "text": "Analyse des données de vente (2021-2023):\n\n1. Évolution globale:\n   - Chiffre d'affaires total en hausse: 340K€ (2021) → 380K€ (2022) → 428K€ (2023)\n   - Croissance annuelle: +11,8% (2021-2022), +12,6% (2022-2023)\n   - Croissance cumulée sur 3 ans: +25,9%\n\n2. Analyse par produit:\n   • Baguettes:\n     - Produit générant le plus de revenus\n     - Croissance modérée: +4,2% (2021-2022), +2,4% (2022-2023)\n     - Part de marché en déclin: 35,3% (2021) → 32,9% (2022) → 29,9% (2023)\n\n   • Croissants:\n     - Deuxième source de revenus\n     - Forte croissance: +11,8% (2021-2022), +15,8% (2022-2023)\n     - Part de marché en progression: 25% (2021) → 25% (2022) → 25,7% (2023)\n\n   • Pains spéciaux:\n     - Plus forte croissance: +33,3% (2021-2022), +25% (2022-2023)\n     - Segment en émergence rapide\n     - Part de marché en hausse significative: 13,2% (2021) → 15,8% (2022) → 17,5% (2023)\n\n   • Pâtisseries:\n     - Croissance solide: +11,1% (2021-2022), +15% (2022-2023)\n     - Part de marché stable: 26,5% (2021) → 26,3% (2022) → 26,9% (2023)\n\nRecommandations:\n1. Investir davantage dans le développement des pains spéciaux qui montrent le potentiel de croissance le plus élevé\n2. Analyser la stratégie de prix et de qualité des baguettes pour stimuler leur croissance\n3. Capitaliser sur la popularité croissante des croissants et pâtisseries\n4. Envisager des offres combinées pour encourager les achats multiples",
                    },
                ],
            }
        ],
    },
}

agreements = [
    {
        'name': 'Conditions d\'utilisation - Projet OpenLLM',
        'description': 'Conditions générales régissant votre participation au projet de recherche.',
        'text': '''
## **Plateforme de collecte des données de préférence**

### **Présentation du projet**

Bienvenue sur la plateforme de collecte de données du projet OpenLLM. Ce projet de recherche vise à améliorer la qualité des modèles de langage (LLM) francophones grâce à vos retours et préférences.

Les données que vous nous aiderez à recueillir seront rendues accessibles à tous pour contribuer directement à développer des modèles de langage plus performants et mieux alignés avec les attentes des utilisateurs francophones, en particulier le modèle Lucie.

### **Objectifs de votre participation**

Votre participation consiste à :

- Lire ou créer des prompts (instructions données au modèle)
- Examiner les réponses générées par le(s) modèle(s)
- Exprimer vos préférences et fournir vos avis sur ces réponses

Vos retours nous sont précieux pour améliorer les performances et la qualité des modèles de langage.

### **Informations importantes**

**Participation volontaire et non rémunérée**

- Votre participation est entièrement volontaire et bénévole.
- Vous pouvez arrêter votre participation à tout moment.
- Aucune indemnisation n'est prévue pour cette activité.

**Critères de participation**

- Vous devez être âgé(e) d'au moins 18 ans.
- En acceptant ces conditions, vous confirmez avoir une maîtrise suffisante de la langue française.

**Durée et modalités**

- La durée de votre participation n'est pas contrainte.
- Vous pouvez participer autant de fois que vous le souhaitez durant la période d'ouverture de l'étude, à partir du 01/05/2025.

### **Protection des données**

**Collecte et anonymisation**

- Vos données de connexion seront pseudo-anonymisées (identifiants aléatoires).
- Les prompts que vous pourriez créer seront automatiquement traités pour supprimer toute information personnelle identifiable.
- Nous ne collectons pas volontairement de données sensibles (origine ethnique, orientation sexuelle, opinions politiques, croyances religieuses, données de santé, etc.).

**Important** : Veuillez éviter d'inclure des informations personnelles ou sensibles dans vos prompts ou interactions avec le modèle.

### **Risques potentiels**

Les modèles de langage étant en phase de recherche, ils peuvent parfois générer du contenu :

- En contradiction avec vos valeurs personnelles,
- Susceptible de provoquer une réaction émotionnelle ou psychique,
- Pouvant créer un inconfort ou une gêne.

Si vous êtes exposé(e) à un contenu que vous jugez inapproprié ou traumatisant :

- Signalez immédiatement le scénario ayant conduit à cette situation,
- Contactez l'équipe encadrante qui vous accompagnera si nécessaire,
- Vous pouvez également choisir de ne pas poursuivre votre participation.

### **Utilisation des données recueillies**

**Licence et réutilisation**

- Les données collectées seront publiées sous licence CC-BY-SA (Creative Commons Attribution - Partage dans les Mêmes Conditions).
- Cette licence permet la réutilisation et le partage des données, à condition de mentionner l'attribution d'origine et de partager les adaptations sous les mêmes conditions.

**Finalité**

- Les données collectées seront utilisées par OpenLLM exclusivement à l'amélioration des modèles de langage et à la recherche dans le domaine.
- Elles pourront être réutilisées par d'autres chercheurs selon les termes de la licence CC-BY-SA.

### **Bénéfices de votre participation**

En participant à cette étude, vous contribuez à :

- L'amélioration de la qualité des modèles de langage francophones
- La réduction des biais et des contenus problématiques générés par ces modèles
- L'avancement de la recherche dans le domaine de l'intelligence artificielle
- Acquérir une expérience dans l'utilisation et l'évaluation des technologies d'IA

### **Contact et assistance**

Pour toute question, signalement ou besoin d'assistance pendant votre participation :

- Utilisez la fonction de signalement disponible sur la plateforme
- Contactez l'équipe encadrante à l'adresse : [adresse email de contact]

### **Consentement**

En cliquant sur le bouton "J'accepte", vous confirmez que :

- Vous avez lu et compris les informations ci-dessus
- Vous êtes âgé(e) d'au moins 18 ans
- Vous consentez librement à participer à cette étude
- Vous acceptez que les données collectées soient publiées sous licence CC-BY-SA
''' },
    {
        'name': 'Autres conditions',
        'description': 'Autres conditions à accepter.',
        'text': '''
Autres conditions à accepter.
''' }
]

instructions = [
    { 'text': 'Ce document fait 2 à 3 pages.' }
]

def create_dummy_db():
    db = next(get_db())
    srv = DataCollectionPlatform()

    for item in agreements:
        srv.add_agreement(db, item['name'], item['description'], item['text'])

    instruction_id = None
    for item in instructions:
        instruction_id = srv.add_instruction(db, item['text'])

    for t in tasks:
        lst = srv.get_tasks(db)
        if t in [ v.name for v in lst ]:
            continue
        try:
            task_id = srv.add_task(db, t, tasks[t]['public'], tasks[t]['meta'], instruction_id)
            sys.stderr.write(f'INFO: new task id: {task_id}\n')
        except Exception as e:
            sys.stderr.write(f"ERROR: {e}\n")
            return -1

        for prompt in tasks[t]['prompts']:
            lst = srv.get_prompts(db)
            if prompt['text'] in [ v.text for v in lst ]:
                continue
            try:
                prompt_id = srv.add_prompt(db, task_id, prompt['text'])
                sys.stderr.write(f'INFO: new prompt id: {prompt_id}\n')
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                return -1

            for item in prompt['generations']:
                lst = srv.get_generations(db)
                if item['text'] in [ v.text for v in lst ]:
                    continue

                try:
                    item["params"] = json.loads(item["params"])
                except Exception as e:
                    sys.stderr.write(f'JSON:\n{item["params"]}\n')
                    sys.stderr.write(f"ERROR: {e}\n")

                params = srv.find_generation_params(db, item['params'])
                if params is None:
                    try:
                        params_id = srv.add_generation_params(db, item['params'])
                        sys.stderr.write(f'INFO: new generation params id: {params_id}\n')
                    except Exception as e:
                        sys.stderr.write(f"ERROR: {e}\n")
                        return -1
                else:
                    params_id = params['id']

                try:
                    generation_id = srv.add_generation(db, item['text'], params_id, prompt_id)
                    sys.stderr.write(f'INFO: new generation id: {generation_id}\n')
                except Exception as e:
                    sys.stderr.write(f"ERROR: {e}\n")
                    return -1


if __name__ == '__main__':
    sys.exit(create_dummy_db())
