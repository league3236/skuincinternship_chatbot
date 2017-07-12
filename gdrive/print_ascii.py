import html
import re




kword = '123'
pattern = '[`~!@#$%^&*_=+;:",./<>?]'
if re.search(pattern, kword) :
    print("찾음")


st = '1234'
if st.find(
