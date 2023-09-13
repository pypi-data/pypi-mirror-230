from spprval.database.DBWrapper import DBWrapper
import pandas as pd


class ObjectNameProcessor:
    def __init__(self, db_url="http://10.32.15.31:8000"):
        self.db = DBWrapper(db_url)

    def _get_names(self, name_type: str) -> pd.DataFrame:
        if name_type == "act":
            return self.db.get_act_names()
        elif name_type == "res":
            return self.db.get_res_names()
        else:
            raise ValueError(f"Unsupported name_type: {name_type}")

    def _create_dict(self, names, name_type: str, name_field: str, swap: bool = False):
        df_all_names = self._get_names(name_type)
        name_dict = df_all_names.set_index("name").to_dict()[name_field]
        result_dict = {}
        for name in names:
            if name in name_dict:
                if swap:
                    if name_dict[name] in result_dict:
                        result_dict[name_dict[name]].append(name)
                    else:
                        result_dict[name_dict[name]] = [name]
                else:
                    if name in result_dict:
                        result_dict[name].append(name_dict[name])
                    else:
                        result_dict[name] = [name_dict[name]]
            else:
                result_dict[name] = [name]
        result_dict.update((k, k) for k, v in result_dict.items() if v == "-")
        return result_dict

    def create_processed_dict(self, names, name_type: str, swap: bool = False):
        return self._create_dict(names, name_type, "processed_name", swap)

    def create_granulary_dict(self, names, name_type: str, swap: bool = False):
        return self._create_dict(names, name_type, "granulary_name", swap)
