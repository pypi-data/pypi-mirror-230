from spprval.database.DataSource import DataSource
from idbadapter.schedule_loader import Schedules, PROCESSED, GRANULARY


class DBWrapper(DataSource):
    def __init__(self, url, level=GRANULARY):
        self.adapter = Schedules(url)
        self.level = level

    def get_data(self, pools, res_names):
        validation_dataset_list = []
        for df in self.adapter.get_works_by_pulls(
            work_pulls=pools, resource_list=res_names, key=self.level, res_key=GRANULARY
        ):
            if df is not None:
                df.fillna(0, inplace=True)
            validation_dataset_list.append(df)
        return validation_dataset_list

    def get_act_names(self):
        df = self.adapter.get_all_works_name()
        return df

    def get_res_names(self):
        df = self.adapter.get_all_resources_name()
        return df
