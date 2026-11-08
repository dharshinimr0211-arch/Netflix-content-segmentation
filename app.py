
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Netflix Content Segmentation",
    layout="wide"
)

# Colours
BLACK = "#000000"
BLUE = "#242f9b"
LAVENDER = "#d1d5f6"
WHITE = "#ffffff"

# Page styling
st.markdown("""
<style>
.stApp {
    background-color: #000000;
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 2px solid #242f9b;
}

[data-testid="stHeader"] {
    display: none;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

h1, h2, h3 {
    color: #ffffff;
}

p, label {
    color: #d1d5f6;
}

[data-testid="stMetric"] {
    background-color: #111111;
    border: 1px solid #242f9b;
    padding: 18px;
    border-radius: 6px;
}

[data-testid="stMetricValue"] {
    color: #d1d5f6;
}

[data-testid="stSidebar"] hr {
    border-color: #242f9b;
}

div.stButton > button {
    background-color: #242f9b;
    color: #ffffff;
    border: none;
    border-radius: 5px;
}

div.stButton > button:hover {
    background-color: #d1d5f6;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)


# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("Netflix_Clustered_Data.csv")


df = load_data()


# Chart styling
def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BLACK,
        plot_bgcolor=BLACK,
        font=dict(color=WHITE, size=13),
        height=height,
        margin=dict(l=20, r=20, t=45, b=35),
        colorway=[BLUE, LAVENDER],
        showlegend=True
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#292929"
    )

    return fig


# Genre counts
def get_genres(data):
    return (
        data["listed_in"]
        .dropna()
        .str.split(", ")
        .explode()
        .value_counts()
    )


# Sidebar navigation
st.sidebar.title("Netflix Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Cluster Analysis",
        "Visualizations",
        "Explore Titles"
    ]
)


# Overview
if page == "Overview":

    st.title("Netflix Content Segmentation")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Titles", f"{len(df):,}")
    col2.metric("Movies", f"{(df['type'] == 'Movie').sum():,}")
    col3.metric("TV Shows", f"{(df['type'] == 'TV Show').sum():,}")
    col4.metric("Clusters", df["Cluster"].nunique())

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Cluster Distribution")

        cluster_counts = (
            df["Cluster"]
            .value_counts()
            .sort_index()
            .rename_axis("Cluster")
            .reset_index(name="Titles")
        )

        fig = px.bar(
            cluster_counts,
            x="Cluster",
            y="Titles",
            text="Titles",
            color_discrete_sequence=[BLUE]
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with col2:
        st.subheader("Content Types")

        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Titles"]

        fig = px.pie(
            type_counts,
            names="Type",
            values="Titles",
            hole=0.5,
            color_discrete_sequence=[BLUE, LAVENDER]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )


# Cluster Analysis
elif page == "Cluster Analysis":

    st.title("Cluster Analysis")

    selected_cluster = st.selectbox(
        "Select Cluster",
        sorted(df["Cluster"].unique())
    )

    cluster_df = df[df["Cluster"] == selected_cluster]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Titles", len(cluster_df))
    col2.metric(
        "Movies",
        (cluster_df["type"] == "Movie").sum()
    )
    col3.metric(
        "TV Shows",
        (cluster_df["type"] == "TV Show").sum()
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Types")

        type_counts = (
            cluster_df["type"]
            .value_counts()
            .reset_index()
        )

        type_counts.columns = ["Type", "Titles"]

        fig = px.bar(
            type_counts,
            x="Type",
            y="Titles",
            color_discrete_sequence=[BLUE]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with col2:
        st.subheader("Top Genres")

        genre_counts = (
            get_genres(cluster_df)
            .head(10)
            .sort_values()
            .rename_axis("Genre")
            .reset_index(name="Titles")
        )

        fig = px.bar(
            genre_counts,
            x="Titles",
            y="Genre",
            orientation="h",
            color_discrete_sequence=[LAVENDER]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("Titles")

    st.dataframe(
        cluster_df[
            ["title", "type", "release_year",
             "rating", "duration", "listed_in"]
        ],
        use_container_width=True,
        hide_index=True
    )


# Visualizations
elif page == "Visualizations":

    st.title("Visualizations")

    visualizations = [
        (
            "Cluster Distribution",
            "images/final_cluster_distribution.png"
        ),
        (
            "Genre Distribution",
            "images/final_genre_heatmap.png"
        ),
        (
            "Content Type Distribution",
            "images/final_content_type_distribution.png"
        )
    ]

    for title, path in visualizations:
        st.subheader(title)
        st.image(path, use_container_width=True)


# Explore Titles
elif page == "Explore Titles":

    st.title("Explore Netflix Titles")

    col1, col2 = st.columns(2)

    with col1:
        selected_cluster = st.selectbox(
            "Cluster",
            ["All"] + sorted(df["Cluster"].unique().tolist())
        )

    with col2:
        selected_type = st.selectbox(
            "Content Type",
            ["All"] + sorted(df["type"].dropna().unique().tolist())
        )

    genre_options = sorted(
        set(
            genre
            for genres in df["listed_in"].dropna().str.split(", ")
            for genre in genres
        )
    )

    selected_genre = st.selectbox(
        "Genre",
        ["All"] + genre_options
    )

    search = st.text_input("Search by title")

    filtered_df = df.copy()

    if selected_cluster != "All":
        filtered_df = filtered_df[
            filtered_df["Cluster"] == selected_cluster
        ]

    if selected_type != "All":
        filtered_df = filtered_df[
            filtered_df["type"] == selected_type
        ]

    if selected_genre != "All":
        filtered_df = filtered_df[
            filtered_df["listed_in"].str.contains(
                selected_genre,
                regex=False,
                na=False
            )
        ]

    if search:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(
                search,
                case=False,
                regex=False,
                na=False
            )
        ]

    st.markdown("---")

    st.metric("Matching Titles", len(filtered_df))

    st.dataframe(
        filtered_df[
            ["title", "type", "release_year",
             "rating", "duration", "listed_in", "Cluster"]
        ],
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Results",
        data=csv,
        file_name="filtered_netflix_titles.csv",
        mime="text/csv"
    )
