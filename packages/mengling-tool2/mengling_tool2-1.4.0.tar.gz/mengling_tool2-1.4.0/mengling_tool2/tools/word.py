import traceback
import jieba
from jieba.analyse import extract_tags, textrank
import re
from googletrans import Translator
import pypinyin
from numpy.core.defchararray import capitalize


def division(txt: str, gap: str = ','):
    ss = jieba.cut(txt, cut_all=False)
    return gap.join(ss)


# 提取关键字
def getKeys(text, topK=10, notkeys={}, if_ls_and=True):
    keys = list()
    # 基于TF-IDF算法
    ls_tf = [k[0] for k in extract_tags(text, topK=topK, withWeight=True)]
    # 基于textrank算法
    tr_tf = [k[0] for k in textrank(text, topK=topK, withWeight=True)]
    # 结合两种算法得出权重关键字
    ls = (set(ls_tf) & set(tr_tf)) if if_ls_and else (set(ls_tf) | set(tr_tf))
    return [key for key in ls if key not in notkeys]


# 首字母大写
def titleCase(txt: str):
    ts = str(txt).split(' ')
    rs = []
    for t in ts:
        rs.append(str(capitalize(t)))
    return ' '.join(rs)


# 翻译
def translation(*txts, from_lang='en', to_lang="zh-CN") -> dict:
    # 设置Google翻译服务地址
    translator = Translator(service_urls=['translate.google.cn'])
    resultdt = dict()
    txts = set(txts)
    index, length = 0, len(txts)
    for txt in txts:
        try:
            translation = translator.translate(txt, src=from_lang, dest=to_lang)
            resultdt[txt] = translation.text
        except:
            traceback.print_exc()
            resultdt[txt] = txt
        index += 1
        print(f'\r{index}/{length}', end='')
    return resultdt


# 转为拼音,默认以空格分隔
def getPinYin(zh_txt: str, ifgetls=False, split: str = ' ', ifyindiao=False):
    if ifyindiao:
        pys = [''.join(py) for py in pypinyin.pinyin(zh_txt, heteronym=True)]
    else:
        pys = [''.join(py) for py in pypinyin.pinyin(zh_txt, style=pypinyin.NORMAL)]
    if ifgetls:
        return pys
    else:
        return split.join(pys)


def chinese_sorted(ls) -> list:
    return sorted(ls, key=lambda keys: [pypinyin.pinyin(i, style=pypinyin.Style.TONE3) for i in keys])
