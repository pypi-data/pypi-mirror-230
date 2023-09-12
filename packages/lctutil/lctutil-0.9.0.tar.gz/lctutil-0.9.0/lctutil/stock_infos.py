

import os
"""
股票列表
每个对应的概念和板块
板块列表
概念列表
"""


info_stock_names = []
info_stock_codes = []

code_name_kv = {}

filtered_gainian = set(["融资融券", "转融券标的", "富时罗素概念", "富时罗素概念股","深股通", "沪股通"])
gainian_keywords = []
all_bankuai_1 = set()
all_bankuai_2 = set()
all_bankuai_3 = set()

info_tables = {}

def loadcodes(filepath):
    with open(filepath, encoding="utf8") as f:
        for line in f:
            eles = line.strip().split(",")
            if len(eles) < 2: continue
            code, name = eles[0], eles[1]
            code_name_kv[name] = code
            code_name_kv[code] = name
            info_stock_names.append(name)
            info_stock_codes.append(code)

            all_bankuai_1.add(eles[3])
            all_bankuai_2.add(eles[4])
            all_bankuai_3.add(eles[5])

            info_tables[name] = (eles[2], eles[3], eles[4], eles[5])


loadcodes(os.getenv("STOCK_INFO_FILE"))


def get_code_or_name(ele):
    return code_name_kv.get(ele, "")

def get_name(ele):
    if '0' <= ele[0] and ele[0] <= '9':
        return code_name_kv.get(ele, ele)

    return ele


def load_cate():
    filepath = os.getenv("STOCK_CATE_FILE")
    with open(filepath, encoding="utf8") as f:
        for line in f:
            eles = line.strip().split(",")
            if len(eles) < 3: continue
            keywords = eles[2].split(";")
            cate = eles[0] + "-" + eles[1]
            gainian_keywords.append((cate, keywords))

load_cate()