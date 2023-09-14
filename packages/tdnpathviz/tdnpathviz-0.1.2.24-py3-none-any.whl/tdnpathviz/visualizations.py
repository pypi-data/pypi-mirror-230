import plotly.graph_objects as go
from plotly import subplots
import random
import teradataml as tdml
import io
from IPython.display import Image
from PIL import Image as PILImage
import imageio
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import base64
from tdnpathviz.utils import execute_query

from tqdm import tqdm
import teradataml as tdml
from teradataml import valib
import matplotlib.pyplot as plt

from tdnpathviz.clustering import compute_cluster_inertia


import cv2

import random  # Importing the random module for random number generation

def colors(n, alpha=0.8, random_seed=124):
    """
    Generates a list of n colors in the form of RGBA strings.

    Parameters:
    - n (integer): The number of colors to generate.
    - alpha (float, optional): The alpha value (opacity) for each color. Defaults to 0.8.
    - random_seed (integer, optional): The seed value used for random number generation. Defaults to 124.

    Returns:
    - ret (list): A list of RGBA strings representing the generated colors.
    """

    random.seed(random_seed)  # Seed the random number generator for consistent colors

    ret = []  # Initialize an empty list to store the generated colors

    # Generate random values for the initial color components (r, g, b)
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)

    step = 256 / n  # Calculate the step interval between each color component

    # Generate n colors
    for i in range(n):
        r += step  # Increment the red component by the step interval
        g += step  # Increment the green component by the step interval
        b += step  # Increment the blue component by the step interval

        r = int(r) % 256  # Wrap around the red component to the range 0-255
        g = int(g) % 256  # Wrap around the green component to the range 0-255
        b = int(b) % 256  # Wrap around the blue component to the range 0-255

        # Construct the RGBA string and append it to the ret list
        ret.append("rgba(" + str(r) + "," + str(g) + "," + str(b) + "," + str(alpha) + ")")

    return ret  # Return the list of generated colors



def plot_first_main_paths(myPathAnalysis, path_column='mypath', id_column='travelid', nb_paths=15, print_query=False,
                          font_size=10, width=1200, height=800, weight_column = None, weight_agg = 'count', justify='left'):
    """
        Plots the first main paths based on a given output of the teradataml NPATH function or the teradataml dataframe of its result field.

        Parameters:
        - myPathAnalysis (DataFrame or tdml.dataframe.dataframe.DataFrame): The input DataFrame containing path analysis data.
        - path_column (str, optional): The column name representing the path. Defaults to 'mypath'.
        - id_column (str or list, optional): The column name(s) representing the unique identifier(s). Defaults to 'travelid'.
        - nb_paths (int, optional): The number of main paths to plot. Defaults to 15.
        - print_query (bool, optional): Whether to print the generated query. Defaults to False.
        - font_size (int, optional): define the size of the font. Defaults is 10.
        - width (int, optional): define the width of the figure. Defaults is 1200.
        - height (int, optional): define the height of the figure. Defaults is 800.
        - weight_column (str, optional): define the column to aggregate. If None, just count the number of pathes.
          Default is None.
        - weight_agg (str, optional): when weight_column is not None, then the weight is the result of the aggregation
          defined by weight_agg on the weight_column. Permitted values are 'count', 'avg', 'max', 'min', 'sum'.
          Default is 'count'.
        - justify (str, optional): define if you want to justify 'right' or 'left' or 'both' the output sankey. Defaults is 'left'.

        Returns:
        - None (it display an interactive Sankey plot)
    """
    if type(id_column) != list:
        id_column = [id_column]

    if weight_column == None:

        if type(myPathAnalysis) != tdml.dataframe.dataframe.DataFrame:
            df_agg = myPathAnalysis.result.select(id_column+[path_column]).groupby(path_column).count()
        else:
            df_agg = myPathAnalysis.select(id_column+[path_column]).groupby(path_column).count()

        df_agg._DataFrame__execute_node_and_set_table_name(df_agg._nodeid, df_agg._metaexpr)

        query = f"""SEL
            row_number() OVER (PARTITION BY 1 ORDER BY count_{id_column[0]} DESC) as id
        ,	REGEXP_REPLACE(lower(A.{path_column}),'\\[|\\]', '') as str
        ,	count_{id_column[0]} as weight
        FROM {df_agg._table_name} A
        QUALIFY id < {nb_paths}+1"""

    else:
        if type(myPathAnalysis) != tdml.dataframe.dataframe.DataFrame:
            df_agg = myPathAnalysis.result.select(list(set(id_column + [path_column] + [weight_column]))).groupby(path_column).agg({weight_column : weight_agg})
        else:
            df_agg = myPathAnalysis.select(list(set(id_column + [path_column] + [weight_column]))).groupby(path_column).agg({weight_column : weight_agg})

        df_agg._DataFrame__execute_node_and_set_table_name(df_agg._nodeid, df_agg._metaexpr)

        query = f"""SEL
            row_number() OVER (PARTITION BY 1 ORDER BY {weight_agg}_{weight_column} DESC) as id
        ,	REGEXP_REPLACE(lower(A.{path_column}),'\\[|\\]', '') as str
        ,	{weight_agg}_{weight_column} as weight
        FROM {df_agg._table_name} A
        QUALIFY id < {nb_paths}+1"""

    df_selection = tdml.DataFrame.from_query(query)

    if justify == 'left':
        justify_query = 'AAA.id_end_temp AS id_end'
        ascending     = ''
        init          = '0'
    elif justify == 'right':
        justify_query = '''max_max_path_length - AAA.id_end_temp as id_end'''
        ascending     = ' DESC'
        init          = 'max_path_length'
    elif justify == 'both':
        justify_query = '''AAA.id_end_temp as id_end'''
        ascending     = ' DESC'
        init          = '0'

    query2 = f"""
    sel
        CC.id
    ,   CC.node_source
    ,	CC.node_target
    ,	CC.beg
    ,	CC."end"
    ,	sum(CC.weight) as weight
    FROM 
    (
    sel
        B.*
    ,	LAG(id_end,1,{init}) OVER (PARTITION BY B."path" ORDER BY B."index" ) as id_beg
    ,	B."beg" || '_' || TRIM(CAST(id_beg AS VARCHAR(200))) as node_source
    ,	B."end" || '_' || TRIM(CAST(id_end AS VARCHAR(200))) as node_target
    FROM 
    (
        SEL
            AAA.*
        ,   {justify_query}
        ,   MAX(AAA.id_end_temp) OVER (PARTITION BY AAA."path") AS max_path_length
        ,   MAX(AAA.id_end_temp) OVER (PARTITION BY 1) AS max_max_path_length
        FROM (
            sel 
                A.*
            ,	row_number() OVER (PARTITION BY A."path" ORDER BY A."index" {ascending}) as id_end_temp
            from (
                SELECT
        
                    lag(AA.token,1) IGNORE NULLS OVER (PARTITION BY AA.outkey ORDER BY AA.tokennum) as "beg"
                ,	AA.token as "end"
                ,	AA.outkey as "path"
                ,	B.weight
                ,	AA.tokennum as "index"
                ,   B.id
                FROM (
        
                    SELECT 
                        d.*
                    FROM TABLE (strtok_split_to_table({df_selection._table_name}.id, {df_selection._table_name}.str, ',')
                    RETURNS (outkey integer, tokennum integer, token varchar(200)character set unicode) ) as d 
            
                    ) AA
                ,{df_selection._table_name} B
                WHERE AA.outkey = B.id
                QUALIFY beg IS NOT NULL
            ) A
        ) AAA
    ) B
    --ORDER BY "path","index"
    ) CC
    GROUP BY 1,2,3,4,5
    """

    if print_query:
        print(query2)

    df_ready = tdml.DataFrame.from_query(query2)

    df_ready_local = df_ready.to_pandas()

    df_ready_local = df_ready_local.sort_values(by=['id','node_source','node_target'])

    labs = dict()
    labels = list(set(df_ready_local.node_source.tolist() + df_ready_local.node_target.tolist()))

    for i, label in enumerate(labels):
        labs[label] = i

    labels = ['_'.join(x.split('_')[0:(len(x.split('_')) - 1)]) for x in labels]

    df_ready_local['color'] = df_ready_local.id.map(
        {id: col for id, col in zip(list(set(df_ready_local.id)), colors(len(set(df_ready_local.id)), random_seed=45))})

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors(len(labels), random_seed=123)
        ),
        link=dict(
            source=df_ready_local.node_source.map(labs),  # indices correspond to labels, eg A1, A2, A2, B1, ...
            target=df_ready_local.node_target.map(labs),
            value=df_ready_local.weight,
            color=df_ready_local.color
        ))])

    fig.update_layout(font_size=font_size, width=width,
                      height=height)
    fig.show()

    return

def create_all_pathes_views(myPathAnalysis, root_name = 'mytest',
                            schema = None,
                            path_column='mypath', id_column='travelid', justify = 'left'):
    """
        Creates multiple views related to the given myPathAnalysis DataFrame.

        Parameters:
        - myPathAnalysis (DataFrame or tdml.dataframe.dataframe.DataFrame): The input DataFrame containing path analysis data.
        - root_name (str, optional): The root name to be used for naming the created views. Defaults to 'mytest'.
        - schema (str, optional): The schema to create the views in. Defaults to the current database schema.
        - path_column (str, optional): The column name representing the path. Defaults to 'mypath'.
        - id_column (str or list, optional): The column name(s) representing the unique identifier(s). Defaults to 'travelid'.
        - justify (str, optional): define if you want to justify 'right' or 'left' or 'both' the output sankey. Defaults is 'left'.

        Returns:
        - None
    """

    if schema is None:
        schema = execute_query('SELECT DATABASE').fetchall()[0][0]

    if type(id_column) != list:
        id_column = [id_column]

    # Create the view of my npath
    npath_view = f"{schema}.{root_name}_NPATH_VIEW"

    try:
        query = f"""
        REPLACE VIEW  {npath_view} AS
        {myPathAnalysis.sqlmr_query}
        """
    except Exception as e:
        print(str(e).split('\n')[0])
        query = f"""
        REPLACE VIEW  {npath_view} AS
        {myPathAnalysis.show_query()}
        """
    execute_query(query)
    print(f'npath view created : {npath_view}')

    # Create the aggregated view of my npath
    aggregated_npath_view = f"{schema}.{root_name}_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {aggregated_npath_view} AS
    SELECT 
        {path_column}
    ,   COUNT(*) as count_{id_column[0]}
    FROM {npath_view}
    GROUP BY 1
    """
    execute_query(query)
    print(f'aggregated npath view created : {aggregated_npath_view}')

    # Create the cleaned aggregated view of my npath
    clean_aggregated_npath_view = f"{schema}.{root_name}_CLEAN_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {clean_aggregated_npath_view} AS
    SELECT 
        row_number() OVER (PARTITION BY 1 ORDER BY count_{id_column[0]} DESC) as id
    ,	REGEXP_REPLACE(lower(A.{path_column}),'\[|\]', '') as str
    ,	count_{id_column[0]} as weight
    FROM {aggregated_npath_view} A"""
    execute_query(query)
    print(f'clean aggregated npath view created : {clean_aggregated_npath_view}')

    if justify == 'left':
        justify_query = 'AAA.id_end_temp AS id_end'
        ascending     = ''
        init          = '0'
    elif justify == 'right':
        justify_query = '''max_max_path_length - AAA.id_end_temp as id_end'''
        ascending     = ' DESC'
        init          = 'max_path_length'
    elif justify == 'both':
        justify_query = '''AAA.id_end_temp as id_end'''
        ascending     = ' DESC'
        init          = '0'

    # Create the graph view of the aggregated npath view
    graph_aggregated_npath_view =  f"{schema}.{root_name}_GRAPH_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {graph_aggregated_npath_view} AS
    SELECT
        CC.id
    ,	CC.node_source
    ,	CC.node_target
    ,	CC.beg
    ,	CC."end"
    ,	sum(CC.weight) as weight
    FROM 
    (
    sel
        B.*
    ,	LAG(id_end,1,{init}) OVER (PARTITION BY B."path" ORDER BY B."index" ) as id_beg
    ,	B."beg" || '_' || TRIM(CAST(id_beg AS VARCHAR(10))) as node_source
    ,	B."end" || '_' || TRIM(CAST(id_end AS VARCHAR(10))) as node_target
    FROM 
        (
        SEL
            AAA.*
        ,   {justify_query}
        ,   MAX(AAA.id_end_temp) OVER (PARTITION BY AAA."path") AS max_path_length
        ,   MAX(AAA.id_end_temp) OVER (PARTITION BY 1) AS max_max_path_length
        FROM (
            sel 
                A.*
            ,	row_number() OVER (PARTITION BY A."path" ORDER BY A."index" {ascending}) as id_end_temp
            from (
                SELECT
        
                    lag(AA.token,1) IGNORE NULLS OVER (PARTITION BY AA.outkey ORDER BY AA.tokennum) as "beg"
                ,	AA.token as "end"
                ,	AA.outkey as "path"
                ,	B.weight
                ,	AA.tokennum as "index"
                ,   B.id
                FROM (
                    SELECT 
                        d.*
                    FROM TABLE (strtok_split_to_table({clean_aggregated_npath_view}.id, {clean_aggregated_npath_view}.str, ',')
                    RETURNS (outkey integer, tokennum integer, token varchar(20)character set unicode) ) as d 
                ) AA
                ,   {clean_aggregated_npath_view} B
                WHERE AA.outkey = B.id
                QUALIFY beg IS NOT NULL
            ) A
        ) AAA
       ) B
    --ORDER BY "path","index"
    ) CC
    GROUP BY 1,2,3,4,5
    """
    execute_query(query)
    print(f'npath view created : {graph_aggregated_npath_view}')

    return


def scatter_plot(tddf, x_col, y_col, **kwargs):
    """
    This function generates a scatter plot based on the given parameters.

    Parameters
    ----------
    tddf : teradata DataFrame
        The DataFrame from which the plot will be generated.
    x_col : str
        The column of the DataFrame to use as the x-axis.
    y_col : str
        The column of the DataFrame to use as the y-axis.
    **kwargs :
        Additional optional parameters can be set as follows:

        width : int, optional
            The width of the plot, defaults to 600.
        height : int, optional
            The height of the plot, defaults to 600.
        row_axis_type : str, optional
            The type of axis, defaults to 'SEQUENCE'.
        series_id : str or list, optional
            The id(s) of the series, defaults to None.
        color : str, optional
            The color of the marker, defaults to 'b'.
        marker : str, optional
            The shape of the marker, defaults to 'o'.
        markersize : int, optional
            The size of the marker, defaults to 3.
        noplot : bool, optional
            If True, the plot will not be displayed, defaults to False.
        title : str, optional
            The title of the plot, defaults to '{y_col} Vs. {x_col}'.
        x_range : tuple, optional
            The x range (x_min, y_min). Default is that of TD_PLOT by default.
        y_range : tuple, optional
            The y range (y_min, x_min). Default is that of TD_PLOT by default.

    Returns
    -------
    Image
        either the image read from the stream or the Image object object containing the scatter plot (depending on the "no_plot" option).
    """

    # Fetch keyword arguments with default values
    width = kwargs.get('width', 600)
    height = kwargs.get('height', 600)
    row_axis_type = kwargs.get('row_axis_type', 'SEQUENCE')
    series_id = kwargs.get('series_id', None)
    color = kwargs.get('color', 'b')
    marker = kwargs.get('marker', 'o')
    markersize = kwargs.get('markersize', 3)
    noplot = kwargs.get('noplot', False)
    title = kwargs.get('title', f'{y_col} Vs. {x_col}')
    x_range = kwargs.get('x_range', None)
    y_range = kwargs.get('y_range', None)

    # If no series id is provided, a default one is created
    if series_id is None:
        tddf = tddf.assign(series_id=1)
        series_id = 'series_id'

    if x_range is None:
        x_range = ''
    else:
        x_range = f'XRANGE {x_range},'

    if y_range is None:
        y_range = ''
    else:
        y_range = f'YRANGE {y_range},'

    n = 1
    # If series_id is a list, its length is stored and it's joined into a comma-separated string
    if type(series_id) == list:
        n = len(series_id)
        series_id = ','.join(series_id)

    # This line is specific to teradata DataFrame structure,
    # it aims to be sure the name of the temporary view is available
    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    # SQL query to be executed using TD_PLOT
    query = f"""
    EXECUTE FUNCTION
        TD_PLOT(
            SERIES_SPEC(
            TABLE_NAME({tddf._table_name}),
            ROW_AXIS({row_axis_type}({x_col})),
            SERIES_ID({series_id}),
            PAYLOAD (
                FIELDS({y_col}),
                CONTENT(REAL)
            )
        ),
        FUNC_PARAMS(
        TITLE('{title}'),
        PLOTS[(
        TYPE('scatter'),
        MARKER('{marker}'),
        {x_range}
        {y_range}
        MARKERSIZE({markersize})
        --COLOR('{color}')
        )],
        WIDTH({width}),
        HEIGHT({height})
        )
        );
    """

    # If enabled, print the SQL query
    if tdml.display.print_sqlmr_query:
        print(query)

    # Execute the query and fetch the result
    res = execute_query(query).fetchall()

    stream_str = io.BytesIO(res[0][1 + n])

    # Return either the image read from the stream or the Image object
    if noplot:
        return imageio.imread(stream_str.getvalue())
    else:
        return Image(stream_str.getvalue())


def pair_plot(tddf, **kwargs):
    """
    This function generates a pair plot based on the given parameters.
    This function used TD_PLOT so requires Teradata 17.20 or later versions.

    Parameters
    ----------
    tddf : teradata DataFrame
        The DataFrame from which the plot will be generated.
    **kwargs :
        Additional optional parameters can be set as follows:

        width : int, optional
            The width of the plot, defaults to 600.
        height : int, optional
            The height of the plot, defaults to 600.
        row_axis_type : str, optional
            The type of axis, defaults to 'SEQUENCE'.
        series_id : str or list, optional
            The id(s) of the series, defaults to None.
        color : str, optional
            The color of the marker, defaults to 'b'.
        marker : str, optional
            The shape of the marker, defaults to 'o'.
        noplot : bool, optional
            If True, the plot will not be displayed, defaults to False.
        title : str, optional
            The title of the plot, defaults to 'pairplot'.
        markersize : int, optional
            The size of the marker, defaults to 3.

    Returns
    -------
    Image
        An Image object containing the pair plot.
    """

    # Fetch keyword arguments with default values
    width = kwargs.get('width', 600)
    height = kwargs.get('height', 600)
    row_axis_type = kwargs.get('row_axis_type', 'SEQUENCE')
    series_id = kwargs.get('series_id', None)
    color = kwargs.get('color', 'b')
    marker = kwargs.get('marker', 'o')
    noplot = kwargs.get('noplot', False)
    title = kwargs.get('title', 'pairplot')
    markersize = kwargs.get('markersize', 3)

    # If no series id is provided, a default one is created
    if series_id is None:
        tddf = tddf.assign(series_id=1)
        series_id = 'series_id'

    n = 1
    # If series_id is a list, its length is stored and it's joined into a comma-separated string
    if type(series_id) == list:
        n = len(series_id)
        series_id = ','.join(series_id)

    # This line is specific to teradata DataFrame structure,
    # it aims to be sure the name of the temporary view is available
    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    # Determine which columns to include in the plot
    if type(series_id) == list:
        columns = [c for c in list(tddf.columns) if c not in series_id]
    else:
        columns = [c for c in list(tddf.columns) if c not in [series_id]]

    series_blocks = []
    plot_blocks = []
    counter = 0

    # For each pair of columns, add a block to the series_blocks and plot_blocks lists
    for i, c_row in enumerate(columns):
        for j, c_col in enumerate(columns):
            if i < j:
                counter += 1
                # Series block for the SQL query
                series_block = f"""
                SERIES_SPEC(
                TABLE_NAME({tddf._table_name}),
                ROW_AXIS({row_axis_type}({c_row})),
                SERIES_ID({series_id}),
                PAYLOAD (
                    FIELDS({c_col}),
                    CONTENT(REAL)
                ))"""
                series_blocks.append(series_block)

                # Plot block for the SQL query
                plot_block = f"""
                (
                    ID({counter}),
                    CELL({i + 1},{j}),
                    TYPE('scatter'),
                    MARKER('{marker}'),
                    MARKERSIZE({markersize})
                    --COLOR('{color}')
                    )
                """
                plot_blocks.append(plot_block)

    series_blocks = ',\n'.join(series_blocks)
    plot_blocks = ',\n'.join(plot_blocks)

    # SQL query to be executed
    query = f"""
    EXECUTE FUNCTION
        TD_PLOT(
            {series_blocks}
        ,
        FUNC_PARAMS(
        LAYOUT({len(columns) - 1},{len(columns) - 1}),
        TITLE('{title}'),
        WIDTH({width}),
        HEIGHT({height}),
        PLOTS[
            {plot_blocks}
        ]
        )
        );
    """

    # If enabled, print the SQL query
    if tdml.display.print_sqlmr_query:
        print(query)

    # Execute the query and fetch the result
    res = execute_query(query).fetchall()

    stream_str = io.BytesIO(res[0][1 + n])

    # Return either the image read from the stream or the Image object
    if noplot:
        return imageio.imread(stream_str.getvalue())
    else:
        return Image(stream_str.getvalue())


def plot_correlation_heatmap(tddf, **kwargs):
    """
    This function calculates the correlation matrix of a DataFrame and plots a heatmap of it.
    It requires Vantage Analytic Library installed with the rights to execute its functions.

    Parameters
    ----------
    tddf : teradata DataFrame
        The DataFrame for which the correlation matrix will be calculated and plotted.
    **kwargs :
        Additional optional parameters can be set as follows:

        ax : matplotlib axis, optional
            The axis on which the plot will be displayed. If none is given, the current axis will be used. Defaults to None.
        no_plot : bool, optional
            If True, the plot will not be displayed, and the function will return the correlation matrix. Defaults to False.
        title : str, optional
            The title of the plot, defaults to an empty string.

    Returns
    -------
    DataFrame or None
        If no_plot is True, a DataFrame containing the correlation matrix is returned.
        Otherwise, None is returned, and a heatmap of the correlation matrix is plotted.
    """

    # Fetch keyword arguments with default values
    ax = kwargs.get('ax', None)
    no_plot = kwargs.get('no_plot', False)
    title = kwargs.get('title', '')

    # compute the correlation matrix in-db
    obj = tdml.valib.Matrix(data=tddf,
                       columns=list(tddf.columns),
                       type="COR")

    # download the result
    val_corr_matrix = obj.result.to_pandas().reset_index().drop('rownum', axis=1).set_index('rowname').loc[
                      list(tddf.columns), :]

    # plot the heatmap
    if no_plot:
        return val_corr_matrix
    else:
        if ax != None:
            sns.heatmap(val_corr_matrix, annot=True, cmap='coolwarm', ax=ax)
            ax.set_title(title)
        else:
            sns.heatmap(val_corr_matrix, annot=True, cmap='coolwarm')
            plt.title(title)


def plotcurves(df, field='calculated_resistance', row_axis='time_no_unit', series_id='curve_id', select_id=None,
               width=1024, height=768, noplot=False, color=None, row_axis_type='SEQUENCE', plot_type='line', legend = None):
    """
    Plot curves using TD_PLOT function from a DataFrame in Teradata.

    Parameters:
    - df: DataFrame containing the data to plot.
    - field: Field name to plot (default: 'calculated_resistance').
    - row_axis: Field name representing the x-axis (default: 'time_no_unit').
    - series_id: Field name representing the series identifier (default: 'curve_id').
    - select_id: Optional, series identifier(s) to select (can be a single value or a list) (default: None).
    - width: Width of the plot image in pixels (default: 1024).
    - height: Height of the plot image in pixels (default: 768).
    - noplot: If True, returns the image data without displaying the image (default: False).
    - color: Optional, color specification for the plot (default: None).
    - row_axis_type: Type of the row axis, either 'SEQUENCE' or 'TIME' (default: 'SEQUENCE').
    - plot_type: Type of plot, either 'line' or 'scatter' (default: 'line')
    - legend: Type of legend. If not specified, then the legend is not generated. The following options are available:
    'upper right', 'upper left', 'lower right', 'lower left', 'right', 'center left', 'center right', 'lower center',
    'upper center', 'center', 'best'. The 'best' option is the same as 'upper right'.

    Returns:
    - If noplot is True, returns the image data as a NumPy array.
    - Otherwise, displays the image.

    Note:
    - The function assumes the existence of a TD_PLOT function in the Teradata environment.
    - The function requires the 'imageio' and 'Pillow' libraries to be installed.
    """

    # Execute the DataFrame node to obtain the table name
    df._DataFrame__execute_node_and_set_table_name(df._nodeid, df._metaexpr)

    # Construct the filter clause based on select_id
    if isinstance(select_id, list):
        if len(series_id) > 0:
            filter_ = f"WHERE {series_id} IN ({','.join([str(x) for x in select_id])}),"
        else:
            filter_ = ','
    else:
        if select_id is not None:
            filter_ = f"WHERE {series_id} = {select_id},"
        else:
            filter_ = ','

    # Calculate the number of series in the DataFrame
    nb_series = df[[series_id]+[row_axis]].groupby(series_id).count().shape[0]

    # Determine the number of plots based on series_id
    n = 1
    if type(series_id) == list:
        n = len(series_id)
        series_id = ','.join(series_id)

    # Handle the color parameter
    if color == None:
        color = ''
    else:
        color = f",FORMAT('{color}')"

    # Handle the legend
    if legend == None:
        legend_ = ''
    else:
        legend_ = f"LEGEND('{legend}'),"

    # Construct the query based on the number of series
    if nb_series < 1025:
        query = f"""
        EXECUTE FUNCTION
            TD_PLOT(
                SERIES_SPEC(
                TABLE_NAME({df._table_name}),
                ROW_AXIS({row_axis_type}({row_axis})),
                SERIES_ID({series_id}),
                PAYLOAD (
                    FIELDS({field}),
                    CONTENT(REAL)
                )
            )
            {filter_}
            FUNC_PARAMS(
            TITLE('{field}'),
            PLOTS[(
            {legend_}
            TYPE('{plot_type}')
            {color}
            )],
            WIDTH({width}),
            HEIGHT({height})
            )
            );
        """
    else:
        # Create a modified DataFrame to handle a large number of series
        df_ = df.assign(**{series_id: 1})
        df_._DataFrame__execute_node_and_set_table_name(df_._nodeid, df_._metaexpr)
        query = f"""
        EXECUTE FUNCTION
            TD_PLOT(
                SERIES_SPEC(
                TABLE_NAME({df_._table_name}),
                ROW_AXIS({row_axis_type}({row_axis})),
                SERIES_ID({series_id}),
                PAYLOAD (
                    FIELDS({field}),
                    CONTENT(REAL)
                )
            )
            {filter_}
            FUNC_PARAMS(
            TITLE('{field}'),
            PLOTS[(
            {legend_}
            TYPE('scatter')
            {color}
            )],
            WIDTH({width}),
            HEIGHT({height})
            )
            );
        """

    # Print the query if tdml.display.print_sqlmr_query is True
    if tdml.display.print_sqlmr_query:
        print(query)

    # Execute the query and fetch the result
    res = execute_query(query).fetchall()

    # Get the image data from the result
    stream_str = io.BytesIO(res[0][1 + n])

    # Return the image data or display the image
    if noplot:
        return imageio.imread(stream_str.getvalue())
    else:
        return Image(stream_str.getvalue())

# This function plots curves from a DataFrame that belongs to a specific cluster.
# It copies the cluster DataFrame to a temporary table in Teradata, performs a join with the original DataFrame,
# and then calls the plotcurves function to generate the plot.
def plotcurvescluster(df, cluster, no_cluster, schema, field='calculated_resistance', row_axis='time_no_unit', series_id='CURVE_ID', select_id=None):
    """
    Plot curves from a DataFrame that belongs to a specific cluster.

    Parameters:
    - df: Original DataFrame containing the data to plot.
    - cluster: DataFrame containing the cluster information.
    - no_cluster: Cluster number to select.
    - schema: Schema name in the Teradata environment for temporary table creation.
    - field: Field name to plot (default: 'calculated_resistance').
    - row_axis: Field name representing the x-axis (default: 'time_no_unit').
    - series_id: Field name representing the series identifier (default: 'CURVE_ID').
    - select_id: Optional, series identifier(s) to select (can be a single value or a list) (default: None).

    Returns:
    - The result of the plotcurves function called on the selected DataFrame.

    Note:
    - The function assumes the existence of the plotcurves function.
    - The function assumes the availability of the 'tdml' module for DataFrame operations.
    """

    # Copy the cluster DataFrame to a temporary table in Teradata
    tdml.copy_to_sql(df=cluster,table_name='cluster_temp',if_exists='replace',schema_name=schema)

    # Create a DataFrame for the cluster temporary table
    df_cluster = tdml.DataFrame(tdml.in_schema(schema,'cluster_temp'))

    # Join the original DataFrame with the cluster DataFrame based on the cluster number and series identifier
    df_select = df.join(df_cluster[df_cluster.cluster == no_cluster],
                        how='inner',
                        on=f'{series_id}=CURVE_ID', rsuffix='r',
                        lsuffix='l')
    try:
        # Assign the selected series identifier from the left DataFrame and drop unnecessary columns
        df_select = df_select.assign(**{series_id: df_select['l_' + series_id]}).drop(
            columns=[f'l_{series_id}', 'r_CURVE_ID'])
    except:
        1==1 # Placeholder statement to handle any exception silently
    df_select.shape

    # Call the plotcurves function with the selected DataFrame and other parameters
    return plotcurves(df_select,field=field, row_axis=row_axis, series_id=series_id,select_id=select_id)


def crop_margin(image, min_distance=50, display_edges=False):
    """
    This function crops the margin of the provided image by identifying the longest lines (edges) in the image.

    Args:
    image (np.ndarray): The input image as a numpy array.
    min_distance (int, optional): The minimum distance to consider between lines. Defaults to 50.
    display_edges (bool, optional): Whether to display the image with detected lines. Defaults to False.

    Returns:
    np.ndarray: The cropped image.
    """

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Apply probabilistic Hough line transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    # If no lines were found, return the original image
    if lines is None:
        return image

    # Calculate line lengths and sort lines by length
    lines = sorted(lines, key=lambda line: np.hypot(line[0][2] - line[0][0], line[0][3] - line[0][1]), reverse=True)

    # Filter out lines that are too close to each other
    filtered_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        midpoint = [(x1 + x2) / 2, (y1 + y2) / 2]
        if all(np.hypot(midpoint[0] - ((x1_ + x2_) / 2), midpoint[1] - ((y1_ + y2_) / 2)) > min_distance for
               x1_, y1_, x2_, y2_ in filtered_lines):
            filtered_lines.append((x1, y1, x2, y2))

    # Get the longest 4 lines (expected to be the borders of the page)
    longest_lines = filtered_lines[:4]

    # Calculate direction cosines to differentiate between vertical and horizontal lines
    cosines = [np.abs((x2 - x1) / np.hypot(x2 - x1, y2 - y1)) for x1, y1, x2, y2 in longest_lines]
    sorted_indices = np.argsort(cosines)
    longest_lines = [longest_lines[i] for i in sorted_indices]

    if display_edges:
        # Draw the longest lines on the image with different colors based on their orientation
        for i, line in enumerate(longest_lines):
            x1, y1, x2, y2 = line
            if i < 2:  # horizontal lines
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green color
            else:  # vertical lines
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # red color

        # Display the image with detected lines
        cv2.imshow('Detected Lines', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    horizontal_lines = longest_lines[0:2]
    vertical_lines = longest_lines[2:]

    # Determine the y and x values among the vertical and horizontal lines respectively
    mid_y = [max(line[1], line[3]) for line in vertical_lines] + [min(line[1], line[3]) for line in vertical_lines]
    mid_x = [max(line[0], line[2]) for line in horizontal_lines] + [min(line[0], line[2]) for line in horizontal_lines]

    # Determine the min and max x and y values among the longest lines
    min_x = min(mid_x) + 2
    max_x = max(mid_x) - 2
    min_y = min(mid_y) + 2
    max_y = max(mid_y) - 2

    # Crop the image using the min and max values
    cropped_image = image[int(min_y):int(max_y), int(min_x):int(max_x)]

    # Return the cropped image
    return cropped_image


def plot_with_background_image(dataset_large, dataset_small, col_x, col_y, x_range, y_range, color_small='red',
                               **kwargs):
    """
    This function generates a scatter plot of a small dataset with a background image generated from a large dataset.

    Args:
    dataset_large (pd.DataFrame): The large dataset to be used for generating the background image.
    dataset_small (pd.DataFrame): The small dataset to be plotted.
    col_x (str): The column name for the x-axis.
    col_y (str): The column name for the y-axis.
    x_range (tuple): The range for the x-axis.
    y_range (tuple): The range for the y-axis.
    color_small (str or list): The color for the scatter plot markers. Can be a fixed color, or a column name from dataset_small.
                               If it's a column name, the color of markers will be determined by the values in this column.
                               Defaults to 'red'.

    kwargs:
    color_large (str, optional): The color for the large dataset's scatter plot. Defaults to 'b'.
    title (str, optional): The title of the plot. Defaults to None.
    x_label (str, optional): The label for the x-axis. Defaults to col_x.
    y_label (str, optional): The label for the y-axis. Defaults to col_y.
    tooltip (str, optional): The tooltip text. Defaults to None.

    Returns:
    None
    """

    color_large = kwargs.get('color_large', 'b')
    title = kwargs.get('title', None)
    x_label = kwargs.get('x_label', col_x)
    y_label = kwargs.get('y_label', col_y)
    tooltip = kwargs.get('tooltip', None)
    series_id = kwargs.get('series_id', None)

    dataset_small = dataset_small.to_pandas()

    if color_small in dataset_small.columns:
        color_small = dataset_small[color_small]

    image = scatter_plot(dataset_large, col_x, col_y, x_range=x_range, y_range=y_range, noplot=True,
                         color=color_large,series_id=series_id)
    cropped_image = crop_margin(image)

    height, width, _ = cropped_image.shape
    cropped_image = PILImage.fromarray(cropped_image)

    image_bytes = io.BytesIO()
    cropped_image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()

    base64_image = base64.b64encode(image_bytes).decode('ascii')

    if tooltip is not None:
        dataset_small['hovertext'] = dataset_small[tooltip].apply(
            lambda x: '<br>'.join([f'{col}: {val}' for col, val in zip(x.index, x.dropna().values)]), axis=1)
        hover_text = dataset_small['hovertext']
    else:
        hover_text = None

    fig = subplots.make_subplots(specs=[[{"secondary_y": True}]])

    if isinstance(color_small, str):
        fig.add_trace(
            go.Scatter(
                x=dataset_small[col_x],
                y=dataset_small[col_y],
                mode='markers',
                marker=dict(color=color_small),
                hovertext=hover_text,
                hoverinfo='text'
            ),
            secondary_y=False
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=dataset_small[col_x],
                y=dataset_small[col_y],
                mode='markers',
                hovertext=hover_text,
                hoverinfo='text'
            ),
            secondary_y=False
        )

    fig.update_xaxes(range=x_range, showgrid=False, zeroline=False, showline=False)
    fig.update_yaxes(range=y_range, showgrid=False, zeroline=False, showline=False)

    # Calculate aspect ratio from the image
    aspect_ratio = height / width
    # Determine the figure's dimensions according to the aspect ratio
    fig_width = 600
    fig_height = int(fig_width * aspect_ratio)

    fig.update_layout(
        images=[
            go.layout.Image(
                source='data:image/png;base64,{}'.format(base64_image),
                xref="x",
                yref="y",
                x=x_range[0],
                y=y_range[1],
                sizex=x_range[1] - x_range[0],
                sizey=y_range[1] - y_range[0],
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        ],
        autosize=False,
        width=fig_width,
        height=fig_height,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,  # Adding y-axis label
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=0
        ),
        dragmode=False  # Disabling zoom
    )

    # Show the plot
    fig.show()


def plot_elbow(tddf, features, index_columns, nb_cluster_max=10, nb_cluster_min=2,
               operator_database=tdml.configure.val_install_location,
               indb_function='sqlmr', export_inertia=False, scaling=False, figsize=(16, 8), volatile=False):
    """
    Plot the elbow curve to find the optimal number of clusters for k-means clustering.

    Parameters:
    - tddf (DataFrame): Input data.
    - features (list): List of features to use for clustering.
    - index_columns (str or list): Column(s) to be used as index for clustering.
    - nb_cluster_max (int, default=10): Maximum number of clusters to test.
    - nb_cluster_min (int, default=2): Minimum number of clusters to test.
    - operator_database (str): Location for in-database operations.
    - indb_function (str, default='sqlmr'): Which in-database function to use ('sqlmr' or 'valib').
    - export_inertia (bool, default=False): Whether to return the inertia values or not.
    - scaling (bool, default=False): Whether to scale the features or not.
    - figsize (tuple, default=(16, 8)): Size of the plotted figure.

    Returns:
    - DataFrame: If export_inertia is True, returns a DataFrame with number of clusters, inertia, and distorsion. Otherwise, None.
    """

    # Convert index_columns to a list if it's a string.
    if type(index_columns) == str:
        index_colums = [index_columns]

    # Scale the data if scaling is True.
    if scaling:
        scaler = tdml.ScaleFit(
            data=tddf.dropna(),
            target_columns=features,
            scale_method="STD",
            global_scale=False
        )
        ADS = tdml.ScaleTransform(
            data=tddf,
            object=scaler.output,
            accumulate=index_colums)
        ADS = ADS.result
    else:
        ADS = tddf

    inertia_values_Vantage = []
    distorsion_values_Vantage = []
    num_clusters_range = range(nb_cluster_min, nb_cluster_max + 1)

    # Iterate through the range of cluster numbers and compute k-means clustering.
    for k in (pbar := tqdm(num_clusters_range)):
        pbar.set_description(f"Processing {k} clusters")

        if indb_function == 'sqlmr':

            kmeans_model = tdml.KMeans(
                data=ADS,
                target_columns=features,
                num_clusters=k,
                id_column=index_columns
            )

            kmeans_out = tdml.KMeansPredict(
                object=kmeans_model.result,
                data=ADS,
                output_distance=True,
                volatile=volatile
            ).result

            kmeans_out = kmeans_out.assign(sq_distance=kmeans_out.td_distance_kmeans * kmeans_out.td_distance_kmeans)

            kmeans_out_agg = kmeans_out.groupby('td_clusterid_kmeans').sum()  # sum_sq_distance
            kmeans_out_agg = kmeans_out_agg.mean()  # mean_sum_sq_distance
            inertia_values_Vantage.append(kmeans_out[index_colums + ['sq_distance']].sum()[
                                              ['sum_sq_distance']].to_pandas().sum_sq_distance.values[0])
            distorsion_values_Vantage.append(
                kmeans_out_agg[['mean_sum_sq_distance']].to_pandas().mean_sum_sq_distance.values[0])

        elif indb_function == 'valib':
            kmeans_model = valib.KMeans(
                data=ADS,
                columns=features,
                centers=k,
                operator_database=tdml.configure.val_install_location
            )

            kmeans_out = valib.KMeansPredict(
                data=ADS,
                model=kmeans_model.result,
                cluster_column="clusterid",
                index_columns=index_columns,
                fallback=False,
                accumulate=features,
                operator_database=tdml.configure.val_install_location
            )

            inertia, distorion = compute_cluster_inertia(kmeans_model, kmeans_out, features)
            inertia_values_Vantage.append(inertia)
            distorsion_values_Vantage.append(
                distorion)

    # Plot the computed inertia and distortion for each number of clusters.
    fig, ax = plt.subplots(1, 2, figsize=figsize)

    plt.subplot(1, 2, 1)
    plt.plot(num_clusters_range, inertia_values_Vantage, 'bo-')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    plt.title(f'Elbow Method for Optimal k ({indb_function})')

    plt.subplot(1, 2, 2)
    plt.plot(num_clusters_range, distorsion_values_Vantage, 'bo-')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Distorsion')
    plt.title(f'Elbow Method for Optimal k ({indb_function})')
    plt.show()

    # Return the inertia and distortion values if export_inertia is True.
    if export_inertia:
        return pd.DataFrame({'nb_clusters': list(num_clusters_range), 'inertia': inertia_values_Vantage, 'distorsion': distorsion_values_Vantage})
