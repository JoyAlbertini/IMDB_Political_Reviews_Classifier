import plotly.express as px


def filter_outside_range(df, min_rating, max_rating):
    df_filtered = df[(df['rating'] <= min_rating) | (df['rating'] >= max_rating)]
    return df_filtered


def plot_political_label_counts(df_reviews_predicted):
    label_counts = df_reviews_predicted['politics'].value_counts().reset_index()
    label_counts.columns = ['political_label', 'count']

    fig = px.bar(label_counts, x='political_label', y='count',
                 title="Number of Reviews by Political affiliation",
                 labels={"political_label": "Political Label", "count": "Number of Reviews"},
                 color='political_label',
                 color_discrete_map={'right': 'red', 'left': 'blue', 'neutral': 'green'})

    return fig


def plot_political_outliers(df_reviews_predicted):
    df_filtered = df_reviews_predicted[
        df_reviews_predicted['rating'].isin([1, 10])
    ].copy()

    df_filtered['political_label'] = df_filtered['politics'] + ' ' + df_filtered['rating'].astype(int).astype(str)

    label_counts = df_filtered['political_label'].value_counts().reset_index()
    label_counts.columns = ['political_label', 'count']

    fig = px.bar(label_counts, x='political_label', y='count',
                 title="Number of Reviews by Political Label and Vote Score",
                 labels={"political_label": "Political Label and Vote Score", "count": "Number of Reviews"},
                 color='political_label',
                 color_discrete_map={
                     'left 10': 'blue', 'left 1': 'lightblue',
                     'right 10': 'red', 'right 1': 'pink'
                 })

    return fig
def plot_box_plot_rating_politics(df_reviews_predicted):
    return plot_box_internal(df_reviews_predicted, 'rating', "Rating Distribution by Political affiliation")


def plot_box_plot_confidence_politics(df_reviews_predicted):
    return plot_box_internal(df_reviews_predicted, 'confidence', "Confidence Distribution by Political affiliation")


def plot_box_internal(df_reviews_predicted, y_label, title):
    fig = px.box(df_reviews_predicted, x='politics', y=y_label,
                 title=title,
                 labels={"politics": "Political Label", "rating": "Rating"},
                 color='politics',
                 color_discrete_map={'right': 'red', 'left': 'blue', 'neutral': 'green'})
    return fig


def custom_show_fig(fig):
    fig.update_layout(
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    fig.show(config={'displayModeBar': True,
                     'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan', 'select2d', 'lasso2d',
                                                'resetScale2d', 'toggleSpikelines', 'autoScale2d']})
