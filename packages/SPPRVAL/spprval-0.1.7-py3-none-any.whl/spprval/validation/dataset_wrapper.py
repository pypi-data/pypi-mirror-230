import datetime
import json
import warnings
from datetime import timedelta

import pandas as pd

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


act_df = pd.read_csv("unique_tasks_dict.csv", sep=";")
act_dict = dict()
for i in act_df.index:
    act_dict[act_df.loc[i, "task_name"]] = act_df.loc[i, "unique_task_name"]


res_ved_dict = {
    "Агрегат сварочный_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Бурильная установка_res_fact": "Бурильная машина_res_fact",
    "Водители, Машинисты, Механизаторы_res_fact": "Машинист, водители_res_fact",
    "Водители, механизаторы_res_fact": "Машинист, водители_res_fact",
    "Водитель (Газ)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ автокран)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ миксер)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ площадка)_res_fact": "Машинист, водители_res_fact",
    "Водитель (савок)_res_fact": "Машинист, водители_res_fact",
    "Водитель_res_fact": "Машинист, водители_res_fact",
    "Грейдер_res_fact": "Автогрейдер_res_fact",
    "Кран стреловой_res_fact": "Автокран_res_fact",
    "Кран_res_fact": "Автокран_res_fact",
    "Кровельщик, изолировщик, арматурщик, бетонщик_res_fact": "Изолировщик_res_fact",
    "Кровельщик, изолировщик, арматурщик, отделочник, сантехник, отделочник_res_fact": "Изолировщик_res_fact",
    "Кровельщик, изолировщик, арматурщик, отделочник, сантехник_res_fact": "Изолировщик_res_fact",
    "Маш копра _res_fact": "Машинист, водители_res_fact",
    "Машинист ДЭС (дизельная электростанция)_res_fact": "Машинист, водители_res_fact",
    "Машинист ППУ (паровой передвижной установки)_res_fact": "Машинист, водители_res_fact",
    "Машинист Сваебойной установки_res_fact": "Машинист, водители_res_fact",
    "Машинист трубоукладчика_res_fact": "Машинист, водители_res_fact",
    "Машинист экскаватора_res_fact": "Машинист, водители_res_fact",
    "Механизатор_res_fact": "Машинист, водители_res_fact",
    "Монтажник ВЛ_res_fact": "Монтажник_res_fact",
    "Монтажник электромонтажа_res_fact": "Монтажник_res_fact",
    "Погрузчик телескопический Dieci Icarus_res_fact": "Погрузчик_res_fact",
    "Погрузчик телескопический_res_fact": "Погрузчик_res_fact",
    "Погрузчик фронтальный CAT_res_fact": "Погрузчик_res_fact",
    "Погрузчик-экскаватор Гидромик_res_fact": "Погрузчик_res_fact",
    "Помошник бурильщика_res_fact": "Бурильщик, помощник бурильщика_res_fact",
    "Сварочный агрегат_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный дизель-генератор_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный комплекс_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварщик ЭМУ _res_fact": "Сварщик_res_fact",
    "Сварщик ЭМУ_res_fact": "Сварщик_res_fact",
    "Сварщики РД (труба)_res_fact": "Сварщик_res_fact",
    "Сварщики РД_res_fact": "Сварщик_res_fact",
    "Сварщики СК (общестрой)_res_fact": "Сварщик_res_fact",
    "Сварщики по технологии_res_fact": "Сварщик_res_fact",
    "Сварщики_res_fact": "Сварщик_res_fact",
    "Седельный тягач (площадка)_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Седельный тягач (трал)_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Седельный тягач_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Слесарь АМЦ_res_fact": "Слесарь_res_fact",
    "Трактор_res_fact": "Трактор гусеничный_res_fact",
    "Трал_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Тягач_res_fact": "Тягач, тягач седельный, трал_res_fact",
    'Экскаватор  "Komatsu" movax_res_fact': "Экскаватор_res_fact",
    "Экскаватор оборудованный бурильным оборудованием_res_fact": "Экскаватор_res_fact",
    "Электрик, электромонтажник_res_fact": "Электромонтажник_res_fact",
    "Электрик_res_fact": "Электромонтажник_res_fact",
}


res_dict_all = {
    " Трубоукладчик ТГ-122Я_res_fact": "Трубоукладчик_res_fact",
    "АБС (миксер)_res_fact": "Бетономешалка_res_fact",
    "АДД_res_fact": "АДД (дизельный сварочный агрегат)_res_fact",
    "Автобетоносмеситель Урал 583100_res_fact": "Бетономешалка_res_fact",
    "Автобетоносмеситель_res_fact": "Бетономешалка_res_fact",
    "Автобетоносмиситель_res_fact": "Бетономешалка_res_fact",
    "Автокран  25 тн_res_fact": "Автокран_res_fact",
    'Автокран "Grove GMK 4100L"_res_fact': "Автокран_res_fact",
    'Автокран "Liebher LTM 1100-4.2"_res_fact': "Автокран_res_fact",
    "Автокран 50тн_res_fact": "Автокран_res_fact",
    "Автокран _res_fact": "Автокран_res_fact",
    "Автокран, до 25_res_fact": "Автокран_res_fact",
    "Автокраны и гидроманипуляторы_res_fact": "Автокран_res_fact",
    "Автомобильный кран_res_fact": "Автокран_res_fact",
    "Агрегат сварочный_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Бетоносмеситель_res_fact": "Бетономешалка_res_fact",
    "Бортовой Урал_res_fact": "Бортовой автомобиль_res_fact",
    "Бортовой автомобиль ГАЗ_res_fact": "Бортовой автомобиль_res_fact",
    'Бульдозер "CAT D8R"_res_fact': "Бульдозер_res_fact",
    'Бульдозер "Четра" Т-11_res_fact': "Бульдозер_res_fact",
    "Бульдозер _res_fact": "Бульдозер_res_fact",
    "Бульдозер типа Dressta (с рыхлителем)_res_fact": "Бульдозер_res_fact",
    "Бурилка_res_fact": "Бурильная машина_res_fact",
    "Бурильная машина БМ-811М_res_fact": "Бурильная машина_res_fact",
    "Бурильная установка_res_fact": "Бурильная машина_res_fact",
    'Бурильно-сваебойная "NIPPON"_res_fact': "Бурильная машина_res_fact",
    "Бурильно-сваебойная БМ811_res_fact": "Бурильная машина_res_fact",
    "Бурильно-сваебойный комплекс (на базе УРАЛ, КАМАЗ)_res_fact": "Бурильная машина_res_fact",
    "Бурильщик, помошник бурильщика_res_fact": "Бурильщик, помощник бурильщика_res_fact",
    "Бурильщик, помощник бурильщика_res_fact": "Бурильщик, помощник бурильщика_res_fact",
    "Бурильщик_res_fact": "Бурильщик, помощник бурильщика_res_fact",
    "Буровая машина БМ_res_fact": "Бурильная машина_res_fact",
    "Буровая машина_res_fact": "Бурильная машина_res_fact",
    "Буровая установка БМ 811_res_fact": "Бурильная машина_res_fact",
    "Буровая установка БМ_res_fact": "Бурильная машина_res_fact",
    "Буровая установка ТСГ_res_fact": "Бурильная машина_res_fact",
    "Буровая установка_res_fact": "Бурильная машина_res_fact",
    "Водители, Машинисты, Механизаторы_res_fact": "Машинист, водители_res_fact",
    "Водители, механизаторы_res_fact": "Машинист, водители_res_fact",
    "Водители_res_fact": "Машинист, водители_res_fact",
    "Водитель (Газ)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ автокран)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ миксер)_res_fact": "Машинист, водители_res_fact",
    "Водитель (КАМАЗ площадка)_res_fact": "Машинист, водители_res_fact",
    "Водитель (савок)_res_fact": "Машинист, водители_res_fact",
    "Водитель_res_fact": "Машинист, водители_res_fact",
    "Геодезист _res_fact": "Геодезист_res_fact",
    "Грейдер_res_fact": "Автогрейдер_res_fact",
    "ДЭС  АД-100с-Т400-1РМ1_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС  АД-60с-Т400-1РМ1_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС (дизельная электростанция)_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС SDMO-D110_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС SDMO-D350_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС45_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ДЭС_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "Деффектоскопист_res_fact": "Дефектоскопист_res_fact",
    "Дизель электростанция_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "Дизельная электростанция ДЭС-100_res_fact": "ДЭС (дизельная электростанция)_res_fact",
    "ИТР_res_fact": "ИТР (инженерно-технический персонал)_res_fact",
    "Изолеровщик_res_fact": "Изолировщик_res_fact",
    "Изолировщики_res_fact": "Изолировщик_res_fact",
    "Кран на автомобильном ходу г/п 25 тн на шасси Урал 4320 КС 45717_res_fact": "Автокран_res_fact",
    "Кран на гусеничном ходу РДК 250_res_fact": "Автокран_res_fact",
    "Кран стреловой_res_fact": "Автокран_res_fact",
    "Кран электрический СКГ-401_res_fact": "Автокран_res_fact",
    "Кран-манипулятор_res_fact": "Автокран_res_fact",
    "Кран_res_fact": "Автокран_res_fact",
    "Краны (автокран)_res_fact": "Автокран_res_fact",
    "Краны (автокран, RDK)_res_fact": "Автокран_res_fact",
    "Кровельщик, изолировщик, арматурщик, бетонщик_res_fact": "Изолировщик_res_fact",
    "Кровельщик, изолировщик, арматурщик, отделочник, сантехник, отделочник_res_fact": "Изолировщик_res_fact",
    "Кровельщик, изолировщик, арматурщик, отделочник, сантехник_res_fact": "Изолировщик_res_fact",
    "Маляр _res_fact": "Маляр_res_fact",
    "Маляры_res_fact": "Маляр_res_fact",
    "Маш СП-49_res_fact": "Машинист, водители_res_fact",
    "Маш копра _res_fact": "Машинист, водители_res_fact",
    "Маш. ДЭС_res_fact": "Машинист, водители_res_fact",
    "Маш. ППУ_res_fact": "Машинист, водители_res_fact",
    "Маш. трубоукладчика_res_fact": "Машинист, водители_res_fact",
    "Маш. экскаватора _res_fact": "Машинист, водители_res_fact",
    "Машинист_res_fact": "Машинист, водители_res_fact",
    "Машинисты, водители_res_fact": "Машинист, водители_res_fact",
    "Машинисты,водители_res_fact": "Машинист, водители_res_fact",
    "Машинисты_res_fact": "Машинист, водители_res_fact",
    "Механизатор_res_fact": "Машинист, водители_res_fact",
    "Механизаторы, водители, пом. машиниста бур. уст-ки_res_fact": "Машинист, водители_res_fact",
    "Механизаторы, водители, техник учет ГСМ_res_fact": "Машинист, водители_res_fact",
    "Механизаторы_res_fact": "Машинист, водители_res_fact",
    "Механик _res_fact": "Машинист, водители_res_fact",
    "Механик_res_fact": "Машинист, водители_res_fact",
    "Монтажник ВЛ_res_fact": "Электромонтажник_res_fact",
    "Монтажник ТТ_res_fact": "Монтажник ТТ (технологических трубопроводов)_res_fact",
    "Монтажник м/к_res_fact": "Монтажник МК (металлоконструкций)_res_fact",
    "Монтажник электромонтажа_res_fact": "Электромонтажник_res_fact",
    "Монтажники (СК)_res_fact": "Монтажник_res_fact",
    "Монтажники (труба)_res_fact": "Монтажник ТТ (технологических трубопроводов)_res_fact",
    "Монтажники стальных и ж/б конструкций_res_fact": "Монтажник МК (металлоконструкций)_res_fact",
    "Монтажники_res_fact": "Монтажник_res_fact",
    "Одноковшовый экскаватор емкостью не менее 1.2 куб.м_res_fact": "Экскаватор_res_fact",
    "ПСК (Передвижной Сварочный Комплекс) _res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "ПСК (Передвижной Сварочный Комплекс) Камаз_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "ПСК (передвижной сварочный комплекс)_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Передвижной сварочный агрегат АС-42_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Передвижной сварочный комплекс_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Погрузчик телескопический Dieci Icarus_res_fact": "Погрузчик_res_fact",
    "Погрузчик телескопический_res_fact": "Погрузчик_res_fact",
    "Погрузчик фронтальный CAT_res_fact": "Погрузчик_res_fact",
    "Погрузчик-экскаватор Гидромик_res_fact": "Погрузчик_res_fact",
    "Пом. Бур _res_fact": "Бурильщик, помошник бурильщика_res_fact",
    "Пом. машиниста бур. уст-ки_res_fact": "Бурильщик, помошник бурильщика_res_fact",
    "Помошник бурильщика_res_fact": "Бурильщик, помошник бурильщика_res_fact",
    "Разнорабочие_res_fact": "Разнорабочий_res_fact",
    "Разнорабочий, комендант, кладовщик_res_fact": "Разнорабочий_res_fact",
    "Сварочные посты_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный агрегат Denyo_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный агрегат на базе трактора_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный агрегат(дуговая сварка, полуавтоматическая,автоматическая,плазморезы и пр.)_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный ап. 2-хпост диз. На шасси_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный аппарат  1 пост_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный аппарат  10 пост ВДМ_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный аппарат  1пост_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный аппарат  2хпост_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный аппарат  4-хпост ВДМ_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный дизель-генератор_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварочный комплекс_res_fact": "АПС (агрегат передвижной сварочный)_res_fact",
    "Сварщик ТТ_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщик ЭМУ _res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщик ЭМУ_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщик м/к_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщик электромонтажа_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщик_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщики STT+М300 (труба)_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщики РД (труба)_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщики РД_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщики СК (общестрой)_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщики металлоконструкций_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Сварщики по технологии_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Сварщики_res_fact": "Сварщик ТТ (технологических трубопроводов)_res_fact",
    "Стропальщики_res_fact": "Стропальщик_res_fact",
    "Стропольщик_res_fact": "Стропальщик_res_fact",
    "Трубоукладчик _res_fact": "Трубоукладчик_res_fact",
    'Тягач  "Камаз"_res_fact': "Тягач, тягач седельный, трал_res_fact",
    "Тягач седельный_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Тягач сидельный_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Тягач, тягач седельный, трал_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Тягач_res_fact": "Тягач, тягач седельный, трал_res_fact",
    "Тягачи седельные_res_fact": "Тягач, тягач седельный, трал_res_fact",
    'Экскаватор  "Komatsu" movax_res_fact': "Экскаватор_res_fact",
    'Экскаватор  "Komatsu" вращатель_res_fact': "Экскаватор_res_fact",
    'Экскаватор  "Komatsu" ковш_res_fact': "Экскаватор_res_fact",
    "Экскаватор  HUNDAI R 250 LC-7 ковш_res_fact": "Экскаватор_res_fact",
    "Экскаватор (вращатель)_res_fact": "Экскаватор_res_fact",
    "Экскаватор (ковшевой)_res_fact": "Экскаватор_res_fact",
    "Экскаватор _res_fact": "Экскаватор_res_fact",
    "Экскаватор оборудованный бурильным оборудованием _res_fact": "Экскаватор_res_fact",
    "Экскаватор оборудованный бурильным оборудованием_res_fact": "Экскаватор_res_fact",
    "Экскватор _res_fact": "Экскаватор_res_fact",
    "Эл. монтажник_res_fact": "Электромонтажник_res_fact",
    "Электрик, электромонтажник_res_fact": "Электромонтажник_res_fact",
    "Электромонтажник по силовым сетям_res_fact": "Электромонтажник_res_fact",
    "Электромонтажник, электромонтер_res_fact": "Электромонтажник_res_fact",
    "Электромонтажники_res_fact": "Электромонтажник_res_fact",
    "Электромонтер_res_fact": "Электромонтажник_res_fact",
    "Электросварщик_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Электросварщики_res_fact": "Сварщик МК (металлоконструкций)_res_fact",
    "Электростанция (ДЭС) (50,100,200,400 кВт)_res_fact": "ДЭС (дизельная электростанция)_res_fact",
}


config = pd.read_csv("Config_of_params.csv")

BRAVE_CRIT = config.loc[0, "Crit value of Brave"]


def create_model_dataset(ksg_for_val_data):
    """Function to convert json file to msg file

    Args:
        ksg_for_val_data (dict): input json file
    Returns:
        DataFrame: msg file
    """
    model_dataset = pd.DataFrame()
    for w in ksg_for_val_data["activities"]:
        name = w["activity_name"]

        start = datetime.datetime.strptime(w["start_date"].split()[0], "%Y-%m-%d")
        end = datetime.datetime.strptime(w["end_date"].split()[0], "%Y-%m-%d")
        vol = float(w["volume"])
        res_data = dict()
        for r in w["labor_resources"]:
            if "_res_fact" in r["labor_name"]:
                res_data[r["labor_name"]] = r["volume"]
            else:
                res_data[r["labor_name"] + "_res_fact"] = r["volume"]
        days = (end - start).days + 1
        vol_per = vol / days
        delta = timedelta(days=1)
        while start <= end:
            model_dataset.loc[start, name] = vol_per
            for k in res_data.keys():
                model_dataset.loc[start, k] = res_data[k]
            start += delta
    model_dataset.fillna(0, inplace=True)
    model_dataset.index = model_dataset.index.strftime("%d.%m.%Y")
    model_columns = []
    for c in model_dataset.columns:
        if "_res_fact" not in c:
            model_columns.append(c + "_act_fact")
        else:
            model_columns.append(c)
    model_dataset.columns = model_columns

    return model_dataset


def get_work_pools(ksg_for_val_data):
    """Function for obtaining pools of parallel jobs in the KSG

    Args:
        ksg_for_val_data (dict): input json file

    Returns:
        list: list of pools
    """
    act = []
    for w in ksg_for_val_data["activities"]:
        act.append(w["activity_name"])
    model_dataset = pd.DataFrame()
    for w in ksg_for_val_data["activities"]:
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
        work_pools.append(pool)
    work_pools_final = []
    for p in work_pools:
        if p not in work_pools_final and len(p) != 0:
            work_pools_final.append(p)
    return work_pools_final


def get_validation_dataset(val_files, pools, act, res):
    """Function for generating a validation dataset

    Args:
        val_files (list): list of json files names which contain acts from ksg
        pools (list): list of work pools
        act (list): list of works
        res (list): list of resources

    Returns:
        DataFrame: validation dataset
    """
    validation_dataset = pd.DataFrame()
    msg_df = dict()
    for file in val_files:
        f = open(file, encoding="utf8")
        msg_json = json.load(f)
        for w in msg_json["work"]:
            name = w["work title"]
            if name in act_dict.keys():
                name = act_dict[name]
            if name:
                for w_d in w["work_data"]["progress"]:
                    if name not in msg_df.keys():
                        msg_df[name] = dict()
                        msg_df[name][list(w_d.keys())[0]] = float(
                            w_d[list(w_d.keys())[0]]["fact"]
                        )
                    else:
                        if list(w_d.keys())[0] in msg_df[name].keys():
                            msg_df[name][list(w_d.keys())[0]] += float(
                                w_d[list(w_d.keys())[0]]["fact"]
                            )
                        else:
                            msg_df[name][list(w_d.keys())[0]] = float(
                                w_d[list(w_d.keys())[0]]["fact"]
                            )
        for r in msg_json["resource"]:
            name = r["resource_name"]
            if name:
                if name + "_res_fact" in res_dict_all.keys():
                    name = res_dict_all[name + "_res_fact"].split("_")[0]
                elif name + "_res_fact" in res_ved_dict.keys():
                    name = res_ved_dict[name + "_res_fact"].split("_")[0]
                for r_d in r["progress"]:
                    if name not in msg_df.keys():
                        msg_df[name] = dict()
                        msg_df[name][list(r_d.keys())[0]] = float(
                            r_d[list(r_d.keys())[0]]["fact"]
                        )
                    else:
                        if list(r_d.keys())[0] in msg_df[name].keys():
                            msg_df[name][list(r_d.keys())[0]] += float(
                                r_d[list(r_d.keys())[0]]["fact"]
                            )
                        else:
                            msg_df[name][list(r_d.keys())[0]] = float(
                                r_d[list(r_d.keys())[0]]["fact"]
                            )

                    # if name in msg_df.columns:
                    #     if list(r_d.keys())[0] in msg_df.index:
                    #         if pd.isna(msg_df.loc[list(r_d.keys())[0], name]) or pd.isnull(msg_df.loc[list(r_d.keys())[0], name]):
                    #             try:
                    #                 msg_df.loc[list(r_d.keys())[0], name] = float(r_d[list(r_d.keys())[0]]['fact'])
                    #             except:
                    #                 msg_df.loc[list(r_d.keys())[0], name] = 0
                    #         else:
                    #             try:
                    #                 msg_df.loc[list(r_d.keys())[0], name] += float(r_d[list(r_d.keys())[0]]['fact'])
                    #             except:
                    #                 msg_df.loc[list(r_d.keys())[0], name] = 0
                    #     else:
                    #         try:
                    #             msg_df.loc[list(r_d.keys())[0], name] = float(r_d[list(r_d.keys())[0]]['fact'])
                    #         except:
                    #             msg_df.loc[list(r_d.keys())[0], name] = 0
                    # else:
                    #     try:
                    #         msg_df.loc[list(r_d.keys())[0], name] = float(r_d[list(r_d.keys())[0]]['fact'])
                    #     except:
                    #         msg_df.loc[list(r_d.keys())[0], name] = 0

    # for c in act:
    #     if c in msg_df.columns:

    #         for i in msg_df.index:
    #             validation_dataset.loc[i,c] = msg_df.loc[i,c]

    # for ri in res:
    #     if ri in msg_df.columns:

    #         for i in msg_df.index:
    #             validation_dataset.loc[i,ri] = msg_df.loc[i,ri]

    validation_dataset = pd.DataFrame.from_dict(msg_df)
    validation_dataset.fillna(0, inplace=True)
    # validation_dataset = validation_dataset.loc[(validation_dataset!=0).any(axis=1)]

    right_index = []
    for pool in pools:
        if len(pool) == 1:
            not_c = [ci for ci in act if ci != pool[0]]
            zero_ind = validation_dataset[not_c][
                (validation_dataset[not_c] == 0).all(axis=1)
            ].index
            for i in validation_dataset.index:
                if (validation_dataset.loc[i, pool[0]] != 0) and (i in zero_ind):
                    right_index.append(i)
        else:
            not_c = [ci for ci in act if ci not in pool]
            zero_ind = validation_dataset[not_c][
                (validation_dataset[not_c] == 0).all(axis=1)
            ].index
            for i in validation_dataset.index:
                flag = True
                for p in pool:
                    if validation_dataset.loc[i, p] == 0:
                        flag = False
                if flag and (i in zero_ind):
                    right_index.append(i)
    validation_dataset = validation_dataset[act + res]
    new_val_dataset = pd.DataFrame(validation_dataset.loc[right_index, :])

    new_ind = []
    for i in new_val_dataset.index:
        new_ind.append(datetime.datetime.strptime(i, "%d.%m.%Y"))
    new_val_dataset.index = new_ind
    new_val_dataset = new_val_dataset.sort_index()
    new_ind = []
    for i in new_val_dataset.index:
        try:
            new_ind.append(datetime.datetime.strftime(i, "%d.%m.%Y"))
        except BaseException:
            print("bug")
    new_val_dataset.index = new_ind

    model_columns = []
    for c in new_val_dataset.columns:
        if c in act:
            model_columns.append(c + "_act_fact")
        if c in res:
            model_columns.append(c + "_res_fact")
    new_val_dataset.columns = model_columns

    return new_val_dataset
