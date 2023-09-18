from cooldfa import dfa, preset_words

# dfa算法
example = dfa(['123', '56', 'end'])
text = '1--2--3--4--5--6--7--8--9--end--'

assert example.find_one(text) == '1--2--3'
assert example.find_all(text) == ['1--2--3', '5--6', 'end']
assert example.sub(text, '*') == '*******--4--****--7--8--9--***--'

# 使用预置的敏感词库
example = dfa(
    preset_words.politics,
    preset_words.sex,
    preset_words.violence,
    preset_words.url,
    preset_words.others,
)

# 记录测试结果
name = 'me/cooldfa'
print(f'[测试通过] {name}')