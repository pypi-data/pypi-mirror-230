import calendar
import warnings

import matplotlib.pyplot as plt
import numpy as np
from prophet import Prophet
from prophet.plot import plot_components_plotly
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from statsmodels.tsa.stattools import acf, adfuller, kpss, pacf

from ..utility.resources import log_exception, logger


class timeSeriesVisualization():

    def __init__(self,df: pd.DataFrame, target: str, data: str, regione: str, use_case: str):

        """Class for time series visualization (plot and test)
        
        Parameters
        ----------
        df : pd.DataFrame
            dataset result of pre-process,containg timeline and target
        target : str
            name of target column
        data : str
            name of timeline column
        regione : str, optional
            name of level hierarchy, by default 
        use_case : str
            use case name
        """

        self.df = df
        self.target = target
        self.data = data
        self.regione = regione
        self.use_case = use_case

    def plotTimeSeries(self) -> tuple:
        
        """Plot and mirror plot of time series

        Parameters
        ----------

        Results
        -------
        tuple
            tuple that containing two figure for plot and mirror plot
        """

        # df = df.dropna()

        # Plot
        fig = px.line(
            self.df,
            x=self.data,
            y=self.target,
            labels={self.data: "data", self.target: f"{self.target}"},
            title=f"Andamento {self.use_case} - {self.regione}",
            color_discrete_sequence=["blue"],
            width=800,
            height=500,
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )

        # Plot (mirror)
        fig_mirror = px.area(
            self.df,
            x=self.data,
            y=self.target,
            labels={self.data: "data", self.target: f"{self.target}"},
            title=f"Andamento {self.use_case} - {self.regione} (mirror plot)",
            color_discrete_sequence=["green"],
            width=800,
            height=500,
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )

        fig_mirror.add_trace(
            go.Scatter(
                x=self.df[self.data],
                y=-self.df[self.target],
                marker=dict(color="green"),
                mode="lines",
                fill="tonexty",
                showlegend=False,
            )
        )

        # fig.show()
        # fig_mirror.show()

        return (fig, fig_mirror)

    def distribution_plot(self) -> plotly.graph_objs._figure.Figure:
        
        """Plot distribution of time series

        Parameters
        ----------

        Returns
        -------
        plotly.graph_objs._figure.Figure
            plot distribution
        """

        fig = px.histogram(
            self.df,
            self.target,
            title=f"Distribuzione di frequenza serie temporale <br> ({self.use_case}-{self.regione})",
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                    bargap=0.2,
                )
            ),
        )

        return fig

    def plot_day_month(self) -> tuple:
        
        """Plot time series aggregated by day and month

        Parameters
        ----------
        
        Returns
        -------
        tuple
            tuple that containing figure for day and month
        """

        time_series = self.df[self.target]
        time_series.index = self.df[self.data]

        # Casi per giorno della settimana
        tmp_abbr = pd.DataFrame.from_dict(
            {a: b for a, b in enumerate(calendar.day_abbr[:])},
            orient="index",
            columns=[self.data],
        )
        tmp_num = time_series.groupby(pd.to_datetime(time_series.index).dayofweek).sum()
        tmp = tmp_abbr.join(tmp_num, how="outer").fillna(0)

        # day = df.groupby(df[data].apply(lambda i: pd.to_datetime(i).dayofweek))[target].sum()
        # day.index = [i for i in calendar.day_abbr]
        # day = day.to_frame().reset_index()
        # day.columns = [data,target]

        fig_day = px.bar(
            tmp,
            x=self.data,
            y=self.target,
            labels={self.data: "Giorno della settimana", self.target: f"Richieste {self.use_case}"},
            title=f"Numero di richieste {self.use_case} per giorno della settimana - {self.regione}",
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )

        # Casi per mese
        tmp_abbr = pd.DataFrame.from_dict(
            {a + 1: b for a, b in enumerate(calendar.month_abbr[1:])},
            orient="index",
            columns=[self.data],
        )
        tmp_num = time_series.groupby(pd.to_datetime(time_series.index).month).sum()
        tmp = tmp_abbr.join(tmp_num, how="outer").fillna(0)

        # month = df.groupby(df[data].apply(lambda i: pd.to_datetime(i).month))[target].sum()
        # month.index = [i for i in calendar.month_abbr[1:]]
        # month = month.to_frame().reset_index()
        # month.columns = [data,target]

        fig_month = px.bar(
            tmp,
            x=self.data,
            y=self.target,
            labels={self.data: "Mese", self.target: f"Richieste {self.use_case}"},
            title=f"Numero di richieste {self.use_case} per mese - {self.regione}",
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )

        # fig_day.show()
        # fig_month.show()

        return (fig_day, fig_month)

    # Test stazionarietà (per individuare stagionalità)
    def stationarity(self) -> str:

        """test to verify stationarity

        Parameters
        ----------

        Returns
        -------
        str
            result of test
        """

        df = self.df.dropna()

        time_series = df[self.target]
        time_series.index = df[self.data]

        dftest = adfuller(time_series, autolag="AIC")
        dfoutput = pd.Series(dftest[0:3], index=["Test Statistic", "p-value", "#Lags Used"])
        DF = dfoutput["p-value"] < 0.05
        res = "Dickey-Fuller Test:\n"
        res += "Se p-value > 0.05: NON-stazionario\n"
        res += "Se p-value < 0.05: stazionario\n"
        res += f"p-value={dfoutput['p-value']}, Stazionario: {DF}\n\n"

        kpsstest = kpss(time_series, regression="ct", nlags="auto")
        kpss_output = pd.Series(
            kpsstest[0:3], index=["Test Statistic", "p-value", "#Lags Used"]
        )
        KPSS = kpss_output["p-value"] >= 0.05
        res += "KPSS Test:\n"
        res += "Se p-value > 0.05: stazionario\n"
        res += "Se p-value < 0.05: NON-stazionario\n"
        res += f"p-value={kpss_output['p-value']}, Stazionario: {KPSS}\n\n"

        if DF == KPSS:
            stazionarieta = DF
        elif DF == False:
            stazionarieta = "trend stazionario"
        else:
            stazionarieta = "differenza stazionaria"
        res += f"Risultato dei test: {stazionarieta}"

        return res

    # Autocorrelation
    def autocorrelation(self, n_lags: int = 50, detrend: bool = True) -> tuple:

        """Plot that show autocorrelation of time series

        Parameters
        ----------
        n_lags : int
            number of lags to compute autocorrelation
        detrend : bool
            whether to detrend the time series before computing the autocorrelation. Default is True

        Returns
        -------
        tuple
            tuple that containing figure for autocorrelation

        """

        if detrend:
            trend = self.additive_decomposition()[0]
            time_series = self.df[self.target] - trend
            title = "Autocorrelazione (detrendizzata)"
        else:
            time_series = self.df[self.target]
            title = "Autocorrelazione"

        autocorr = acf(time_series.dropna(), nlags=n_lags)[1:]
        fig1 = px.bar(
            x=np.arange(autocorr.shape[0]) + 1,
            y=autocorr,
            labels={"x": "Lag", "y": "Autocorrelazione"},
            title=title,
            template=dict(
                layout=go.Layout(
                    title_font=dict(family="Rockwell", size=24, color="red"),
                    font=dict(color="green"),
                )
            ),
        )
        fig1.update_layout(showlegend=False)

        return fig1

    # Decomposizione Additiva (Trend + Seasonality + Residual)
    def additive_decomposition(self) -> tuple:

        """Compute and plot additive decompostion

        Parameters
        ----------
        
        Returns
        -------
        tuple
            result of additive decomposition (trend and seasonality)
        """
        df = self.df.dropna()

        df = pd.DataFrame({'ds': df[self.data], 'y': df[self.target]})
        m = Prophet()
        m.fit(df)
        forecast = m.predict(df[["ds"]])

        fig = plot_components_plotly(m, forecast)

        forecast = forecast.set_index("ds")
        try:
            weekly = forecast["weekly"]
        except:
            weekly = None
        return (forecast["trend"], weekly, fig)

    def boxplots_seasons(self) -> plt.figure:
        
        """Creates a boxplot showing weekday-season effects

        Parameters
        ----------
        
        Returns
        -------
        plt.figure
            Pyplot figure in seaborn style
        """

        df_ = self.df.set_index(self.data).copy()
        df_ = df_.copy()
        df_["date"] = df_.index
        df_["weekday"] = df_["date"].dt.day_name()
        df_["month"] = df_["date"].dt.month
        df_["day"] = df_["date"].dt.day
        df_["date_offset"] = (df_.date.dt.month * 100 + df_.date.dt.day - 320) % 1300
        df_["season"] = pd.cut(
            df_["date_offset"],
            [0, 300, 602, 900, 1300],
            labels=["Spring", "Summer", "Fall", "Winter"],
        )
        df_plot = df_[["weekday", "season", self.target]]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(
            data=df_plot.dropna(), x="weekday", y=self.target, hue="season", ax=ax, linewidth=1
        )
        ax.set_title("Effetti settimanali-stagionali")
        ax.set_xlabel("Giorno della settimana")
        ax.set_ylabel(f"Numero {self.use_case}")
        ax.legend(bbox_to_anchor=(1, 1))
        return fig
    
    @log_exception(logger)
    def analyzingTimeSeries(self, aggregation_level: str) -> dict:
        
        """Perform an analysis of time series (plot,stationarity test,autocorrelation and additive decomposition)

        Parameters
        ----------

        Returns
        -------
            dict
            dict tath contain result of analysis (stationarity, trend and seasonality)
        """

        warnings.filterwarnings("ignore")

        visualizations = {}
        logger.info(message="START elaborate time series plot and time series mirror plot")
        plot = self.plotTimeSeries()
        visualizations["serie_temporale"] = [*plot]
        logger.info(message="DONE elaborate time series plot and time series mirror plot")

        logger.info(message="START distribution plot")
        distribution = self.distribution_plot()
        visualizations["serie_temporale"].append(distribution)
        logger.info(message="DONE distribution plot")

        if aggregation_level == "D":
            logger.info(message="START elaborate plot for day of week and for mount of year")
            plotDayMonth = self.plot_day_month()
            visualizations["aggregazioni"] = [*plotDayMonth]
            logger.info(message="DONE elaborate plot for day of week and for mount of year")

            logger.info(message="START weekly-seasonal plot")
            weekly_seasonal_effects = self.boxplots_seasons()
            visualizations["aggregazioni"].append(weekly_seasonal_effects)
            logger.info(message="DONE weekly-seasonal plot")

        if len(self.df) > 5:
            logger.info(message="START autocorrelation plot")
            autocorr = self.autocorrelation(n_lags=min(len(self.df.dropna()[self.target]) // 3 - 1, 365))
            visualizations["autocorrelazione"] = [autocorr]
            logger.info(message="DONE autocorrelation plot")

        try:
            logger.info(message="START stationarity test")
            stationar = self.stationarity()
            visualizations["test_stazionarietà"] = stationar
            logger.info(message="DONE stationarity test")
        except:
            pass

        try:
            logger.info(message="START additive decomposition")
            additive = self.additive_decomposition()
            visualizations["decomposizione_additiva"] = [additive[2]]
            logger.info(message="DONE additive decomposition")
            return {
                "trend": additive[0],
                "seasonality": additive[1],
                "visualizations": visualizations,
            }
        except:
            pass

        return {"visualizations": visualizations}
