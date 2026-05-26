import streamlit as st
import requests
import json

st.set_page_config(page_title="World Cinema Finder", page_icon="🎬", layout="wide")

LANGS = ["Tamil","Telugu","Hindi","Kannada","Malayalam","Bengali","Korean",
         "Japanese","Chinese","Spanish","French","Hollywood (English)"]
GENRES = ["Action","Thriller","Drama","Romance","Comedy","Horror",
          "Sci-Fi","Animation","Fantasy","Crime","Mystery","Historical"]
ERAS = ["1980s","1990s","2000s","2010s","2020s–Now","All time"]

st.title("🎬 World Cinema Finder")
st.caption("Free AI-powered · Real movies · 1980s to 2025")

col1, col2, col3 = st.columns(3)
with col1:
    sel_langs  = st.multiselect("🌍 Language", LANGS)
with col2:
    sel_genres = st.multiselect("🎭 Genre", GENRES)
with col3:
    sel_eras   = st.multiselect("📅 Era", ERAS)

mood    = st.text_input("💭 Mood / Vibe (optional)", placeholder="e.g. mind-bending, feel-good, dark...")
api_key = st.text_input("🔑 Groq API Key (Free)", type="password",
                         help="Get free key at console.groq.com — no credit card needed")

if st.button("🎬 Find Real Movies", use_container_width=True):
    if not api_key:
        st.warning("Please enter your Groq API key.")
    else:
        lang_part  = ", ".join(sel_langs)  if sel_langs  else "Tamil, Telugu, Hindi, Korean, Japanese, Hollywood"
        genre_part = ", ".join(sel_genres) if sel_genres else "any genre"
        era_part   = ", ".join(sel_eras)   if sel_eras   else "1980s to 2025"
        mood_part  = f"Mood/vibe: {mood}." if mood else ""

        prompt = f"""You are a world-class film curator with deep knowledge of global cinema.

List 20 REAL movies from: {lang_part}
Genres: {genre_part}
Eras: {era_part}
{mood_part}

Respond ONLY with a JSON array. No markdown. No backticks. Start with [ end with ].

[
  {{
    "title": "Exact movie title",
    "language": "Language",
    "year": "Year",
    "genre": "Genre",
    "director": "Director name",
    "rating": "IMDb rating out of 10",
    "description": "2-3 sentence plot summary and why it is worth watching",
    "streaming": "Netflix / Prime / Hotstar / etc"
  }}
]

Only real verified movies. No duplicates. Cover all requested languages."""

        with st.spinner("🔍 Finding real movies..."):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.7
                    },
                    timeout=60
                )

                if response.status_code != 200:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    st.stop()

                data     = response.json()
                full_text = data["choices"][0]["message"]["content"]

                # clean and parse
                cleaned = full_text.strip().replace("```json","").replace("```","")
                start = cleaned.find("[")
                end   = cleaned.rfind("]")

                if start == -1:
                    st.error("No movie list returned. Try again.")
                    st.code(full_text[:500])
                    st.stop()

                movies = json.loads(cleaned[start:end+1])

                st.success(f"✅ Found {len(movies)} movies!")
                st.divider()

                for i, m in enumerate(movies, 1):
                    with st.expander(
                        f"#{i}  {m.get('title','?')}  ·  {m.get('language','')}  ·  {m.get('year','')}"
                    ):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**Genre:** {m.get('genre','-')}  |  **Director:** {m.get('director','-')}")
                            st.write(m.get("description",""))
                            if m.get("streaming"):
                                st.info(f"📺 {m['streaming']}")
                        with c2:
                            st.metric("⭐ IMDb", f"{m.get('rating','?')} / 10")

            except json.JSONDecodeError as je:
                st.error(f"JSON parse error: {je}")
                st.code(full_text[:500])
            except Exception as e:
                st.error(f"Error: {e}")