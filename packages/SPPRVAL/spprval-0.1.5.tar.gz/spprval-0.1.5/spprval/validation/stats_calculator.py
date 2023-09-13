class StatisticCalculator:
    def __init__(
        self,
        norm_res,
        norm_ved,
        norm_volume,
        norm_time,
        norm_seq,
        not_res,
        not_ved,
        not_volume,
        not_time,
        not_seq,
    ):
        self.norm_res = norm_res
        self.norm_ved = norm_ved
        self.norm_volume = norm_volume
        self.norm_time = norm_time
        self.norm_seq = norm_seq
        self.not_res = not_res
        self.not_ved = not_ved
        self.not_volume = not_volume
        self.not_time = not_time
        self.not_seq = not_seq

    def get_statistic_for_properties_and_all_stat(self):
        result_dict = dict()
        result_dict["Процент нормальных значений объёмов ресурсов"] = round(
            self.norm_res
        )
        if self.not_res != 100:
            result_dict["Процент нетипичных значений объёмов ресурсов"] = 100 - round(
                self.norm_res
            )
        else:
            result_dict["Процент нетипичных значений объёмов ресурсов"] = 0

        result_dict["Процент нормальных ресурсов по ведомостям"] = round(self.norm_ved)
        if self.not_ved != 100:
            result_dict["Процент нетипичных ресурсов по ведомостям"] = 100 - round(
                self.norm_ved
            )
        else:
            result_dict["Процент нетипичных ресурсов по ведомостям"] = 100
        result_dict["Процент нормальных значений времени работ"] = round(self.norm_time)
        if self.not_time != 100:
            result_dict["Процент нетипичных значений времени работ"] = 100 - round(
                self.norm_time
            )
        else:
            result_dict["Процент нетипичных значений времени работ"] = 0

        result_dict["Процент нормальных значений объёмов работ"] = round(
            self.norm_volume
        )

        if self.not_volume != 100:
            result_dict["Процент нетипичных значений объёмов работ"] = 100 - round(
                self.norm_volume
            )
        else:
            result_dict["Процент нетипичных значений объёмов работ"] = 0
        result_dict["Процент нормальных значений связей работ"] = round(self.norm_seq)
        if self.not_seq != 100:
            result_dict["Процент нетипичных значений связей работ"] = 100 - round(
                self.norm_seq
            )
        else:
            result_dict["Процент нетипичных значений связей работ"] = 0

        result_dict["Процент нормальных занчений по всем работам"] = round(
            (round(self.norm_time) + round(self.norm_volume) + round(self.norm_seq)) / 3
        )
        result_dict["Процент критических занчений по всем работам"] = 100 - round(
            (round(self.norm_time) + round(self.norm_volume) + round(self.norm_seq)) / 3
        )

        result_dict["Процент нормальных значений по всем ресурсам"] = round(
            (round(self.norm_res) + round(self.norm_ved)) / 2
        )
        result_dict["Процент критических значений по всем ресурсам"] = 100 - round(
            (round(self.norm_res) + round(self.norm_ved)) / 2
        )

        return result_dict

    def get_plan_statistic(self):
        norm_value = round(
            (
                self.norm_res
                + self.norm_ved
                + self.norm_volume
                + self.norm_time
                + self.norm_seq
            )
            / 5
        )
        crit_value = 100 - norm_value
        not_val = round(
            (
                self.not_res
                + self.not_ved
                + self.not_volume
                + self.not_time
                + self.not_seq
            )
            / 5
        )
        tested_val = 100 - not_val
        dict_result = {
            "Процент нормальных значений плана": norm_value,
            "Процент нетипичных значений плана": crit_value,
            "Процент непокрытых валидацией значений плана": not_val,
            "Процент покрытых валидацией значений плана": tested_val,
        }

        return dict_result
