import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_color_map(palette, df, column_for_color_map):
    """
    Convert diverse inputs into a discrete color map with distinct colors for each category.

    :param palette: continuous plotly palette, a list of colors, or a mapping dictionary
    :param df: dataframe
    :param column_for_color_map: column to be color mapped
    :return: dictionary where categories are the keys, and colors are the values
    """
    # categories = df[column_for_color_map].unique()
    if column_for_color_map=="Superclass": # fixed order and categories for ClassyFire Superclass
        categories = ['Lipids and lipid-like molecules',
                        'Organoheterocyclic compounds',
                        'Benzenoids',
                        'Hydrocarbons',
                        'Hydrocarbon derivatives',
                        'Organic acids and derivatives',
                        'Organic nitrogen compounds',
                        'Organic oxygen compounds',
                        'Organohalogen compounds',
                        'Organosulfur compounds',
                        'Organophosphorus compounds',
                        'Alkaloids and derivatives',
                        'Phenylpropanoids and polyketides',
                        'Lignans, neolignans and related compounds',
                        'Nucleosides, nucleotides, and analogues',
                        'Organometallic compounds',
                        'Mixed metal/non-metal compounds',
                        'Homogeneous metal compounds',
                        'Homogeneous non-metal compounds',
                        'Inorganic salts',
                        'Miscellaneous inorganic compounds',
                        'not assigned',
                        'Organic 1,3-dipolar compounds',
                        'Acetylides',
                        'Allenes',
                        'Carbides',
                        'Organic Polymers',
                        'Organic salts',
                        'Organic cations',
                        'Organic anions',]
    else:
        categories = df[column_for_color_map].value_counts().index.tolist() # sort by frequency

    if type(palette) == str:
        # colors = px.colors.sample_colorscale(palette, len(categories)) 
        colors = getattr(px.colors.qualitative, palette) # use qualitative palettes for discrete coloring
        
        if len(colors) < len(categories):
            print(f"Warning: The provided palette '{palette}' has only {len(colors)} colors, but {len(categories)} categories exist. Colors will be repeated.")
        
        # repeat colors if not enough colors in palette - alternative: throw all remaining in 'other' category?
        repeat_colors = (colors * (len(categories) // len(colors) + 1))[:len(categories)]
        color_map = dict(zip(categories, repeat_colors))

    elif type(palette) == list:
        assert len(palette) == len(categories), "The size of the provided palette does not match the number of categories"
        color_map = dict(zip(categories, palette))
    elif type(palette) == dict:
        assert all(c in palette.keys() for c in categories), (f"The provided palette is missing categories: \
                                                              palette: {palette}, categories: {categories}")
        color_map = palette
    else:
        raise ValueError("The provided palette could not be parsed:", palette)
    return color_map


def plot_chemical_space(df, xy = ('TSNE1', 'TSNE2'),
                         nametag = '', map_on=None,
                   hover_name = 'SMILES', hover_data = ['INCHIKEY'], # minimal input requirements
                   color='lightgrey',
                   column_for_color_map = None,
                   color_type='discrete',
                   palette='Alphabet',
                   size=3, opacity=0.7, symbol='circle', height=700, width=1200):
    """
    Map data into new or onto existing chemical space plot

    :param df: data to be mapped, laoded from data/input/output_[nametag].csv
    :param nametag: nametag of data set
    :param map_on: figure where new dataset should be mapped (optional)
    :param hover_name: title of data box displayed on interactive plot
    :param hover_data: data columns to be shown in display box
    :param color: default color for data points
    :param column_for_color_map: column to be color mapped
    :param color_type: 'discrete' or 'continuous'
    :param palette: continuous plotly palette, a list of colors, or a mapping dictionary
    :param size: size of data points
    :param opacity: opacity of data points
    :param symbol: marker symbol
    :param height: height of plot
    :param width: width of the plot
    :return: figure object
    """
    print(f"Mapping {nametag} data...")

    if column_for_color_map is not None: # coloring by column
        assert column_for_color_map in df.columns, (f"Column {column_for_color_map} does not exist in dataframe. "
                                                    f"Available columns: {df.columns.tolist()}")
        if color_type== 'discrete': # discrete coloring
            print("Use {} column to color map".format(column_for_color_map))
            color_discrete_map = get_color_map(palette, df, column_for_color_map)
            input_fig = px.scatter(df, x=xy[0], y=xy[1],
                                   hover_name = hover_name, hover_data=hover_data,
                                   render_mode="webgl", height=height, width=width,
                                   color=column_for_color_map, color_discrete_map=color_discrete_map)
            input_fig.update_traces(marker=dict(size=size, opacity=opacity, symbol=symbol, line=dict(width=0)))

            # Add custom legend traces to control the opacity of the legend markers
            input_fig.update_traces(showlegend=False)
            for c in color_discrete_map:
                input_fig.add_trace(go.Scatter(x=[None], y=[None],
                    mode='markers', marker=dict(color=color_discrete_map[c], size=min(size*4, 10), opacity=1, symbol=symbol),
                    legendgroup=c, showlegend=True, name=c))

        elif color_type== 'continuous': # continuous coloring
            print("Use {} column to color map".format(column_for_color_map))

            assert type(palette) == str, "The provided continuous palette must be plotly palette name"
            color_continuous_scale = palette
            input_fig = px.scatter(df, x=xy[0], y=xy[1],
                                   hover_name=hover_name, hover_data=hover_data,
                                   render_mode="webgl", height=height, width=width,
                                   color=column_for_color_map, color_continuous_scale=color_continuous_scale)
            input_fig.update_traces(marker=dict(size=size, opacity=opacity, line=dict(width=0)))

        else:
            raise ValueError("color_type must be discrete or continuous")

    else: #single color
        print('Use single color')
        input_fig = px.scatter(df, x=xy[0], y=xy[1], 
                               hover_name=hover_name, hover_data=hover_data,
                                render_mode="webgl", height=height, width=width)
        input_fig.update_traces(marker=dict(color=color, size=size, opacity=opacity, line=dict(width=0)), 
                                name=nametag, showlegend=False)
        
        input_fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                                       marker=dict(color=color, size=12, opacity=1),
                                       legendgroup=nametag, showlegend=True, name=nametag))
    
    # build custom hovertemplate
    hovertemplate = ("<b>%{hovertext}</b><br>"
                     f"{xy[0]}=%{{x}}, {xy[1]}=%{{y}}<br>")
    for i, col in enumerate(hover_data):
        hovertemplate += f"{col}: %{{customdata[{i}]}}<br>"
    hovertemplate += "<extra></extra>"
    input_fig.update_traces(hovertemplate=hovertemplate, hoverlabel=dict(align="left"))
    
    # merge data
    if map_on is not None:
        fig = map_on
        merged_fig = go.Figure(data=fig.data + input_fig.data, layout=fig.layout)

    else:
        merged_fig = input_fig

    # keep stable aspect ratio
    merged_fig.update_yaxes(scaleanchor="x", scaleratio=0.8)

    merged_fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        # paper_bgcolor='white',
        # plot_bgcolor='white',
        font_color='black',
        xaxis=dict(title=xy[0],visible=False, showgrid=False, zeroline=False,
                    fixedrange=False),
        yaxis=dict(title=xy[1],visible=False, showgrid=False, zeroline=False,
                    fixedrange=False),
        # align legend look 
        legend_tracegroupgap=0, 
        legend_itemsizing='constant',
        title='',
        font=dict(
            family="Arial",
            size=12,
            color="black"),)

    return merged_fig


def plot_treemap(df, palette='Alphabet'):
    """
    Map ClassyFire classes as treemap

    :param df: dataframe with ClassyFire annotations
    :param palette: color palette for treemap
    :return: figure object
    """

    df_treemap = df[["Superclass", "Class", "Subclass"]].dropna(thresh=3).fillna("not assigned")
    color_discrete_map = get_color_map(palette, df_treemap, "Superclass")

    figure = px.treemap(df_treemap, path=["Superclass", "Class", "Subclass"], color='Superclass', 
                            color_discrete_map=color_discrete_map)
    
    hovertemplate = (
                        "<b>%{label}</b><br>" 
                        "Parent: %{parent}<br>" 
                        "ID: %{id}<br>"
                        "Count: %{value}<br>"
                        "<extra></extra>"
                    )
        
    figure.update_traces(hovertemplate=hovertemplate)

    return figure

def save_figure(fig, file_name, format='.png', height=700, width=1200, scale=3):
    # todo: currently, the resolution of the exported figures is very low
    output_path_static = os.path.join(PROJECT_ROOT, 'output', file_name + format)
    output_path_html = os.path.join(PROJECT_ROOT, 'output', file_name + '.html')
    fig.write_image(output_path_static, height=height, width=width, scale=scale)
    fig.write_html(output_path_html)
    print('Static figure saved to {}'.format(output_path_static))
    print('Interactive figure saved to {}'.format(output_path_html))



# deprecated
def chemical_space_plot_grey(df,
                             hover_name = 'PREFERRED_NAME', hover_data = ['CASRN', 'Superclass', 'Class', 'Subclass'],
                             size=3, opacity=0.3, symbol='circle'):
    # palette, top15, hue_order = get_color_class_mapping(folder_name, file_name) not used here
    fig_grey = px.scatter(df, x="TSNE1", y="TSNE2",
                          hover_name = hover_name, hover_data=hover_data,
                          render_mode="webgl", height=700, width=1200)

    fig_grey.update_traces(
        marker=dict(color='lightgrey',size=size, opacity=opacity, symbol=symbol, line=dict(width=0)),
        name='reference space')

    fig_grey.update_layout(
        # paper_bgcolor='white',
        # plot_bgcolor='white',
        font_color='black',
        xaxis=dict(title="TSNE1",visible=False, showgrid=False, zeroline=False, 
                    fixedrange=False),
        yaxis=dict(title="TSNE2",visible=False, showgrid=False, zeroline=False, 
                    fixedrange=False))

    return fig_grey


def map_input_data(fig, df, nametag = '',
                   hover_name = 'SMILES', hover_data = ['INCHIKEY'], # minimal input requirements
                   color='lightgrey',
                   column_for_color_map = None,
                   color_type='discrete',
                   palette='Alphabet',
                   size=3, opacity=0.7, symbol='circle', height=700, width=1200):
    """
    Map new data to existing chemical space plot

    :param fig: figure where new dataset should be mapped
    :param df: data to be mapped, laoded from data/input/output_[nametag].csv
    :param nametag: nametag of data set
    :param hover_name: title of data box displayed on interactive plot
    :param hover_data: data columns to be shown in display box
    :param color: default color for data points
    :param column_for_color_map: column to be color mapped
    :param color_type: 'discrete' or 'continuous'
    :param palette: continuous plotly palette, a list of colors, or a mapping dictionary
    :param size: size of data points
    :param opacity: opacity of data points
    :param height: height of plot
    :param width: width of the plot
    :return: figure object
    """
    print(f"Adding {nametag} data...")

    if column_for_color_map is not None: # coloring by column
        assert column_for_color_map in df.columns, f"Column {column_for_color_map} does not exist in dataframe"

        if color_type== 'discrete': # discrete coloring
            print("Use {} column to color map".format(column_for_color_map))
            color_discrete_map = get_color_map(palette, df, column_for_color_map)
            input_fig = px.scatter(df, x="TSNE1", y="TSNE2",
                                   hover_name = hover_name, hover_data=hover_data,
                                   render_mode="webgl", height=height, width=width,
                                   color=column_for_color_map, color_discrete_map=color_discrete_map)
            input_fig.update_traces(marker=dict(size=size, opacity=opacity, symbol=symbol, line=dict(width=0)))

            # Add custom legend traces to control the opacity of the legend markers
            input_fig.update_traces(showlegend=False)
            for c in color_discrete_map:
                input_fig.add_trace(go.Scatter(x=[None], y=[None],
                    mode='markers', marker=dict(color=color_discrete_map[c], size=12, opacity=1),
                    legendgroup=c, showlegend=True, name=c))

        elif color_type== 'continuous': # continuous coloring
            print("Use {} column to color map".format(column_for_color_map))
            assert type(palette) == str, "The provided continuous palette must be plotly palette name"
            color_continuous_scale = palette
            input_fig = px.scatter(df, x="TSNE1", y="TSNE2",
                                   hover_name=hover_name, hover_data=hover_data,
                                   render_mode="webgl", height=height, width=width,
                                   color=column_for_color_map, color_continuous_scale=color_continuous_scale)
            input_fig.update_traces(marker=dict(size=size, opacity=opacity, line=dict(width=0)))
        else:
            raise ValueError("color_type must be discrete or continuous")

    else: #single color
        print('Use single color')
        input_fig = px.scatter(df, x="TSNE1", y="TSNE2", hover_name=hover_name, hover_data=hover_data,
                        render_mode="webgl", height=height, width=width)
        input_fig.update_traces(marker=dict(color=color, size=size, opacity=opacity, line=dict(width=0)),
            name=nametag)
        
        input_fig.update_traces(showlegend=False)
        input_fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                                       marker=dict(color=color, size=12, opacity=1),
                                       legendgroup=nametag, showlegend=True, name=nametag))

    # merge data
    merged_fig = go.Figure(data=fig.data + input_fig.data)

    merged_fig.update_layout(
        # paper_bgcolor='white',
        # plot_bgcolor='white',
        font_color='black',
        xaxis=dict(title="TSNE1",visible=False, showgrid=False, zeroline=False,
                    fixedrange=False),
        yaxis=dict(title="TSNE2",visible=False, showgrid=False, zeroline=False,
                    fixedrange=False))

    return merged_fig


# old code for reference
def get_color_class_mapping(folder_name, file_name):
    df_reference_tsne = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', folder_name, f'output_{file_name}.csv'))
    # This is the palette I used in my publication for the top 15 most common ClassyFire Superclasses + some code snippets
    palette = ['darkslategrey', 'teal', 'aquamarine', 'darkred', 'orangered', 'mediumpurple', 'darkorchid',
                'mediumblue', 'royalblue', 'skyblue', 'darkgoldenrod', 'darkorange', 'gold',  'lightpink', 'hotpink',
                'lightgrey']

    top15 = df_reference_tsne.groupby('Superclass').count()['TSNE1'].sort_values(ascending=False).index[:15]
    df_reference_tsne['Superclass (top 15)'] = df_reference_tsne['Superclass'].where(df_reference_tsne['Superclass'].isin(top15), 'Other')
    hue_order = top15.sort_values().to_list() + ['Other']

    return palette, top15, hue_order
