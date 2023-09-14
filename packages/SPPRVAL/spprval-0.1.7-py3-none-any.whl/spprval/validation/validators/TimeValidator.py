import numpy as np
import pandas as pd

from .BaseValidator import BaseValidator


class TimeValidator(BaseValidator):
    def validate(
        self, df_wind_model: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        df_wind_model = df_wind_model.drop_duplicates()
        df_stat = pd.DataFrame()
        dict_fig = {}
        final_df = pd.DataFrame()
        j = 0
        for c in act:
            dict_fig[c] = []
            for i in df_wind_model.index:
                if df_wind_model.loc[i, c] != 0:
                    c_act = [c]
                    volume = [df_wind_model.loc[i, ci] for ci in c_act]
                    delta = [self.percent_delta * volume_i for volume_i in volume]
                    sample = df_wind_val.copy()
                    for k, ci in enumerate(c_act):
                        sample = sample.loc[
                            (sample[ci] >= volume[k] - delta[k])
                            & (sample[ci] <= volume[k] + delta[k])
                        ]
                    if sample.shape[0] > 3:
                        df_stat, dict_for_sample = self.handle_sample(
                            i,
                            c,
                            df_wind_model,
                            sample,
                            df_wind_val,
                            df_stat,
                            j,
                        )
                        dict_fig[c].append(
                            {
                                "volume": volume,
                                "fig_data": dict_for_sample,
                                "color": dict_for_sample["Color"],
                            }
                        )
                    else:
                        df_stat.loc[j, "Работа"] = c
                        df_stat.loc[j, "Метка времени"] = "grey"
                    j += 1

        not_grey = df_stat.loc[df_stat["Метка времени"] != "grey"]
        not_perc = ((df_stat.shape[0] - not_grey.shape[0]) / df_stat.shape[0]) * 100
        norm_df = df_stat.loc[df_stat["Метка времени"] == "green"]
        norm_perc = 0
        if not_perc != 100:
            norm_perc = (
                (not_grey.shape[0] - norm_df.shape[0]) / not_grey.shape[0]
            ) * 100

        final_df = self.finalize_dataframe(act, final_df, not_grey)
        return final_df, dict_fig, norm_perc, not_perc

    def handle_sample(self, i, c, df_wind_model, sample, df_wind_val, df_stat, j):
        value = df_wind_model.loc[i, c.split("_act_fact")[0] + "_real_time_act"]
        q1, q99 = np.quantile(
            sample[c.split("_act_fact")[0] + "_real_time_act"].values,
            [self.lower_quantile, self.upper_quantile],
        )
        q1 = int(q1)
        q99 = int(q99)
        if value < q1 or value > q99:
            color = "red"
        else:
            color = "green"
        df_stat.loc[j, "Работа"] = c
        df_stat.loc[j, "Метка времени"] = color
        sample_dict = self.create_figure_dict(
            c, color, sample, df_wind_val, df_wind_model, i, q1, q99
        )
        return df_stat, sample_dict

    @staticmethod
    def create_figure_dict(
        c,
        color,
        sample,
        df_wind_val: pd.DataFrame,
        df_wind_model: pd.DataFrame,
        i,
        q1,
        q99,
    ):
        blue_points = {
            "x": list(df_wind_val[c].values),
            "y": list(df_wind_val[c.split("_act_fact")[0] + "_real_time_act"].values),
        }
        black_points = {
            "x": list(sample[c].values),
            "y": list(sample[c.split("_act_fact")[0] + "_real_time_act"].values),
        }
        star = {
            "x": df_wind_model.loc[i, c],
            "y": df_wind_model.loc[i, c.split("_act_fact")[0] + "_real_time_act"],
        }
        return {
            "Blue points": blue_points,
            "Black points": black_points,
            "Star": star,
            "Color": color,
            "Q1": q1,
            "Q99": q99,
        }

    @staticmethod
    def finalize_dataframe(act: list, final_df, not_grey):
        for i, c in enumerate(act):
            final_df.loc[i, "Наименование"] = c
            sample = not_grey.loc[not_grey["Работа"] == c]
            count_dict = sample["Метка времени"].value_counts().to_dict()
            if "green" not in list(count_dict.keys()):
                final_df.loc[i, "Время на ед. объёма"] = 0
            else:
                final_df.loc[i, "Время на ед. объёма"] = (
                    count_dict["green"] / sample.shape[0]
                ) * 100
        return final_df
