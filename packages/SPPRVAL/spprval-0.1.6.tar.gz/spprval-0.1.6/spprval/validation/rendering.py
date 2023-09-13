def style(cell_value):
    default = ""

    if "Типичное значение" in cell_value:
        return "background-color: green;"
    if "Редкое значение" in cell_value:
        return "background-color: yellow;"
    if "Критическое значение" in cell_value:
        return "background-color: red;"
    if "Недостаточно исторических данных" in cell_value:
        return "background-color: grey;"
    return default


def style_vedom(cell_value):
    default = ""

    if "Connect by ved with high Brave" in cell_value:
        return "background-color: green;"
    if "Connect by ved with low Brave" in cell_value:
        return "background-color: red;"
    if "Not connect by ved with high Brave" in cell_value:
        return "background-color: violet;"
    if "Not connect by ved with low Brave" in cell_value:
        return "background-color: blue;"
    if "Resource not in data" in cell_value or "Work not in data" in cell_value:
        return "background-color: grey;"
    return default


def create_res_html(df_style, name, result_path):
    df_map_style = df_style.style.applymap(style)
    df_html = df_map_style.render()
    with open(result_path + name + "/" + "res_report.html", "w") as file:
        file.write(df_html)
