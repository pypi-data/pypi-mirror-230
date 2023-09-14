import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .BaseValidator import BaseValidator


class WorksValidator(BaseValidator):
    def validate(
        self, model_dataset: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        model_dataset = model_dataset.drop_duplicates()
        df_stat = pd.DataFrame()
        dist_dict = dict()
        j = 0
        for c in act:
            for i in model_dataset.index:
                value = model_dataset.loc[i, c]
                if value != 0:
                    sample = df_wind_val.loc[df_wind_val[c] != 0]
                    if sample.shape[0] != 0:
                        q1, q99 = np.quantile(
                            sample[c].values, [self.lower_quantile, self.upper_quantile]
                        )
                        q1 = int(q1)
                        q99 = int(q99)
                        if value < q1 or value > q99:
                            df_stat.loc[j, "Работа"] = c
                            df_stat.loc[j, "Метка работы"] = "red"
                            key = c
                            line = value
                            color = "red"
                            counts, bins, _ = plt.hist(sample[c].values)
                            dist_dict[key] = {
                                "Line": line,
                                "color": color,
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                        else:
                            df_stat.loc[j, "Работа"] = c
                            df_stat.loc[j, "Метка работы"] = "green"
                            key = c
                            line = value
                            color = "green"
                            counts, bins, _ = plt.hist(sample[c].values)
                            dist_dict[key] = {
                                "Line": line,
                                "color": color,
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                        j += 1
                    else:
                        df_stat.loc[j, "Работа"] = c
                        df_stat.loc[j, "Метка работы"] = "grey"
        not_grey = df_stat.loc[df_stat["Метка работы"] != "grey"]
        not_perc = ((df_stat.shape[0] - not_grey.shape[0]) / df_stat.shape[0]) * 100
        norm_df = df_stat.loc[df_stat["Метка работы"] == "green"]
        norm_perc = ((not_grey.shape[0] - norm_df.shape[0]) / not_grey.shape[0]) * 100
        df_final_stat = pd.DataFrame()
        for i, c in enumerate(act):
            df_final_stat.loc[i, "Наименование"] = c
            sample = not_grey.loc[not_grey["Работа"] == c]
            count_dict = sample["Метка работы"].value_counts().to_dict()
            if "green" not in list(count_dict.keys()):
                df_final_stat.loc[i, "Среднедневная выработка"] = 0
            else:
                df_final_stat.loc[i, "Среднедневная выработка"] = (
                    count_dict["green"] / sample.shape[0]
                ) * 100
        return df_final_stat, dist_dict, norm_perc, not_perc
