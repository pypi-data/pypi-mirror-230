"""
饼图处理
"""


class PieChart:
    @staticmethod
    def dict2pie(data: dict, unit: str = "", data_key: str = "count", total: int = None,
                 decimal_place: int = None, title: str = ""):
        """
        @param data: 分组出来的数据 示例1: {"人工智能":{"count":1},"工业制造":{"count":1}} 示例2: {"人工智能":1,"工业制造":1}
        @param title: 图题
        @param unit: 数据单位
        @param data_key: 数据key
        @param total: 总数
        @param decimal_place: 保留小数位   None 表示取整
        @return:
        """
        new_data = dict()
        if data_key is not None:
            for key, value in data.items():
                if isinstance(value, dict):
                    new_data.update({key: value.get(data_key)})
        else:
            new_data = data
        if total is None:
            total = sum([_ for _ in new_data.values()])
        if total == 0:
            total = 1
        result = {
            "title": title,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": k, "value": v, "unit": unit,
                         "proportion": round(v / total * 100, decimal_place)} for k, v in
                        new_data.items()
                    ],
                    "unit": unit,
                }
            ],
        }
        return result
