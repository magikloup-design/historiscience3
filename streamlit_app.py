import streamlit as st
import openai
import json
import os
from datetime import datetime
from PIL import Image
import time
import bcrypt
import re
from right_sidebar import render_right_sidebar
import requests
from bs4 import BeautifulSoup

# CONFIG 
st.set_page_config(page_title="HistoriScience", layout="wide")

openai.api_key = "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"
MODEL_NAME = "gpt-4.1-mini"

USERS_FILE = "users.json"
CACHE_FILE = "cache.json"
LOG_FILE = "logs.json"

# ================= OFFRES & LIMITES =================
PLAN_LIMITS = {
    "free": 20 ,
    "vip": 50,
    "premium": 100,
    "ultimate": None
}

PLAN_PRICES = {
    "vip": 20,
    "premium": 50,
    "ultimate": 100
}

PLAN_NAMES = ["VIP", "Premium", "Ultimate"]

# ================= INIT SESSION =================
for key, val in {
    "logged_in": False,
    "theme": "clair",
    "mode": "Étudiant",
    "history": [],
    "current_user": None,
    "admin_view": False,
    "plan": "free",
    "msg_count": 0,
    "last_reset": time.time()
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ================= FILE UTILS =================
def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

users = load_json(USERS_FILE)
cache = load_json(CACHE_FILE)
logs = load_json(LOG_FILE)

# AJOUT ADMIN PAR DÉFAUT
if "magikarpe" not in users:
    users["magikarpe"] = {
        "password": hash_password("1234"),
        "usage": "Administrateur",
        "photo": "",
        "email": "admin@example.com",
        "age": 30
    }
    save_json(USERS_FILE, users)

# ================= THEME =================
def apply_theme():
    if st.session_state.theme == "sombre":
        st.markdown("""
        <style>
        body, .stApp { background-color: #0e1117; color: white; }
        .stTextInput input { background-color:#1c1f26; color:white; }
        .stButton button { background-color:#262730; color:white; border-radius:10px; }
        .stSelectbox select { background-color:#1c1f26; color:white; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stButton button { border-radius:10px; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ================= OFFRES PAGE =================
def show_offers():
    st.title("💎 Nos Offres")

    st.info("Clique sur le bouton retour pour revenir à la page de connexion.")
    st.info("Choisis une offre pour procéder à l'achat via notre serveur Discord officiel.")

    DISCORD_LINK = "https://discord.gg/KByM47x6Jf"

    if st.button("⬅️ Retour"):
        st.experimental_rerun()  # Recharge la page login
        st.stop()

    col0, col1, col2, col3 = st.columns(4)

    with col0:
        st.markdown("### Gratuit")
        st.markdown(f"**Limite** : {PLAN_LIMITS['free']} messages / 12 heure")
        st.markdown("**Prix** : Gratuit")
        st.info("Découvre l'IA avec un usage limité.")
        
    with col1:
        st.markdown("### VIP")
        st.markdown(f"**Limite** : {PLAN_LIMITS['vip']} messages / 12 heure")
        st.markdown(f"**Prix** : {PLAN_PRICES['vip']}€ / mois")
        st.info("Temps de réponse plus rapide")
        st.success("Redirection vers Discord pour acheter l'offre VIP.")
        st.markdown(f"[Rejoindre le serveur Discord]({DISCORD_LINK})")


    with col2:
        st.markdown("### Premium")
        st.markdown(f"**Limite** : {PLAN_LIMITS['premium']} messages / 12 heure")
        st.markdown(f"**Prix** : {PLAN_PRICES['premium']}€ / mois")
        st.info("Temps de réponse très rapide")
        st.success("Redirection vers Discord pour acheter l'offre Prenium.")
        st.markdown(f"[Rejoindre le serveur Discord]({DISCORD_LINK})")

    with col3:
        st.markdown("### Ultimate")
        st.markdown(f"**Limite** : Illimité")
        st.markdown(f"**Prix** : {PLAN_PRICES['ultimate']}€ / mois")
        st.info("Temps de réponse ultra rapide")
        st.success("Redirection vers Discord pour acheter l'offre Ultimate.")
        st.markdown(f"[Rejoindre le serveur Discord]({DISCORD_LINK})")


# ================= LOGIN / REGISTER =================
if not st.session_state.logged_in:
    st.title("🔐 HistoriScience")
    
    if st.button("Nos offres"):
        show_offers()
        st.stop()

    tab1, tab2 = st.tabs(["Connexion", "Créer un profil"])
    with tab1:
        st.subheader("Connexion")
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if user in users and check_password(pwd, users[user]["password"]):
                placeholder = st.empty()
                for i in range(1, 101, 5):
                    placeholder.progress(i)
                    placeholder.text(f"Connexion en cours... {i}%")
                    time.sleep(0.01)
                placeholder.empty()
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.session_state.plan = users[user].get("plan", "free")
                st.session_state.admin_view = users[user]["usage"].lower() == "administrateur"
                st.success(f"Bienvenue {user} !")
                st.rerun()
            else:
                st.error("Utilisateur ou mot de passe incorrect")

    with tab2:
        st.subheader("Créer un profil")
        new_user = st.text_input("Nom d'utilisateur", key="new_user")
        new_pwd = st.text_input("Mot de passe", type="password", key="new_pwd")
        age = st.number_input("Âge (≥ 13 ans)", min_value=8, max_value=120)
        email = st.text_input("Adresse e-mail")
        usage = st.selectbox("Pourquoi vas-tu utiliser l'IA ?", ["Études", "Travail", "Culture générale", "Personnel"])
        photo = st.file_uploader("Photo de profil", type=["jpg", "png", "jpeg"])
        plan_choice = st.selectbox("Choisis ton plan", ["free"] + PLAN_NAMES)

        if st.button("Créer le profil"):
            if new_user in users:
                st.error("Utilisateur déjà existant")
            elif not validate_email(email):
                st.error("Adresse e-mail invalide")
            elif new_user and new_pwd and age >= 13:
                photo_path = ""
                if photo:
                    os.makedirs("profiles", exist_ok=True)
                    photo_path = f"profiles/{new_user}.png"
                    img = Image.open(photo)
                    img.save(photo_path)
                users[new_user] = {
                    "password": hash_password(new_pwd),
                    "usage": usage,
                    "photo": photo_path,
                    "email": email,
                    "age": age,
                    "plan": plan_choice.lower()
                }
                save_json(USERS_FILE, users)
                st.success("Profil créé avec succès !")
            else:
                st.warning("Remplis tous les champs correctement (âge ≥13 et email valide)")

    st.markdown("---")
    st.subheader("🔑 Connexion rapide / Invité")
    st.info("Tu peux tester l'IA sans créer de profil, limité à 5 questions.")
    if "guest_questions" not in st.session_state:
        st.session_state.guest_questions = 0
    if st.button("Continuer en tant qu'invité"):
        st.session_state.logged_in = True
        st.session_state.current_user = "Invité"
        st.session_state.admin_view = False
        st.session_state.guest_questions = 0
        st.session_state.mode = "Étudiant"
        st.session_state.plan = "free"
        st.success("Bienvenue Invité ! Tu peux poser 5 questions maximum.")
        st.rerun()
    st.stop()


#  BIOGRAPHIES & GUIDE 
if st.session_state.logged_in and "bio_shown" not in st.session_state:
    st.markdown("---")
    st.markdown("## 👤 Biographies")

    with st.expander("Fondateur – Magikarpe"):
        st.markdown("""
        Salut ! Je suis magikarpe, développeur principal de HistoriScience.  
        J’ai conçu cette IA pour fournir des réponses claires et pédagogiques en sciences et histoire on à débuter se projet fin 2025.
        """)

    with st.expander("Co-Directeur de projet – Petitloup"):
        st.markdown("""
        Bonjour ! Je suis petitloup, co-directeur de HistoriScience.  
        Je supervise le développement des fonctionnalités avancées et l’intégration de l’IA dans vos recherches.
        """)

    st.markdown("---")
    st.markdown("## 🎓 Guide rapide d'utilisation")

    guide_pages = [
        "Page 1 : Posez vos questions en sciences ou histoire et l'IA vous répondra de façon claire.",
        "Page 2 : Utilisez le mode Étudiant pour des explications pédagogiques, ou Personnel pour des réponses concises.",
        "Page 3 : Consultez votre historique et les logs pour suivre vos questions et réponses.",
        "Page 4 : Changez le thème entre clair et sombre pour un confort optimal."
    ]

    if "guide_index" not in st.session_state:
        st.session_state.guide_index = 0

    # Sécurité bornes
    if st.session_state.guide_index < 0:
        st.session_state.guide_index = 0
    if st.session_state.guide_index > len(guide_pages) - 1:
        st.session_state.guide_index = len(guide_pages) - 1

    st.info(guide_pages[st.session_state.guide_index])

    cols = st.columns([1, 1])

    # Bouton "Précédent"
    if cols[0].button("⬅️ Précédent"):
        if st.session_state.guide_index > 0:
            st.session_state.guide_index -= 1
            st.rerun()

    # Bouton "Suivant" ou "Terminer"
    if st.session_state.guide_index < len(guide_pages) - 1:
        if cols[1].button("Suivant ➡️"):
            st.session_state.guide_index += 1
            st.rerun()
    else:
        if cols[1].button("✅ Terminer"):
            st.success("Vous êtes prêt à utiliser HistoriScience !")
            st.session_state.bio_shown = True
            st.rerun()

    # ---------- Nouveau bouton "Passer la présentation" ----------
    if st.button("⏭️ Passer la présentation"):
        st.session_state.bio_shown = True
        st.success("Vous avez passé la présentation. Bienvenue !")
        st.rerun()

    st.stop()



# SIDEBAR 
with st.sidebar:
    user_data = users.get(st.session_state.current_user, {"photo": "", "usage": "Invité", "age": "N/A", "email": "N/A"})

    if user_data["photo"]:
        st.image(user_data["photo"], width=80)

    st.markdown(f"### 👤 {st.session_state.current_user}")
    st.caption(f"Usage : {user_data['usage']} | Âge : {user_data.get('age', 'N/A')} | Email : {user_data.get('email','N/A')}")

    if st.button("🌙 Mode sombre"):
        st.session_state.theme = "sombre"
        st.rerun()

    if st.button("☀️ Mode clair"):
        st.session_state.theme = "clair"
        st.rerun()

    st.markdown("### 🎛️ Mode IA")
    if st.button("🎓 Étudiant"):
        st.session_state.mode = "Étudiant"
    if st.button("👤 Personnel"):
        st.session_state.mode = "Personnel"

    st.info(f"Mode actif : {st.session_state.mode}")

    if st.session_state.admin_view:
        st.markdown("## 🛠 PANEL ADMIN")
        new_admin = st.text_input("Nom du nouvel admin")
        new_pwd = st.text_input("Mot de passe admin", type="password")
        if st.button("➕ Créer un admin"):
            if new_admin and new_pwd:
                users[new_admin] = {
                    "password": hash_password(new_pwd),
                    "usage": "Administrateur",
                    "photo": "",
                    "email": "",
                    "age": 0
                }
                save_json(USERS_FILE, users)
                st.success(f"Admin {new_admin} créé !")

        st.markdown("### 🔎 Recherche avancée logs")
        keyword = st.text_input("Mot-clé logs")
        start_date = st.date_input("Date début", value=datetime.today())
        end_date = st.date_input("Date fin", value=datetime.today())
        if st.button("Filtrer logs"):
            results = [l for l in logs if keyword.lower() in l["question"].lower()]
            results = [l for l in results if start_date <= datetime.strptime(l["date"], "%Y-%m-%d %H:%M:%S").date() <= end_date]
            for r in results[::-1]:
                st.markdown(f"🕒 {r['date']} | 👤 {r['user']} | 🎛️ {r['mode']}")
                st.markdown(f"❓ {r['question']}")
                st.markdown(f"➡️ {r['answer']}")
                st.markdown("---")

    if st.button("🚪 Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.admin_view = False
        st.rerun()

# HEADER 
st.title("🧠 HistoriScience")
st.write("Assistant intelligent en sciences et histoire")

# PROMPT 
def build_prompt(question):
    if st.session_state.mode == "Étudiant":
        return f"Explique comme à un élève avec exemples simples. Question : {question}"
    else:
        return f"Réponds de façon concise et directe. Question : {question}"

# GPT avec nouvelle API v1
from openai import OpenAI
client = OpenAI(api_key=openai.api_key)

def ask_gpt(question):
    if question in cache:
        return cache[question]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Tu es expert en sciences et histoire. Réponds en français."},
                {"role": "user", "content": build_prompt(question)}
            ],
            temperature=0.7,
            max_tokens=800
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Erreur lors de la requête à l'IA : {e}"

    cache[question] = answer
    save_json(CACHE_FILE, cache)

    if not isinstance(logs, list):
        logs.clear()

    logs.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": st.session_state.current_user,
        "mode": st.session_state.mode,
        "question": question,
        "answer": answer
    })
    save_json(LOG_FILE, logs)

    return answer

# ================= CHAT =================
st.markdown("## 💬 Discussion")
question = st.text_input("Ta question :")

def check_limits():
    """Vérifie les limites en fonction du plan de l'utilisateur"""
    user_plan = users.get(st.session_state.current_user, {}).get("plan", "free")
    max_msg = PLAN_LIMITS.get(user_plan, 20)

    # reset toutes les heures
    if time.time() - st.session_state.last_reset > 3600:
        st.session_state.msg_count = 0
        st.session_state.last_reset = time.time()

    if max_msg is not None and st.session_state.msg_count >= max_msg:
        st.warning(f"⏰ Limite atteinte pour le plan {user_plan}. Pose une nouvelle question.")
        return False
    return True

if question:
    # vérification du nombre de caractères
    if len(question) > 250:
        st.warning("❌ Question trop longue ! Maximum 250 caractères.")
    else:
        if len(question) > 150:
            st.info("⚠️ Attention : tu es proche de la limite recommandée de 150 caractères.")

        if st.session_state.current_user == "Invité" and st.session_state.guest_questions >= 5:
            st.warning("❌ Tu as atteint la limite de 5 questions pour le mode invité.")
        elif check_limits():
            with st.spinner("🤖 L'IA réfléchit..."):
                if not isinstance(logs, list):
                    logs = []

                # demande à GPT
                try:
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "Tu es expert en sciences et histoire. Réponds en français."},
                            {"role": "user", "content": build_prompt(question)}
                        ],
                        temperature=0.7,
                        max_tokens=1000  
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = f"Erreur lors de la requête à l'IA : {e}"

                st.success(answer)
                st.session_state.history.append((question, answer))
                st.session_state.msg_count += 1

                if st.session_state.current_user == "Invité":
                    st.session_state.guest_questions += 1


# HISTORY 
with st.expander("📜 Historique"):
    for q, a in st.session_state.history[::-1]:
        st.markdown(f"**❓ {q}**")
        st.markdown(f"➡️ {a}")
        st.markdown("---")

# LOG SEARCH 
with st.expander("🔎 Recherche logs"):
    keyword = st.text_input("Mot-clé pour rechercher")
    if keyword:
        results = [l for l in logs if keyword.lower() in l["question"].lower()]
        for r in results[::-1]:
            st.markdown(f"🕒 {r['date']} | 👤 {r['user']} | 🎛️ {r['mode']}")
            st.markdown(f"❓ {r['question']}")
            st.markdown(f"➡️ {r['answer']}")
            st.markdown("---")



import streamlit as st
import requests


# ================= SIDEBAR GAUCHE =================
with st.sidebar:
    st.markdown("🌍 **Articles Histoire et Sciences**")
    st.markdown("🔎 Rechercher un article ")

    # Champ de recherche
    wiki_query = st.text_input("Mot-clé ou sujet :", key="wiki_query_sidebar")

    if wiki_query:  # On n'effectue la requête que si l'utilisateur tape quelque chose
        search_url = "https://fr.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": wiki_query,
            "format": "json",
            "utf8": 1,
            "srlimit": 1
        }
        headers = {
            "User-Agent": "HistoriScienceApp/1.0 (contact: admin@example.com)"
        }

        try:
            # Requête principale
            response = requests.get(search_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            res_json = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur de requête Wikipédia : {e}")
            st.stop()
        except ValueError:
            st.error("Impossible de parser la réponse Wikipédia.")
            st.stop()

        # Résultat de recherche
        search_results = res_json.get("query", {}).get("search")
        if search_results:
            page_title = search_results[0]["title"]
            summary_url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{page_title}"

            try:
                summary_res = requests.get(summary_url, headers=headers, timeout=5).json()
            except Exception as e:
                st.error(f"Impossible de récupérer le résumé : {e}")
                st.stop()

            st.markdown(
                f"### [{summary_res.get('title')}]({summary_res.get('content_urls', {}).get('desktop', {}).get('page', '#')})"
            )
            st.markdown(summary_res.get("extract", "Résumé non disponible"))
            if "thumbnail" in summary_res and summary_res["thumbnail"]:
                st.image(summary_res["thumbnail"]["source"], width=200)
        else:
            st.warning("Article non trouvé directement sur Wikipédia.")
            wiki_search_link = f"https://fr.wikipedia.org/w/index.php?search={wiki_query.replace(' ', '+')}"
            st.markdown(f"[Voir tous les résultats sur Wikipédia]({wiki_search_link})")
