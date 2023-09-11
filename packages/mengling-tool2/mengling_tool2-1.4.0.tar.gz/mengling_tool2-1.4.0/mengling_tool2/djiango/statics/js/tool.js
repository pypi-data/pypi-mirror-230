//发送post请求
function sendPost(dt, url) {
    var temp = document.createElement("form");
    temp.action = url;
    temp.method = "POST";
    temp.style.display = "none";
    var opt;
    for (let name in dt) {
        opt = document.createElement("textarea");
        opt.name = name;
        opt.value = dt[name];//找id元素的值
        temp.appendChild(opt);
    }
    var body = $("body");
    body.append(temp);
    temp.submit();
    body[0].removeChild(temp);
}

//绑定回车按键
function enter(input_jq, mark_jq) {
    input_jq.keypress(function (event) {
        if (event.which === 13) {
            mark_jq[0].click();
        }
    });
}

function format(str, args) {
    if (args.length < 1) {
        return str;
    }
    var data = args; // 如果模板参数是数组
    if (args.length === 1 && typeof (args) == "object") {
        // 如果模板参数是对象
        data = args;
    }
    for (var key in data) {
        var value = data[key];
        if (undefined !== value) {
            //字符串替换中尽量不使用$，替换都会出现问题
            str = str.replace(new RegExp("\\{" + key + "\\}", "gm"), value);
        }
    }
    return str;
}

function getXpathElement(xpath_str) {
    return document.evaluate(xpath_str, document).iterateNext();
}

function getCookie(sName, default_value = null) {
    var aCookie = document.cookie.split("; ");
    for (var i = 0; i < aCookie.length; i++) {
        var aCrumb = aCookie[i].split("=");
        if (sName == aCrumb[0]) return unescape(aCrumb[1]);
    }
    return default_value;
}

//获取链接中的源及参数字典
function getUrlArgdt(url) {
    // 如果链接没有参数，或者链接中不存在我们要获取的参数，直接返回空
    if (url.indexOf("?") == -1) return [url, {}];

    // 获取链接中参数部分
    var queryString = url.substring(url.indexOf("?") + 1);

    // 分离参数对 ?key=value&key2=value2
    var parameters = queryString.split("&");

    var pos, paraName, paraValue, dt = {};
    for (var i = 0; i < parameters.length; i++) {
        // 获取等号位置
        pos = parameters[i].indexOf('=');
        if (pos == -1) continue;

        // 获取name 和 value
        paraName = parameters[i].substring(0, pos);
        paraValue = parameters[i].substring(pos + 1);

        // 如果查询的name等于当前name，就返回当前值，同时，将链接中的+号还原成空格
        dt[paraName] = paraValue.replace(/\+/g, " ");
    }
    return [url.split('?')[0], dt];
}

//链接添加参数
function getMergeUrl(url, dt) {
    var args = getUrlArgdt(url);
    for (var k in dt) {
        args[1][k] = dt[k];
    }
    var txts = [];
    for (k in args[1]) {
        txts.push(k + '=' + args[1][k]);
    }
    if (txts.length > 0) return args[0] + '?' + txts.join('&');
    else return args[0];
}

//获取无参数url
function getLocationUrl0() {
    return window.location.protocol + "//" + window.location.host + "" + window.location.pathname;
}

//合并字典
function mergeDts(dt1, dt2) {
    var dt = {};
    for (let k in dt1) {
        dt[k] = dt1[k];
    }
    for (let k in dt2) {
        dt[k] = dt2[k];
    }
    return dt;
}

//获取当前时间
function getNowTime() {
    var d = new Date(), str = '';
    str += d.getFullYear() + '年'; //获取当前年份
    str += d.getMonth() + 1 + '月'; //获取当前月份（0——11）
    str += d.getDate() + '日';
    str += d.getHours() + '时';
    str += d.getMinutes() + '分';
    str += d.getSeconds() + '秒';
    return str;
}

//用于给input设置数字千分符 onblur="this.value=comdify(this.value)
function comdify(n) {
    var re = /\d{1,3}(?=(\d{3})+$)/g;
    var n1 = n.replace(/^(\d+)((\.\d+)?)$/, function (s, s1, s2) {
        return s1.replace(re, "$&,") + s2;
    });
    return n1;
}


function getTableViewTxt(e_txts, n) {
    //傻逼js
    var xz1 = '<div class="col-sm-12"' + '><div class="row">';
    var i = 0, txt;
    for (let t in e_txts) {
        txt = format('<div class="col">{0}</div>', [e_txts[t]]);
        if (i < n) {
            xz1 += txt;
            i++;
        } else {
            xz1 += '</div></div><div class="col-sm-12"' + '><div class="row">' + txt;
            i = 1;
        }
    }
    //对齐处理
    for (i = 0; i < n - (e_txts.length > 0 ? e_txts.length % n : 0); i++) {
        xz1 += '<div class="col"></div>';
    }
    xz1 += '</div></div>';
    return xz1;
}

// 重写alert 提示框，可以自动消除
function auto_alert(str, t = 3000, w = 200, h = 80, f_size = 18) {
    var bordercolor;
    // titleheight = 25 //提示窗口标题高度
    bordercolor = "#336699";//提示窗口的边框颜色
    // titlecolor = "#99CCFF";//提示窗口的标题颜色
    var sWidth, sHeight;
    //获取当前窗口尺寸
    sWidth = document.body.offsetWidth;
    sHeight = document.body.offsetHeight;
    //背景div
    var bgObj = document.createElement("div");
    bgObj.setAttribute('id', 'alertbgDiv');
    bgObj.style.position = "absolute";
    bgObj.style.top = "0";
    bgObj.style.background = "#FFFFFF";
    bgObj.style.filter = "progid:DXImageTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75";
    //透明度
    bgObj.style.opacity = "0.3";
    bgObj.style.left = "0";
    bgObj.style.width = sWidth + "px";
    bgObj.style.height = sHeight + "px";
    bgObj.style.zIndex = "10000";
    document.body.appendChild(bgObj);
    //创建提示窗口的div
    var msgObj = document.createElement("div")
    msgObj.setAttribute("id", "alertmsgDiv");
    msgObj.setAttribute("align", "center");
    msgObj.style.background = "#787878";
    msgObj.style.border = "1px solid " + bordercolor;
    //div设置圆角
    msgObj.style.setProperty('border-radius', '5px 5px 5px 5px', 'important');
    msgObj.style.position = "absolute";
    msgObj.style.left = "50%";
    msgObj.style.font = f_size + "px/1.6em Verdana, Geneva, Arial, Helvetica, sans-serif";
    //窗口距离左侧和顶端的距离
    msgObj.style.marginLeft = "-75px";
    //窗口被卷去的高+（屏幕可用工作区高/2）-150
    msgObj.style.top = document.body.scrollTop + (window.screen.availHeight / 2) - 50 + "px";
    msgObj.style.width = w + "px";
    msgObj.style.height = h + "px";
    msgObj.style.textAlign = "center";
    <!-- msgObj.style.lineHeight ="25px";   -->
    msgObj.style.zIndex = "10001";
    document.body.appendChild(msgObj);
    //提示信息
    var txt = document.createElement("p");
    txt.setAttribute("id", "msgTxt");
    txt.style.margin = "10px 0";
    txt.innerHTML = str;
    txt.style.color = "white";
    document.getElementById("alertmsgDiv").appendChild(txt);
    //设置关闭时间
    if (t > 0) window.setTimeout("close_auto_alert()", t);
}

function close_auto_alert() {
    document.body.removeChild(document.getElementById("alertbgDiv"));
    document.body.removeChild(document.getElementById("alertmsgDiv"));
}

//判断是否包含
function ifContains(ls, obj) {
    for (let i in ls) {
        if (ls[i] == obj) return true;
    }
    return false;
}

//加密
function encryption(txt) {
    return window.btoa(unescape(encodeURIComponent(txt))).replaceAll('=', '_').replaceAll('+', '-');
}

//解密
function decrypt(txt_en) {
    return decodeURIComponent(escape(window.atob(txt_en))).replaceAll('_', '=').replaceAll('-', '+');
}

function hide(e) {
    e.style.display = 'none';
}

function hides(es) {
    for (var i = 0; i < es.length; i++) hide(es[i]);
}

function show(e) {
    e.style.display = '';
}

function shows(es) {
    for (var i = 0; i < es.length; i++) show(es[i]);
}

function get_option(values, if_emp = true) {
    let temp = '<option value="{0}">{0}</option>';
    let s = if_emp ? ['<option value="">--请选择--</option>'] : [];
    for (let i in values) s.push(format(temp, [values[i]]));
    return s.join('');
}