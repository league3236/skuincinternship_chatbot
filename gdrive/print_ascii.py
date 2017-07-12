import html
import re


pre = '&#'
suf = ';'
result = ''
pattern = r'[가-힣]+'
for stt in st :
    if re.search(pattern, stt):
        result += (pre + str(ord(stt)) + suf)
    else:
        result += html.escape(stt)

print(result)