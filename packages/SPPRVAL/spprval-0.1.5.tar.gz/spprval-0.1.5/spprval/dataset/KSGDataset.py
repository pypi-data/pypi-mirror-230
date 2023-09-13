from spprval.dataset.BaseDataset import BaseDataset
from spprval.dataset.ObjectNameProcessor import ObjectNameProcessor


class KSGDataset(BaseDataset):
    def __init__(self, ksg_data):
        self.ksg_data = ksg_data

    def collect(self):
        for iter_act, w in enumerate(self.ksg_data["activities"]):
            if w["activity_name"] == "":
                self.ksg_data["activities"].pop(iter_act)
        dict_class = ObjectNameProcessor()
        act = []
        for w in self.ksg_data["activities"]:
            act.append(w["activity_name"])
        res = []
        for w in self.ksg_data["activities"]:
            for r in w["labor_resources"]:
                if r["labor_name"] not in res:
                    res.append(r["labor_name"])
        act_dict = dict_class.create_granulary_dict(act, "act")
        res_dict = dict_class.create_granulary_dict(res, "res")
        plan_dict = {}
        for act in self.ksg_data["activities"]:
            name = act["activity_name"]
            smr_name = act["activity_name"]
            if name in act_dict:
                smr_name = act_dict[name][0]
            if smr_name in plan_dict:
                plan_dict[smr_name].append(name)
            else:
                plan_dict[smr_name] = [name]
        delete_act = []
        for el in plan_dict:
            if len(plan_dict[el]) > 1:
                for c in plan_dict[el][1:]:
                    delete_act.append(c)
        new_act = []
        deleted_id = []
        for w in self.ksg_data["activities"]:
            if (float(w["volume"]) != 0.0) and (w["activity_name"] not in delete_act):
                new_act.append(w)
            else:
                deleted_id.append(w["activity_id"])
        self.ksg_data["activities"] = new_act
        for w in self.ksg_data["activities"]:
            new_des = []
            for el in w["descendant_activities"]:
                if el[0] not in deleted_id:
                    new_des.append(el)
            w["descendant_activities"] = new_des
        for w in self.ksg_data["activities"]:
            if w["activity_name"] in act_dict:
                w["activity_name"] = act_dict[w["activity_name"]][0]
            for r in w["labor_resources"]:
                if r["labor_name"] in res_dict:
                    r["labor_name"] = res_dict[r["labor_name"]][0]
        return self.ksg_data
