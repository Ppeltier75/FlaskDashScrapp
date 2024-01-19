import base64
import io
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dependencies
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.corpus import stopwords
from flask_login import current_user
from io import BytesIO

def create_dash_application(flask_server):
    dash_app = Dash(server=flask_server, routes_pathname_prefix='/dash/')
    
    dash_app.layout = html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=True  # Allow multiple files to be uploaded
        ),
        html.Div(id='graphs-container'),
        html.Img(id='word-cloud-image')
    ])

    def parse_contents(contents, filename):
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename.lower():
                # Assume that the user uploaded a CSV file
                return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except Exception as e:
            print(e)
            return html.Div(['There was an error processing this file.'])

    def generate_wordcloud(data):
        text = ' '.join(review for review in data['content'])
        wordcloud = WordCloud(stopwords=set(stopwords.words('english'))).generate(text)
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

    @dash_app.callback(
        [Output('graphs-container', 'children'),
         Output('word-cloud-image', 'src')],
        [Input('upload-data', 'contents')],
        [dependencies.State('upload-data', 'filename')]
    )
    def update_output(list_of_contents, list_of_names):
        if list_of_contents is not None:
            children = []
            for contents, name in zip(list_of_contents, list_of_names):
                df = parse_contents(contents, name)
                if isinstance(df, pd.DataFrame):
                    histogram_fig = px.histogram(df, x='Rating', nbins=5, title='Distribution des Notes')
                    scatterplot_fig = px.scatter(df, x='compound', y='Rating', title='Relation entre Score Compound et Note')
                    boxplot_fig = px.box(df, x='Rating', y='compound', title='Boîte à Moustaches des Scores de Sentiment par Note', color='Rating')
                    
                    if 'content' in df.columns:
                        tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
                        tfidf = tfidf_vectorizer.fit_transform(df['content'])
                        nmf = NMF(n_components=5, random_state=0)
                        nmf.fit(tfidf)
                        feature_names = tfidf_vectorizer.get_feature_names_out()
                        topics_html = [html.Li("Topic #{}: ".format(topic_idx + 1) + " ".join([feature_names[i] for i in topic.argsort()[:-10 - 1:-1]])) for topic_idx, topic in enumerate(nmf.components_)]
                        topics_container = html.Ul(topics_html)
                    else:
                        topics_container = html.Div("No 'content' column found in the data.")

                    word_cloud_image = generate_wordcloud(df)

                    children.append(dcc.Graph(figure=histogram_fig))
                    children.append(dcc.Graph(figure=scatterplot_fig))
                    children.append(dcc.Graph(figure=boxplot_fig))
                    children.append(topics_container)
                    return children, word_cloud_image

            return html.Div("Aucune donnée à afficher."), ""
        return html.Div(), ""

    return dash_app
