import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit_lottie import st_lottie

# Streamlit Page Configuration
st.set_page_config(
    page_title="Movie Recommendation System 🎥",
    page_icon="🎦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Movie Data
with open("movie_data.pkl", "rb") as file:
    loaded_data = pickle.load(file)
movie_data = pd.DataFrame.from_dict(loaded_data)

# Load Precomputed Similarity Scores
with open("similarity_score_precalculated.pkl", "rb") as file:
    similarity_score_precalculated = pickle.load(file)

# TMDB API Call Function
def tmdbApiCall(movieId):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movieId}?api_key=ae4b64fbc590eaa5c99a25546af4729e&language=en-US'
    )
    return response.json() if response.status_code == 200 else {}

# Recommendation Function
def recom(movie, num_recommendations):
    try:
        movie_index = movie_data[movie_data['title'] == movie].index[0]
        similarity_scores = similarity_score_precalculated[movie_index]
        similarity_list = list(enumerate(similarity_scores))
        top_matches = sorted(similarity_list, reverse=True, key=lambda x: x[1])[1:num_recommendations + 1]

        recommendations = []
        for i in top_matches:
            movieID = movie_data.iloc[i[0]]['id']
            tmdb_response = tmdbApiCall(movieID)
            movie_details = {
                "movieID": movieID,
                "title": movie_data.iloc[i[0]]['title'],
                "genres": ", ".join(movie_data.iloc[i[0]]['genres']),
                "overview": movie_data.iloc[i[0]]['overview'],
                "keywords": ", ".join(movie_data.iloc[i[0]]['keywords']),
                "director": ", ".join(movie_data.iloc[i[0]]['crew']),
                "cast": ", ".join(movie_data.iloc[i[0]]['cast']),
                "popularity": tmdb_response.get('popularity', "N/A"),
                "release_date": tmdb_response.get('release_date', "N/A"),
                "revenue": tmdb_response.get('revenue', "N/A"),
                "tagline": tmdb_response.get('tagline', "N/A"),
                "vote_count": tmdb_response.get('vote_count', "N/A"),
                "vote_average": tmdb_response.get('vote_average', "N/A"),
                "poster_path": f"https://image.tmdb.org/t/p/w200{tmdb_response.get('poster_path')}" if tmdb_response.get('poster_path') else "N/A"
            }
            recommendations.append(movie_details)

        return recommendations
    except IndexError:
        return []

# Sidebar Inputs
st.sidebar.title("Movie Recommendations 🎥")
st.sidebar.markdown("Select a movie and get personalized recommendations.")

movie_titles = movie_data['title'].tolist()
input_movie = st.sidebar.selectbox("Select a Movie:", movie_titles)
num_recommendations = st.sidebar.slider("Number of Recommendations:", min_value=2, max_value=10, value=5)

if st.sidebar.button("Get Recommendations"):
    st.session_state["input_movie"] = input_movie
    st.session_state["recommendations"] = recom(input_movie, num_recommendations)
    st.balloons()

# Main UI
st.title("Content-Based Movie Recommendations 🎥")
st.markdown(
    """
    **Welcome to the Movie Recommendation System!**
    - Select your favorite movie from the sidebar.
    - Adjust the slider for the number of recommendations.
    - Explore personalized movie suggestions with detailed info!
    """
)

if "input_movie" in st.session_state and "recommendations" in st.session_state:
    input_movie = st.session_state["input_movie"]
    recommendations = st.session_state["recommendations"]

    tab1, tab2 = st.tabs(["Original Movie", "Recommended Movies"])

    with tab1:
        st.subheader(f"Details for: {input_movie}")
        st.markdown(
            "Use the **Recommended Movies** tab for the details of your selection! 👉"
        )
        original_movie = movie_data[movie_data['title'] == input_movie].iloc[0]
        tmdb_response = tmdbApiCall(original_movie['id'])

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(
                f"https://image.tmdb.org/t/p/w300{tmdb_response.get('poster_path')}" if tmdb_response.get('poster_path') else "N/A",
                width=200,
                caption=tmdb_response.get('tagline', "")
            )
        with col2:
            st.markdown(f"**Genres:** {', '.join(original_movie['genres'])}")
            st.markdown(f"**Overview:** {original_movie['overview']}")
            st.markdown(f"**Director:** {', '.join(original_movie['crew'])}")
            st.markdown(f"**Cast:** {', '.join(original_movie['cast'])}")
            if "show_original_details" not in st.session_state:
                st.session_state.show_original_details = False
            if st.button("Show More Details 🔥", key="original_details"):
                st.session_state.show_original_details = not st.session_state.show_original_details
            if st.session_state.show_original_details:
                with st.spinner("Loading details..."):
                    st.markdown(
                        f"""
                        <style>
                            .details-section {{
                                font-family: Arial, sans-serif;
                                color: #4A4A4A;
                                padding: 10px;
                                background-color: #F8F8F8;
                                border-radius: 8px;
                                margin-top: 10px;
                                transition: all 0.3s ease-in-out;
                            }}
                        </style>
                        <div class="details-section">
                            <b>Release Date:</b> {tmdb_response.get('release_date', 'N/A')}<br>
                            <b>Revenue:</b> {tmdb_response.get('revenue', 'N/A')}<br>
                            <b>Popularity:</b> {tmdb_response.get('popularity', 'N/A')}<br>
                            <b>Vote Count:</b> {tmdb_response.get('vote_count', 'N/A')}<br>
                            <b>Vote Average:</b> {tmdb_response.get('vote_average', 'N/A')}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    with tab2:
        st.subheader("Recommended Movies")
        for movie in recommendations:
            with st.container():
                rec_col1, rec_col2 = st.columns([1, 3])
                with rec_col1:
                    st.image(
                        movie['poster_path'],
                        width=150,
                        caption=movie['tagline'] if movie['tagline'] != "N/A" else ""
                    )
                with rec_col2:
                    st.markdown(f"### {movie['title']}")
                    st.markdown(f"**Genres:** {movie['genres']}")
                    st.markdown(f"{movie['overview']}")
                    st.markdown(f"**Director:** {movie['director']}")
                    st.markdown(f"**Cast:** {movie['cast']}")
                    key = f"show_details_{movie['title']}"
                    if key not in st.session_state:
                        st.session_state[key] = False
                    if st.button(f"Details 🔍", key=f"button_{movie['title']}"):
                        st.session_state[key] = not st.session_state[key]
                    if st.session_state[key]:
                        with st.spinner("Loading details..."):
                            st.markdown(
                                f"""
                                <style>
                                    .details-section {{
                                        font-family: Arial, sans-serif;
                                        color: #4A4A4A;
                                        padding: 10px;
                                        background-color: #EFEFEF;
                                        border-radius: 8px;
                                        margin-top: 10px;
                                        transition: all 0.3s ease-in-out;
                                    }}
                                </style>
                                <div class="details-section">
                                    <b>Release Date:</b> {movie['release_date']}<br>
                                    <b>Revenue:</b> {movie['revenue']}<br>
                                    <b>Popularity:</b> {movie['popularity']}<br>
                                    <b>Vote Count:</b> {movie['vote_count']}<br>
                                    <b>Vote Average:</b> {movie['vote_average']}<br>
                                    <b>Keywords:</b> {movie['keywords']}<br>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            st.divider()  # Add separation between movies

# Footer
st.write("---")
st.markdown("""
    <div style="text-align: center; font-size: 1.2em; padding: 10px;">
        <strong>© PyDataLabWithRik, 2025</strong><br>
        <em>Copyright Apache License 2.0</em>
    </div>
""", unsafe_allow_html=True)
