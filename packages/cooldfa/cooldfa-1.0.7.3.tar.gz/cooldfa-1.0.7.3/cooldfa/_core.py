from copy import deepcopy
from json import loads
from pathlib import Path


# 预置忽略词
preset_ignore_words = set('''
    `-_=~!@#$%^&*()+[ ]\\{}|;\',./:"<>?·！￥…（）—【】、；‘：“，。《》？
    ～＆＠＃”’〝〞＂＇´﹞﹝＞＜«»‹›〔〕〈〉』『〗〖｝｛」「］［︵︷︹︿︽﹁﹃︻︗＼｜／︘︼﹄﹂︾﹀︺︸︶＿﹏﹍﹎
    \n\r \t¦¡\xad¨ˊ¯￣﹋﹉﹊ˋ︴¿ˇ\u3000
'''.lower())

# 预置敏感词
words_dir = Path(__file__).parent / '_words'
class PresetWords:
    politics: list
    sex: list
    violence: list
    url: list
    others: list

    def __getattr__(self, name):
        self.__setattr__(name, loads((words_dir / f'{name}.json').read_text('utf8')))
        return self.__dict__[name]
preset_words = PresetWords()

# dfa算法
class dfa():
    ignore_words = preset_ignore_words
    tree = {}

    def __init__(self, *words_lists):
        self.ignore_words = self.ignore_words.copy()
        self.tree = deepcopy(self.tree)
        # 导入词库
        all_words = set()
        for words in words_lists: all_words |= set(words)
        for word in all_words:
            self.add_word(word)
    
    def add_word(self, word:str):
        tree = self.tree
        for x in word.lower():
            if x not in self.ignore_words:
                tree = tree.setdefault(x, {})
        tree['__'] = 0
        # '__'必须大于1个字符
        # 这样才能使<if treeSon := tree.get(s):>判断为False, 否则在添加空敏感词''后, 查找时会报错
    
    def sub(self, text:str, repl:str='*', compress=False):
        last_i = -1
        new_text = []
        content = text.lower()
        if compress:
            for start_i, t in enumerate(content):
                if t not in self.ignore_words:
                    if indexs := self._find_base(content, start_i):
                        i = indexs[0]
                        new_text.append(text[last_i+1:start_i])
                        new_text.append(repl)
                        last_i = i
        else:
            for start_i, t in enumerate(content):
                if t not in self.ignore_words:
                    if indexs := self._find_base(content, start_i):
                        i = indexs[0]
                        new_text.append(text[last_i+1:start_i])
                        new_text.append(repl * (i+1-start_i))
                        last_i = i
        new_text.append(text[last_i+1:])
        return ''.join(new_text)

    def find_one(self, text:str):
        text = text.lower()
        for start_i, t in enumerate(text):
            if t not in self.ignore_words:
                for i in self._find_base(text, start_i):
                    return text[start_i: i+1]
        return ''
    
    def find_all(self, text:str):
        text = text.lower()
        words = []
        for start_i, t in enumerate(text):
            if t not in self.ignore_words:
                for i in self._find_base(text, start_i):
                    words.append(text[start_i: i+1])
        return words
    
    def _find_base(self, text, start_i):
        tree = self.tree
        for i in range(start_i, len(text)):
            s = text[i]
            if treeSon := tree.get(s):
                tree = treeSon
                if "__" in tree: return [i]
            elif s not in self.ignore_words:
                return []
        return []