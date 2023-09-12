from __future__ import annotations

import re

import numpy as np
import pandas as pd
import geopandas as gpd

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

import matplotlib.pyplot as plt
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis

import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import plotly.graph_objects as go

from typing_extensions import Self

from ..utility.resources import log_exception, logger

from ..utility.constants import code_to_region_name


class DataVisualization:

    def __init__(
        self,
        use_case: str,
        df: pd.DataFrame,
        target: str = "volumes"
    ) -> Self:
        
        """Initializing the DataVisualization class.
            A class for the visualization of general situation descript by dataframe (the class consider all value,
            for each aggregation level).

        Parameters
        ----------
        use_case : str
            specify the name of use case (necessary for the plot title)
        df : pd.DataFrame
            the original dataset
        target : str
            the name of column target, by default "volumes"
        dict_reg : dict
            a dictionary that convert codice_regione to name , by default None
        """

        self.use_case = use_case
        self.dict_regioni = code_to_region_name
        self.df = df
        self.target = target

        self.df[target] = 1

        if re.match("teleconsult[i,o]",use_case,re.IGNORECASE):
            self.df = self.df.drop_duplicates(subset=["id_prenotazione"])

    @log_exception(logger)
    def conteggi(
        self,
        level1: str,
        level2: str = None,
        level3: str = None,
        freq: str = None,
    ) -> pd.Series:
        
        """Compute the aggregation by specify level

        Parameters
        ----------
        target : str
            name of target column
        level1 : str
            name of first level aggregation
        level2 : str
            name of second level aggregation, by default None
        level3: str
            name of third level aggregation, by default None

        Returns
        -------
        pd.Series
            Series of aggregation count

        Raises
        ------
        Exception
            _description_
        """

        # try:
        #     pd.Period(data_inizio)
        #     pd.Period(data_fine)
        # except:
        #     raise Exception("La data non è valida")

        livelli = list(filter(None, [level1, level2, level3]))
        livelli1 = [
            pd.Grouper(key=i, freq=freq) if self.df[i].dtype == "<M8[ns]" else i
            for i in livelli
        ]
        regioni = list(self.dict_regioni.values())

        logger.info(message="START elaborate counting dataframe")

        # select DATA
        # i = " 23:59:59"
        # tab = self.df.query(f"({data} >= '{data_inizio}') & ({data} <= '{data_fine + i}')")

        # aggregazione per livelli specificati
        ris = (
            self.df.groupby(livelli1, as_index=False)[self.target]
            .sum()
            .sort_values([self.target], ascending=0)
            .set_index(livelli)
        )

        # regioni mancanti
        if self.df[level1].unique()[0] in regioni:
            regioniMancanti = np.setdiff1d(
                regioni, ris.index.get_level_values(0).unique()
            )
            if len(livelli) > 1:
                regioniMancanti = [(i, "null") for i in regioniMancanti]
        else:
            regioniMancanti = []

        zero = pd.Series(np.nan, index=regioniMancanti)

        if ris.shape[0] > 1:
            ris = pd.concat([ris.squeeze(), zero])
        else:
            ris = pd.concat([ris, zero])[self.target]

        ris = ris.to_frame()

        # indici e colonne
        if len(livelli) > 1:
            ris.index = pd.MultiIndex.from_tuples(ris.index, names=(i for i in livelli))

        ris.reset_index(inplace=True)
        ris.columns = livelli + [self.target]

        #self.cont = ris

        logger.info(message="DONE elaborate counting dataframe")

        return ris

    def plot(
        self,
        df: pd.DataFrame,
        level1: str,
        level2: str = None,
        level3: str = None,
    ) -> plotly.graph_objs._figure.Figure:
        
        """Sunburst plot of aggregate data

        Parameters
        ----------
        df : pd.DataFrame
            dataframe of aggregate data (result of conteggi function)
        target : str
            name of target column (count column)
        level1 : str
            name of first level aggregation
        level2 : str, optional
            name of second level aggregation, by default None
        level3 : str, optional
            name of third level aggregation, by default None

        Returns
        -------
        plotly.graph_objs._figure.Figure
            sunburst plot
        """

        livelli = [level1, level2, level3]
        levels = list(filter(None, livelli))
        name_levels = " e ".join(levels).replace("_", " ").title()

        fig = px.sunburst(
            df,
            path=levels,
            values=self.target,
            width=600,
            height=600,
            title=f"Numero di {self.use_case} per {name_levels}",
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )
        fig.update_traces(textinfo="label+percent parent")

        return fig

    def boxplot(self, df: pd.DataFrame, variable: str):
        
        """Boxplot of aggregated data

        Parameters
        ----------
        df : pd.DataFrame
            dataframe of aggregate data (result of conteggi function)
        variable : str
            name of variable on x axis 

        Results
        -------
        plotly.graph_objs._figure.Figure
            boxplot
        """

        fig = px.box(
            df,
            x=variable,
            y=self.target,
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )

        return fig

    def DTW(self, df: pd.DataFrame, column: str, data: str, val1: str, val2: str) -> tuple:

        """compute distance between two time series

        Parameters
        ----------
        df : pd.DataFrame
            dataframe result of conteggi function
        column : str
            name of one column aggregate on
        data : str
            name of data column
        val1: str
            name of column modality
        val2 : str
            name of column modality

        Returns
        -------
        tuple
            tuple containing a figure that representing distance between time series and the value of distance

        """

        df_sort = df.sort_values(data)
        x = df_sort[df_sort[column] == val1][self.target].values
        y = df_sort[df_sort[column] == val2][self.target].values       

        # Normalize time series
        x = x / x.max()
        y = y / y.max()

        distance = dtw.distance_fast(x, y, use_pruning=True)
        path = dtw.warping_path(x, y)

        fig, ax = plt.subplots(2, 1, figsize=(20, 9))
        dtwvis.plot_warping(x, y, path, fig=fig, axs=ax)

        ax[0].set_title(
            f"Dynamic Time Warping, {column} ({val1}-{val2})",
            fontsize=20,
            y=1.1,
            color="gray",
            loc="left",
            family="serif",
        )
        ax[1].set_xlabel("time", fontsize=12)
        ax[0].set_ylabel(self.target, fontsize=12)
        ax[1].set_ylabel(self.target, fontsize=12)
        fig.tight_layout()

        normalized_distance = distance / np.sqrt(len(x) * len(y))

        return (fig, normalized_distance)
    
    def DTW_distance_matrix(self, df: pd.DataFrame, column: str, data: str) -> tuple:

        """computes DTW distance matrix of all sub time series of a column

        Parameters
        ----------
        df : pd.DataFrame
            dataframe result of conteggi function
        column : str
            name of one column aggregate on
        data : str
            name of data column

        Returns
        -------
        tuple
            tuple containing the matrix and the plot of matrix
        """

        df_sort = df.sort_values(data)

        lista = [(df_sort[df_sort[column] == i][self.target].values.astype(np.double),i)
         for i in df_sort[column].unique()]

        lista_time_series = [i[0]/i[0].max() for i in lista]
        len_time_series = np.array([len(i[0]) for i in lista])
        len_matrix_time_series = np.sqrt(np.einsum("i, j -> ij", len_time_series, len_time_series))
        distance_matrix = dtw.distance_matrix_fast(lista_time_series)
        
        distance_matrix_normalized = distance_matrix / len_matrix_time_series

        fig = px.imshow(distance_matrix_normalized, text_auto=True, template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="grey"),
                    font=dict(color="green"),
                width=800,
                height=700,
                title=f"Distance matrix ({column})",
                )))

        fig.update_layout(
            xaxis = dict(
                tickmode = 'array',
                tickvals = [i for i in range(len(lista))],
                ticktext = [i[1] for i in lista],tickfont=dict(family='Rockwell', color='green', size=10)
            ),
            yaxis = dict(
                tickmode = 'array',
                tickvals = [i for i in range(len(lista))],
                ticktext = [i[1] for i in lista],tickangle=-45,tickfont=dict(family='Rockwell', color='green', size=10)
            )           
        )

        return (fig,distance_matrix_normalized,lista)

    def plot_distance_matrix(self, distance_matrix: np.ndarray, lista: list[tuple]):
        
        dists = squareform(distance_matrix)
        linkage_matrix = linkage(dists, "ward",optimal_ordering=0)
        
        dendr = plt.figure(figsize=(10,6))
        dendrogram(linkage_matrix, labels=[i[1] for i in lista],leaf_rotation=0,orientation="right")
        plt.title("DTW distance - dendrogramm")
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)
        
        return dendr

    def add_geographical_info(
        self, target: str, region: str, df_geo: gpd.GeoDataFrame, region_geo: str
    ) -> gpd.GeoDataFrame:
        
        """Aggregates df on "spatial_variable" and joins with the "regions" geodataframe on "join_variable"

        Parameters
        ----------
        target : str
            name of target column
        region : str
            name of region column
        df_geo : gpd.GeoDataFrame
            GeoDataFrame containing geometry for Italian region
        region_geo : str
            name of region column
        data : str
            name of data column
        data_inizio : str
            initial data to select
        data_fine : str
            final data to select

        Returns
        -------
        gpd.GeoDataFrame
            geodataframe containing geographical information and the aggregated "spatial_variable"
        """

        df_aggreg = self.conteggi(region)
        df_aggreg.set_index(region, inplace=True)
        df_aggreg = df_aggreg.reindex(df_geo[region_geo])

        df_geo[target] = df_aggreg.values

        return df_geo

    def plot_geo(
        self,
        df: gpd.GeoDataFrame,
        target: str,
        region_geo: str,
        confronto: str = None,
        express: str = None,
        title: str = "",
    ) -> plotly.graph_objs._figure.Figure:
        
        """Territorial plot of aggregated data for region

        Parameters
        ----------
        df : gpd.GeoDataFrame
            dataframe with gegographical info join with result of conteggi function
        target : str
            name of target column
        region_geo : str
            name of column with geographical info
        confronto : str 
            name of column with comparision value with target column (for example number of population),by default None
        express : str 
            expression that describe relationship between confronto column and target column
        title : str 
            title for the plot

        Results
        -------
        plotly.graph_objs._figure.Figure
            geographical plot
        """

        def generateColorScale(colors, naColor):
            colorArray = []
            colorArray.append([0, naColor])
            for grenze, color in zip(np.linspace(0.03, 1, len(colors)), colors):
                colorArray.append([grenze, color])
            return colorArray

        df = df.set_index(region_geo)
        df = df.fillna(0)

        target_name = target
        confronto_name = confronto

        if confronto:
            target = df[target_name]
            confronto = df[confronto_name]
            df[target_name] = eval(express).values

        fig = px.choropleth(
            df,
            geojson=df["geometry"],
            locations=df.index,
            color=target_name,
            projection="mercator",
            title=title,
            width=700,
            height=700,
            color_continuous_scale=generateColorScale(
                colors=["blue", "red"], naColor="grey"
            ),
        )
        fig.update_geos(fitbounds="locations", visible=False)

        return fig
