import streamlit as st
import requests

def render_right_sidebar():
    with st.container():
        st.markdown("## 🌍 Articles Histoire et Sciences")

        search = st.text_input("🔎 Rechercher un article", key="wiki_search")

        if search:
            try:
                url = "https://fr.wikipedia.org/api/rest_v1/page/summary/" + search
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    data = r.json()
                    st.subheader(data.get("title", "Sans titre"))
                    st.write(data.get("extract", "Pas de résumé disponible."))

                    if "content_urls" in data:
                        link = data["content_urls"]["desktop"]["page"]
                        st.markdown(f"🔗 [Lire l’article complet]({link})")
                else:
                    st.warning("Article non trouvé sur Wikipédia.")

            except Exception as e:
                st.error("Erreur connexion Wikipédia")
