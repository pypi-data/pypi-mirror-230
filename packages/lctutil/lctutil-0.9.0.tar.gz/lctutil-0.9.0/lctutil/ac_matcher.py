import ahocorasick

S_NAME_TAG = "STOCK"
S_CODE_TAG = "SCODE"
S_BK_TAG = "BK"
S_GAINIAN_TAG = "GN"

def decrypt(s):
    result = ""
    for i in range(len(s)):
        v = ord(s[i])
        if v > 256:
            result += chr(v - i - 1)
        else:
            result += s[i]
    return result.strip()


class AC:
    """
        敏感词检查
        构建词表的AC自动机
    """

    def __init__(self, enc = False):
        self.slot_ac = ahocorasick.Automaton()
        self.enc = enc

    def init_slot_ac(self, files):
        import os
        """
           读入词表文件, 逐个词插入 word: (tag, 词长)
           tag是文件名， 取第一个“.”前的， 比如： 歌曲.txt =>  歌曲;  歌曲.cn.txt =>  歌曲
        """
        for f in files:
            tag = os.path.basename(f).split(".")[0]
            for line in open(f):
                if self.enc: line = decrypt(line)
                if not line: continue
                exists_flag = self.slot_ac.get(line, None)
                if exists_flag is not None:
                    if tag not in exists_flag[0]:
                        exists_flag[0].append(tag)
                        self.slot_ac.add_word(line, (exists_flag[0], len(line)))
                else:
                    self.slot_ac.add_word(line, ([tag], len(line)))


    def init_slot_list_ac(self, lst, tag: str):
        for line in lst:
            exists_flag = self.slot_ac.get(line, None)
            if exists_flag is None:
                self.slot_ac.add_word(line, ([tag], len(line)))

    def init_keywords_list_ac(self, keys_lst, tag):
        for cate, keys in keys_lst:
            for k in keys:
                exists_flag = self.slot_ac.get(k, None)
                if exists_flag is None:
                    self.slot_ac.add_word(k, ([tag +"#"+ cate], len(k)))


    def make_from_file(self):
        import os.path
        import glob
        file_dir = os.path.dirname(__file__) + "/keywords/"
        files = glob.glob(file_dir + '*.txt')
        print(files)
        self.init_slot_ac(files)
        self.slot_ac.make_automaton()

    def make_from_list(self, lst, tag):
        print("Init AC: %s %d"%(tag, len(lst)))
        self.init_slot_list_ac(lst, tag)
        self.slot_ac.make_automaton()

    def match(self, query, tag=None):
        """
            找出一个AC自动机所有匹配到的词
        """
        ans = []
        if self.slot_ac is None: return ans
        for end_index, (tags, key_length) in self.slot_ac.iter(query):
            if tag is None or tag in tags:
                start_index = end_index - key_length + 1
                ans.append(query[start_index: end_index + 1])
        return ans

    def match_all(self, query):
        """
            找出一个AC自动机所有匹配到的词
        """
        ans = []
        has_seen = []
        if self.slot_ac is None: return ans
        for end_index, (tags, key_length) in self.slot_ac.iter(query):
            start_index = end_index - key_length + 1
            mt = query[start_index: end_index + 1]
            if mt not in has_seen:
                has_seen.append(mt)
                ans.append((mt, tags, start_index))
        return ans

from .stock_infos import info_stock_names, info_stock_codes, gainian_keywords, all_bankuai_2, all_bankuai_3


def remove_overlaps_and_sort(words, length):
    words.sort(key=lambda x: (-len(x[0]), x[2]))  # 根据关键词长度和起始位置排序
    bitmap = [0] * length  # 假设句子长度不会超过10000
    result = []

    for word, tags, start in words:
        end = start + len(word)
        if sum(bitmap[start:end]) == 0:  # 如果这个区间没有被其他关键词覆盖
            result.append(tags)  # 加入到结果中
            bitmap[start:end] = [1] * len(word)  # 更新位图

    return result


def filter_gn_tags(_mg, query):
    gns = []
    mg = remove_overlaps_and_sort(_mg, len(query))

    for tags in mg:
        for tag in tags:
            if tag.startswith(S_GAINIAN_TAG + "#"):
                ntag = tag[3:]
                if ntag not in gns: gns.append(ntag)

    return gns


stock_ac = AC()
stock_ac.init_slot_list_ac(info_stock_names, S_NAME_TAG)
stock_ac.init_slot_list_ac(info_stock_codes, S_CODE_TAG)
#stock_ac.init_slot_list_ac(all_gainian, S_GAINIAN_TAG)
stock_ac.init_keywords_list_ac(gainian_keywords, S_GAINIAN_TAG)
stock_ac.make_from_list(set(list(all_bankuai_2) + list(all_bankuai_3)), S_BK_TAG)
