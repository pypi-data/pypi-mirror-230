from spprval.dataset.BaseDataset import BaseDataset
import datetime
from datetime import timedelta
import pandas as pd
from spprval.dataset.ObjectNameProcessor import ObjectNameProcessor


class PlanDataset(BaseDataset):
    def __init__(self, ksg_data):
        self.ksg_data = ksg_data

    def collect(self):
        model_dataset = pd.DataFrame()
        all_descendants = []

        for w in self.ksg_data["activities"]:
            current_descendant_activities = w.get("descendant_activities", [])
            all_descendants.extend(current_descendant_activities)

            name = w["activity_name"] + "_act_fact"
            start = datetime.datetime.strptime(w["start_date"].split()[0], "%Y-%m-%d")
            end = datetime.datetime.strptime(w["end_date"].split()[0], "%Y-%m-%d")
            vol = float(w["volume"])
            res_data = dict()
            for r in w["labor_resources"]:
                res_data[r["labor_name"]] = r["volume"]
            if not res_data:
                raise Exception(
                    'ERROR: One or more activities has no resources. Check "labor_resources" fields'
                )
            days = (end - start).days + 1
            vol_per = vol / days
            delta = timedelta(days=1)
            while start <= end:
                model_dataset.loc[start, name] = vol_per
                for k in res_data.keys():
                    model_dataset.loc[start, k + "_res_fact"] = res_data[k]
                start += delta

        if not all_descendants:
            raise Exception(
                'ERROR: No descendant activities found, at least one descendant activity should be present, check "descendant_activities" fields'
            )

        model_dataset.fillna(0, inplace=True)
        model_dataset.index = model_dataset.index.strftime("%d.%m.%Y")
        return model_dataset

    def get_act_names(self):
        act = []
        for w in self.ksg_data["activities"]:
            act.append(w["activity_name"])
        return act

    def get_res_names(self):
        res = []
        for w in self.ksg_data["activities"]:
            for r in w["labor_resources"]:
                if r["labor_name"] not in res:
                    res.append(r["labor_name"])
        return res

    def get_pools(self):
        model_dataset = pd.DataFrame()
        for w in self.ksg_data["activities"]:
            name = w["activity_name"]
            start = datetime.datetime.strptime(w["start_date"].split()[0], "%Y-%m-%d")
            end = datetime.datetime.strptime(w["end_date"].split()[0], "%Y-%m-%d")
            vol = float(w["volume"])
            days = (end - start).days + 1
            vol_per = vol / days
            delta = timedelta(days=1)
            while start <= end:
                model_dataset.loc[start, name] = vol_per
                start += delta
        model_dataset.fillna(0, inplace=True)
        work_pools = []
        for i in model_dataset.index:
            pool = []
            for c in model_dataset.columns:
                if model_dataset.loc[i, c] != 0:
                    pool.append(c)
            if pool not in work_pools:
                work_pools.append(pool)

        # act_names = self.get_act_names()
        # object_name_processor = ObjectNameProcessor()
        # act_pr_dict = object_name_processor.create_processed_dict(
        #     names=act_names, name_type="act"
        # )

        # new_pools = []
        # for p in work_pools:
        #     pool = []
        #     for pi in p:
        #         if pi in act_pr_dict:
        #             if act_pr_dict[pi][0] not in pool:
        #                 pool.append(act_pr_dict[pi][0])
        #         else:
        #             if pi not in pool:
        #                 pool.append(pi)
        #     if pool not in new_pools:
        #         new_pools.append(pool)
        return work_pools
