import datetime
import json
from copy import copy
from os import listdir
from os.path import isfile, join

import pandas as pd
import pkg_resources

from spprval.database.DBWrapper import DBWrapper
from spprval.dataset.KSGDataset import KSGDataset
from spprval.dataset.PlanDataset import PlanDataset
from spprval.dataset.ValidationDataset import ValidationDataset
from .aggregator import Aggregator
from .expert_metrics_estimator import ExpertMetricsEstimator
from .stats_calculator import StatisticCalculator
from .validators.ResourcesValidator import ResourcesValidator
from .validators.TimeValidator import TimeValidator
from .validators.WorksValidator import WorksValidator

brave_precalculated = "tables/precalculated_brave_coefficients.csv"
links_history = "tables/links_history_messoyaha_with_granular_smr_v4.csv"
brave_path = pkg_resources.resource_filename(__name__, brave_precalculated)
links_history_path = pkg_resources.resource_filename(__name__, links_history)


class PlanValidator:
    def __init__(self, plan, url):
        self.ksg_data = KSGDataset(ksg_data=plan).collect()
        self.plan_dataset = PlanDataset(ksg_data=self.ksg_data)
        self.data_source = DBWrapper(url=url)
        self.aggregator = Aggregator()
        self.works_validator = WorksValidator()
        self.time_validator = TimeValidator()
        self.resources_validator = None
        self.statistic_calculator = None

    def validate(self):
        plan_df = self.plan_dataset.collect()
        act = self.plan_dataset.get_act_names()
        res = self.plan_dataset.get_res_names()

        brave = pd.read_csv(brave_path, index_col=0)

        pools = self.plan_dataset.get_pools()

        validation_df = ValidationDataset(self.data_source, pools, act, res).collect()

        print("Валидируем ресурсы")
        self.resources_validator = ResourcesValidator(
            res=[r + "_res_fact" for r in res]
        )
        (
            df_perc_agg_res,
            df_final_volume_res,
            df_final_style_res,
            fig_dict_res,
            not_perc_res,
            norm_perc_res,
        ) = self.resources_validator.validate(plan_df, validation_df, act)
        print("Валидация ресурсов по ведомости")
        df_vedom, not_perc_vedom, norm_perc_vedom = self.aggregator.get_res_ved_stat(
            brave, self.ksg_data
        )
        print("Нарезка данных на окна")
        _, df_wind_val = self.window_zero(validation_df)
        _, df_wind_model = self.window_zero(plan_df)
        for i in df_wind_val.index:
            for c in act:
                df_wind_val.loc[i, c.split("_")[0] + "_real_time_act"] = (
                    df_wind_val.loc[i, "Window length"]
                    - df_wind_val.loc[i, c.split("_")[0] + "_act_fact_zero_lil"]
                    - df_wind_val.loc[i, c.split("_")[0] + "_act_fact_zero_big"]
                )
        for i in df_wind_model.index:
            for c in act:
                df_wind_model.loc[i, c.split("_")[0] + "_real_time_act"] = (
                    df_wind_model.loc[i, "Window length"]
                    - df_wind_model.loc[i, c.split("_")[0] + "_act_fact_zero_lil"]
                    - df_wind_model.loc[i, c.split("_")[0] + "_act_fact_zero_big"]
                )

        print("Валидация среднедневных объёмов работ")
        (
            df_volume_stat,
            dist_dict,
            norm_volume_perc,
            not_volume_perc,
        ) = self.works_validator.validate(
            plan_df, validation_df, act=[c + "_act_fact" for c in act]
        )
        print("Валидация времени")
        (
            df_time_stat,
            time_plot_dict,
            norm_time_perc,
            not_time_perc,
        ) = self.time_validator.validate(
            df_wind_model, df_wind_val, act=[c + "_act_fact" for c in act]
        )
        print("Валидация последовательностей")
        seq_history = pd.read_csv(links_history_path)
        (
            df_seq_stat,
            df_color_seq,
            norm_perc_seq,
            not_perc_seq,
        ) = self.aggregator.get_all_seq_statistic(seq_history, self.ksg_data)
        print("Получение общих статистик по работам и ресурсам")
        self.statistic_calculator = StatisticCalculator(
            norm_perc_res,
            norm_perc_vedom,
            norm_volume_perc,
            norm_time_perc,
            norm_perc_seq,
            not_perc_res,
            not_perc_vedom,
            not_volume_perc,
            not_time_perc,
            not_perc_seq,
        )
        work_res_common_perc = (
            self.statistic_calculator.get_statistic_for_properties_and_all_stat()
        )
        plan_statistic = self.statistic_calculator.get_plan_statistic()

        return (
            df_perc_agg_res,
            df_final_volume_res,
            df_final_style_res,
            fig_dict_res,
            df_vedom,
            df_volume_stat,
            dist_dict,
            df_time_stat,
            time_plot_dict,
            df_seq_stat,
            df_color_seq,
            work_res_common_perc,
            plan_statistic,
        )

    @staticmethod
    def window_zero(df: pd.DataFrame, min_window: int = 2, max_window: int = 10):
        df = df.drop_duplicates()
        base = datetime.datetime.today()
        date_list = [
            (base + datetime.timedelta(days=x)).strftime("%d.%m.%Y")
            for x in range(df.shape[0])
        ]
        df.index = date_list
        """Function for making time windows of msg files

        Args:
            df (pd.DataFrame): input msg file
            min_window (int, optional): Min length of window. Defaults to 5.
            max_window (int, optional): Max length of window. Defaults to 31.

        Returns:
            DataFrame: msg files with windows
        """
        act_col = [var for var in df.columns if "_act_fact" in var]

        res_col = [var for var in df.columns if "_res_fact" in var]
        new_zero_lil = [act + "_zero_lil" for act in act_col]
        new_zero_big = [act + "_zero_big" for act in act_col]
        df_new = pd.DataFrame(
            columns=list(df.columns)
            + ["Start day", "Window length"]
            + new_zero_lil
            + new_zero_big
        )
        df_zero = pd.DataFrame(columns=act_col)
        for window_len in [7]:
            for start in range(0, len(df) - window_len + 1):
                new_row = (
                    df[act_col]
                    .iloc[start : start + window_len]
                    .sum(axis=0, skipna=True)
                )
                new_row = {
                    act: 1 if value == 0.0 else 0 for act, value in new_row.items()
                }
                start_day = datetime.datetime.strptime(df.index[start], "%d.%m.%Y")
                end_day = datetime.datetime.strptime(
                    df.index[start + window_len - 1], "%d.%m.%Y"
                )
                df_zero.loc[df.index[start]] = new_row

        window_list = list(range(min_window, max_window + 1))
        for window_len in window_list:
            for start in range(0, len(df) - window_len + 1):
                start_day = datetime.datetime.strptime(df.index[start], "%d.%m.%Y")
                end_day = datetime.datetime.strptime(
                    df.index[start + window_len - 1], "%d.%m.%Y"
                )
                if (end_day - start_day).days == window_len - 1:
                    new_row_act = (
                        df[act_col]
                        .iloc[start : start + window_len]
                        .sum(axis=0, skipna=True)
                    )
                    new_row_res = (
                        df[res_col]
                        .iloc[start : start + window_len]
                        .mean(axis=0, skipna=True)
                    )
                    new_row = copy(new_row_act)
                    new_row = pd.concat([new_row, new_row_res])

                    lil = {act + "_zero_lil": 0 for act in act_col}
                    big = {act + "_zero_big": 0 for act in act_col}
                    danger_date = [
                        df.index[ind] for ind in range(start, start + window_len)
                    ]

                    for act in act_col:
                        for i in range(start, start + window_len):
                            if df.iloc[i][act] == 0.0:
                                lil[act + "_zero_lil"] = lil[act + "_zero_lil"] + 1
                                if (
                                    (i < window_len - 6)
                                    and danger_date[i - start] in df_zero.index
                                    and df_zero.loc[danger_date[i - start]][act] == 1
                                ):
                                    if (i > start) and (
                                        df_zero.loc[danger_date[i - start - 1]][act]
                                        == 1
                                    ):
                                        big[act + "_zero_big"] = (
                                            big[act + "_zero_big"] + 1
                                        )
                                    else:
                                        big[act + "_zero_big"] = (
                                            big[act + "_zero_big"] + 7
                                        )
                    lil = {
                        act
                        + "_zero_lil": lil[act + "_zero_lil"]
                        - big[act + "_zero_big"]
                        for act in act_col
                    }

                    new_row = {
                        **new_row,
                        **lil,
                        **big,
                        "Start day": start_day,
                        "Window length": window_len,
                    }
                    df_new = pd.concat(
                        [df_new, pd.DataFrame(pd.Series(new_row)).transpose()],
                        ignore_index=True,
                    )

        return df_zero, df_new

    @staticmethod
    def _file_opener(mypath, validation_files, act):
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        for file in onlyfiles:
            msg_file = open(mypath + file, encoding="utf8")
            msg_data = json.load(msg_file)
            if len(msg_data["resource"]) != 0:
                for work in msg_data["work"]:
                    if work["work title"] in act:
                        validation_files.append(mypath + file)
                        break
        return validation_files

    @staticmethod
    def _save_json_file(label, json_file, new_plan_path):
        with open(new_plan_path + str(label) + ".json", "w") as outfile:
            json.dump(json_file, outfile)
        return new_plan_path + str(label) + ".json"


class ProjectValidation:
    def __init__(self, project_ksg, url):
        self.project_ksg = project_ksg
        self.url = url

    def validate_plan(self):
        result_dict = dict()
        ksg_for_val_data = self.project_ksg
        regime = True
        for el in ksg_for_val_data["activities"]:
            if (
                el["activity_name"] == "Окончание работ по марке"
                or el["activity_name"] == "Начало работ по марке"
            ):
                regime = False
                break
        if regime:
            (
                df_perc_agg_res,
                df_final_volume_res,
                df_final_style_res,
                fig_dict_res,
                df_vedom,
                df_volume_stat,
                dist_dict,
                df_time_stat,
                time_plot_dict,
                df_seq_stat,
                df_color_seq,
                work_res_common_perc,
                plan_statistic,
            ) = PlanValidator(plan=self.project_ksg, url=self.url).validate()
            result_dict["Object 0"] = {
                "Отношения ресурсов к работам": df_perc_agg_res,
                "Пулы работ объёмы": df_final_volume_res,
                "Пулы работ цвета": df_final_style_res,
                "Данные для графиков ресурсов": fig_dict_res,
                "Ресурсная ведомость": df_vedom,
                "Статистика по выработке": df_volume_stat,
                "Данные для графиков выработок": dist_dict,
                "Статистика по времени работ": df_time_stat,
                "Данные для графиков времени": time_plot_dict,
                "Таблица связей": df_seq_stat,
                "Таблица связей цвета": df_color_seq,
                "Статистика итоговая по работам и ресурсам": work_res_common_perc,
                "Итоговая статистика плана": plan_statistic,
            }
        else:
            json_files = []
            act_dict = dict()
            block_id = dict()
            ind_act = dict()
            label = 0
            for i, el in enumerate(ksg_for_val_data["activities"]):
                act_dict[el["activity_id"]] = el["activity_name"]
                if el["activity_name"] == "Окончание работ по марке":
                    label += 1
                elif el["activity_name"] == "Начало работ по марке":
                    label += 1
                else:
                    block_id[el["activity_id"]] = label
                    ind_act[el["activity_id"]] = i
            block_id["0000000"] = label + 1
            json_file = {"activities": []}
            label = block_id[list(block_id.keys())[0]]
            for k in block_id.keys():
                if block_id[k] == label:
                    ind_of_act = ind_act[k]
                    new_des_act = []
                    for el in ksg_for_val_data["activities"][ind_of_act][
                        "descendant_activities"
                    ]:
                        if el[0] in block_id.keys():
                            if (
                                act_dict[el[0]] != "Окончание работ по марке"
                                and act_dict[el[0]] != "Начало работ по марке"
                            ):
                                if block_id[k] == block_id[el[0]]:
                                    new_des_act.append(el)
                    ksg_for_val_data["activities"][ind_of_act][
                        "descendant_activities"
                    ] = new_des_act
                    json_file["activities"].append(
                        ksg_for_val_data["activities"][ind_of_act]
                    )
                    label = block_id[k]
                else:
                    json_files.append(json_file)
                    if k == "0000000":
                        break
                    else:
                        json_file = {"activities": []}
                        ind_of_act = ind_act[k]
                        new_des_act = []
                        for el in ksg_for_val_data["activities"][ind_of_act][
                            "descendant_activities"
                        ]:
                            if el[0] in block_id.keys():
                                if (
                                    act_dict[el[0]] != "Окончание работ по марке"
                                    and act_dict[el[0]] != "Начало работ по марке"
                                ):
                                    if block_id[k] == block_id[el[0]]:
                                        new_des_act.append(el)
                        ksg_for_val_data["activities"][ind_of_act][
                            "descendant_activities"
                        ] = new_des_act
                        json_file["activities"].append(
                            ksg_for_val_data["activities"][ind_of_act]
                        )
                        label = block_id[k]
            for id_number, p in enumerate(json_files):
                (
                    df_perc_agg_res,
                    df_final_volume_res,
                    df_final_style_res,
                    fig_dict_res,
                    df_vedom,
                    df_volume_stat,
                    dist_dict,
                    df_time_stat,
                    time_plot_dict,
                    df_seq_stat,
                    df_color_seq,
                    work_res_common_perc,
                    plan_statistic,
                ) = PlanValidator(plan=p, url=self.url).validate()
                result_dict["Object " + str(id_number)] = {
                    "Отношения ресурсов к работам": df_perc_agg_res,
                    "Пулы работ объёмы": df_final_volume_res,
                    "Пулы работ цвета": df_final_style_res,
                    "Данные для графиков ресурсов": fig_dict_res,
                    "Ресурсная ведомость": df_vedom,
                    "Статистика по выработке": df_volume_stat,
                    "Данные для графиков выработок": dist_dict,
                    "Статистика по времени работ": df_time_stat,
                    "Данные для графиков времени": time_plot_dict,
                    "Таблица связей": df_seq_stat,
                    "Таблица связей цвета": df_color_seq,
                    "Статистика итоговая по работам и ресурсам": work_res_common_perc,
                    "Итоговая статистика плана": plan_statistic,
                }
        return result_dict

    def calculate_expert_metrics(self):
        metrics_calculator = ExpertMetricsEstimator(self.project_ksg)
        metrics = metrics_calculator.calculate_metrics()
        return metrics

    @staticmethod
    def _filter_activities(k, block_id, act_dict, ksg_for_val_data, ind_act):
        ind_of_act = ind_act[k]
        new_des_act = []
        for el in ksg_for_val_data["activities"][ind_of_act]["descendant_activities"]:
            if el[0] in block_id.keys():
                if act_dict[el[0]] not in [
                    "Окончание работ по марке",
                    "Начало работ по марке",
                ]:
                    if block_id[k] == block_id[el[0]]:
                        new_des_act.append(el)
        ksg_for_val_data["activities"][ind_of_act][
            "descendant_activities"
        ] = new_des_act
        return ksg_for_val_data["activities"][ind_of_act]
