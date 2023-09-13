import numpy as np
import pandas as pd


class Aggregator:
    def __init__(self, brave_crit_value: float = 0.45):
        self.CRIT_VALUE = brave_crit_value

    @staticmethod
    def get_all_seq_statistic(start_end_data, model_data):
        # for i in start_end_data.index:
        #     act_name = start_end_data.loc[i, "smr_name"]
        #     if start_end_data.loc[i, "smr_name"] in act_dict_processed_swapped.keys():
        #         if (
        #             len(act_dict_processed_swapped[start_end_data.loc[i, "smr_name"]])
        #             > 1
        #         ):
        #             act_name = random.choice(
        #                 act_dict_processed_swapped[start_end_data.loc[i, "smr_name"]]
        #             )
        #         else:
        #             act_name = act_dict_processed_swapped[
        #                 start_end_data.loc[i, "smr_name"]
        #             ][0]
        #     start_end_data.loc[i, "smr_name"] = act_name

        works_dict = {
            act["activity_id"]: act["activity_name"] for act in model_data["activities"]
        }
        pairs_labels = {
            (act["activity_name"], works_dict[el[0]]): el[1]
            for act in model_data["activities"]
            if act["descendant_activities"]
            for el in act["descendant_activities"]
        }

        pairs = list(pairs_labels.keys())

        if not pairs:
            return pd.DataFrame(), pd.DataFrame(), 0, 0

        freq_dict = {}

        def check_dates(row):
            s1 = row["first_day_x"]
            f1 = row["last_day_x"]
            s2 = row["first_day_y"]
            f2 = row["last_day_y"]

            fs = int(f1 < s2)
            ss = int(s1 == s2)
            ff = int(f1 == f2)
            mix = int(s2 < f1)
            total = fs + ss + ff + mix

            return pd.Series(
                [fs, ss, ff, mix, total], index=["FS", "SS", "FF", "FFS", "count"]
            )

        for w1, w2 in pairs:
            ind1 = start_end_data.loc[(start_end_data["granular_smr_name"] == w1)]
            ind2 = start_end_data.loc[(start_end_data["granular_smr_name"] == w2)]
            merged_data = pd.merge(
                ind1, ind2, how="inner", on="upper_works", suffixes=("_x", "_y")
            )
            counts = pd.Series(
                [0, 0, 0, 0, 0], index=["FS", "SS", "FF", "FFS", "count"]
            )
            if merged_data.shape[0] != 0:
                counts = merged_data.apply(check_dates, axis=1)

            total_fs = counts["FS"].sum()
            total_ss = counts["SS"].sum()
            total_ff = counts["FF"].sum()
            total_ffs = counts["FFS"].sum()
            total_count = counts["count"].sum()

            if total_count > 0:
                freq_dict[w1, w2] = {
                    "count": total_count,
                    "FS": total_fs,
                    "SS": total_ss,
                    "FF": total_ff,
                    "FFS": total_ffs,
                }

        bar_records = []
        color_records = []
        links = ["FFS", "FS", "SS", "FF"]

        for i, ((w1, w2), label) in enumerate(pairs_labels.items()):
            pair_data = freq_dict.get((w1, w2), {})
            total_count = pair_data.get("count", 0)
            if total_count == 0:
                continue

            mix_val = pair_data.get("FFS", 0) / total_count
            fs_val = pair_data.get("FS", 0) / total_count
            ss_val = pair_data.get("SS", 0) / total_count
            ff_val = pair_data.get("FF", 0) / total_count
            links_perc = [mix_val, fs_val, ss_val, ff_val]
            max_label = links[np.argmax(links_perc)]

            bar_record = {
                "Наименование работы 1": w1,
                "Наименование работы 2": w2,
                "Связь в плане": label,
                "FFS": mix_val * 100,
                "FS": fs_val * 100,
                "SS": ss_val * 100,
                "FF": ff_val * 100,
            }
            bar_records.append(bar_record)

            color_record = {
                "Наименование работы 1": w1,
                "Наименование работы 2": w2,
                "color": "green" if max_label == label else "red",
            }
            color_records.append(color_record)

        df_bar = pd.DataFrame.from_records(bar_records)
        df_color = pd.DataFrame.from_records(color_records)

        perc_dict = df_color["color"].value_counts().to_dict()
        norm_perc = (perc_dict.get("green", 0) / df_color.shape[0]) * 100
        not_perc = 0

        return df_bar, df_color, norm_perc, not_perc

    def get_res_ved_stat(self, brave, ksg_for_val_data):
        df_stat = pd.DataFrame(columns=["Работа", "Ресурс", "Метка ресурса"])
        # new_index = []
        # new_columns = []
        # for r in brave_res:
        #     if r.split("_res_fact")[0] in res_dict_swapped.keys():
        #         if len(res_dict_swapped[r.split("_res_fact")[0]]) > 1:
        #             new_index.append(
        #                 random.choice(res_dict_swapped[r.split("_res_fact")[0]])
        #                 + "_res_fact"
        #             )
        #         else:
        #             new_index.append(
        #                 res_dict_swapped[r.split("_res_fact")[0]][0] + "_res_fact"
        #             )
        #     else:
        #         new_index.append(r)
        # for r in brave_act:
        #     if r.split("_act_fact")[0] in act_dict_processed_swapped.keys():
        #         if len(act_dict_processed_swapped[r.split("_act_fact")[0]]) > 1:
        #             new_columns.append(
        #                 random.choice(
        #                     act_dict_processed_swapped[r.split("_act_fact")[0]]
        #                 )
        #                 + "_act_fact"
        #             )
        #         else:
        #             new_columns.append(
        #                 act_dict_processed_swapped[r.split("_act_fact")[0]][0]
        #                 + "_act_fact"
        #             )
        #     else:
        #         new_columns.append(r)
        # brave.index = new_index
        # brave.columns = new_columns
        # brave = brave.groupby(brave.index).sum()
        # brave = brave.groupby(axis=1, level=0).sum()

        def evaluate_resource(row):
            df_row = pd.DataFrame(columns=["Работа", "Ресурс", "Метка ресурса"])
            res = row["labor_resources"]
            act_name = row["activity_name"]
            for i, r in enumerate(res):
                df_row.loc[i, "Работа"] = act_name
                df_row.loc[i, "Ресурс"] = r["labor_name"]
                df_row.loc[i, "Метка ресурса"] = "grey"
                if (
                    f"{row['activity_name']}_act_fact" in brave.columns
                    and f"{r['labor_name']}_res_fact" in brave.index
                ):
                    df_row.loc[i, "Метка ресурса"] = (
                        "green"
                        if brave.loc[
                            r["labor_name"] + "_res_fact",
                            row["activity_name"] + "_act_fact",
                        ]
                        >= self.CRIT_VALUE
                        else "red"
                    )

            return df_row

        for work in ksg_for_val_data["activities"]:
            df_result = evaluate_resource(work)
            df_stat = pd.concat([df_stat, df_result], ignore_index=True)
        # df_stat = df_stat.append(
        #   pd.DataFrame(map(evaluate_resource, ksg_for_val_data["activities"])), ignore_index=True
        # )

        not_grey = df_stat[df_stat["Метка ресурса"] != "grey"]
        not_perc = (len(df_stat) - len(not_grey)) / len(df_stat) * 100
        norm_perc = (
            not_grey["Метка ресурса"].value_counts().to_dict().get("green", 0)
            / len(not_grey)
        ) * 100

        return df_stat, not_perc, norm_perc
