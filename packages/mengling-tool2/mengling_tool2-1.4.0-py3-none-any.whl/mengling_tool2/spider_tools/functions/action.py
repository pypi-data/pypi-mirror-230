import json
import traceback
import urllib.parse
import execjs
import requests


# 谷歌翻译，英翻汉
def translate(text):
    assert len(text) < 4891, "翻译的长度超过限制！！！"
    tk = execjs.compile("""
           function TL(a) {
           var k = "";
           var b = 406644;
           var b1 = 3293161072;
           var jd = ".";
           var $b = "+-a^+6";
           var Zb = "+-3^+b+-f";

           for (var e = [], f = 0, g = 0; g < a.length; g++) {
               var m = a.charCodeAt(g);
               128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
               e[f++] = m >> 18 | 240,
               e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
               e[f++] = m >> 6 & 63 | 128),
               e[f++] = m & 63 | 128)
           }
           a = b;
           for (f = 0; f < e.length; f++) a += e[f],
           a = RL(a, $b);
           a = RL(a, Zb);
           a ^= b1 || 0;
           0 > a && (a = (a & 2147483647) + 2147483648);
           a %= 1E6;
           return a.toString() + jd + (a ^ b)
       };

       function RL(a, b) {
           var t = "a";
           var Yb = "+";
           for (var c = 0; c < b.length - 2; c += 3) {
               var d = b.charAt(c + 2),
               d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
               d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
               a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
           }
           return a
       }
       """).call("TL", text)

    content = urllib.parse.quote(text)
    url = "http://translate.google.cn/translate_a/single?client=t" \
          "&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
          "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1" \
          "&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)
    result = requests.get(url).text
    end = result.find("\",")
    if end > 4: result = result[4:end]
    return result


# 获取识别后的验证码
def getYZM(base64):
    # 调用接口来进行识别,非本地ocr软件
    try:
        js = json.loads(requests.post(
            'https://www.paddlepaddle.org.cn/paddlehub-api/image_classification/chinese_ocr_db_crnn_mobile',
            data='{"image":"%s"}' % base64).text)
        result = js['result'][0]['data'][0]['text']
        return result
    except:
        traceback.print_exc()
        print('[验证码解析失败]', js['result'][0])
        return None
