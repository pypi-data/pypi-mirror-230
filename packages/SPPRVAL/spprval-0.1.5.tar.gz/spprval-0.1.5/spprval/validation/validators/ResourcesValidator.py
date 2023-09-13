import numpy as np
import pandas as pd

from .BaseValidator import BaseValidator


class ResourcesValidator(BaseValidator):
    def __init__(self, res: list):
        super().__init__()
        self.res = res

    def validate(
        self, model_dataset: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        model_dataset = model_dataset.drop_duplicates()
        act = [c + "_act_fact" for c in act]
        df_perc_agg = pd.DataFrame()
        df_style = pd.DataFrame()
        df_volume = pd.DataFrame()
        fig_dict = dict()
        for i in model_dataset.index:
            c_pair = [ci for ci in act if model_dataset.loc[i, ci] != 0]
            c_act = c_pair
            volume = [model_dataset.loc[i, ci] for ci in c_act]
            delta = [self.percent_delta * volume_i for volume_i in volume]
            not_c = [ci for ci in act if ci not in c_act]
            zero_ind = df_wind_val[not_c][(df_wind_val[not_c] == 0).all(axis=1)].index
            sample_non = df_wind_val.loc[zero_ind, :]

            non_zero = sample_non[c_act][(sample_non[c_act] != 0).all(axis=1)].index
            sample_non = pd.DataFrame(sample_non.loc[non_zero, :])
            sample = pd.DataFrame()
            for j, ci in enumerate(c_act):
                sample = sample_non.loc[
                    (sample_non[ci] >= volume[j] - delta[j])
                    & (sample_non[ci] <= volume[j] + delta[j])
                ]
            sample = pd.DataFrame(sample)

            if sample.shape[0] > 4:
                for r in self.res:
                    value = model_dataset.loc[i, r]
                    q1, q99 = np.quantile(
                        sample[r].values, [self.lower_quantile, self.upper_quantile]
                    )
                    if value < q1 or value > q99:
                        df_style.loc[i, r] = "red"
                        df_volume.loc[i, r] = value
                        for ci in c_act:
                            key, blue_points, black_points, star = self._process_key(
                                c_act, r, ci, sample, sample_non, model_dataset, i
                            )

                            color = "red"
                            fig_dict[key] = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                            }
                    else:
                        df_style.loc[i, r] = "green"
                        df_volume.loc[i, r] = value
                        for ci in c_act:
                            key, blue_points, black_points, star = self._process_key(
                                c_act, r, ci, sample, sample_non, model_dataset, i
                            )

                            color = "green"
                            fig_dict[key] = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                            }
                df_style.loc[i, "Наименование"] = str(c_act)
                df_volume.loc[i, "Наименование"] = str(c_act)
            elif sample.shape[0] <= 4:
                df_style.loc[i, "Наименование"] = str(c_act)
                df_volume.loc[i, "Наименование"] = str(c_act)
                for r in self.res:
                    value = model_dataset.loc[i, r]
                    df_style.loc[i, r] = "grey"
                    df_volume.loc[i, r] = value
        new_df_color = df_style[(df_style != "grey").all(1)]
        not_perc = (
            (
                (df_style.shape[0] * df_style.shape[1])
                - (new_df_color.shape[0] * new_df_color.shape[1])
            )
            / (df_style.shape[0] * df_style.shape[1])
        ) * 100
        j = 0

        for c in act:
            new_sample = new_df_color.loc[
                new_df_color["Наименование"].str.count(c) != 0
            ]
            if new_sample.shape[0] != 0:
                for r in self.res:
                    df_perc_agg.loc[j, "Наименование ресурса"] = r
                    df_perc_agg.loc[j, "Наименование работы"] = c
                    value_dict = new_sample[r].value_counts().to_dict()
                    if "green" in list(value_dict.keys()):
                        df_perc_agg.loc[j, "Соотношение"] = round(
                            ((value_dict["green"]) / new_sample.shape[0]) * 100
                        )
                    else:
                        df_perc_agg.loc[j, "Соотношение"] = 0
                    j += 1
            else:
                for r in self.res:
                    df_perc_agg.loc[j, "Наименование ресурса"] = r
                    df_perc_agg.loc[j, "Наименование работы"] = c
                    df_perc_agg.loc[j, "Соотношение"] = 0
                    j += 1

        norm_perc = df_perc_agg["Соотношение"].mean()
        df_final_volume = pd.DataFrame()
        df_final_style = pd.DataFrame()
        for i, p in enumerate(list(df_volume["Наименование"].unique())):
            sample1 = df_volume.loc[df_volume["Наименование"] == p]
            sample2 = df_style.loc[df_style["Наименование"] == p]
            date = str(sample1.index[0]) + " " + str(sample1.index[-1])
            df_final_volume.loc[i, "Наименование"] = p
            df_final_volume.loc[i, "Даты"] = date
            df_final_volume.loc[i, self.res] = sample1.loc[sample1.index[0], self.res]
            df_final_style.loc[i, "Наименование"] = p
            df_final_style.loc[i, "Даты"] = date
            df_final_style.loc[i, self.res] = sample2.loc[sample2.index[0], self.res]

        return (
            df_perc_agg,
            df_final_volume,
            df_final_style,
            fig_dict,
            not_perc,
            norm_perc,
        )

    @staticmethod
    def _process_key(c_act, r, ci, sample, sample_non, model_dataset, i):
        key = str(c_act) + " " + r + " " + ci
        blue_points = {
            "x": list(sample_non[ci].values),
            "y": list(sample_non[r].values),
        }
        black_points = {
            "x": list(sample[ci].values),
            "y": list(sample[r].values),
        }
        star = {
            "x": model_dataset.loc[i, ci],
            "y": model_dataset.loc[i, r],
        }
        return key, blue_points, black_points, star
