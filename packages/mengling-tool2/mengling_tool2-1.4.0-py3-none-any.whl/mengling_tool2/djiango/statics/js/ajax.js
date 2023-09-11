//改变元素内容,url仅访问statics的内容 ../statics/temp.html'
function ajaxChange(url, jq, method = 'GET', data = null) {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        //  IE7+, Firefox, Chrome, Opera, Safari 浏览器执行代码
        xmlhttp = new XMLHttpRequest();
    } else {
        // IE6, IE5 浏览器执行代码
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
            // document.getElementById(id).innerHTML = xmlhttp.responseText;//不会执行js
            $(jq).html(xmlhttp.responseText);//转为html对象后加入至目标下
        }
    }
    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.send(data);
}

//表单提交
function formSubmit(form, url, result_success_func, error_func = null, type = "POST", ifasync = false) {
    $.ajax({
        type: type,//方法类型
        url: url,//url
        data: form != null ? form.serialize() : null,
        async: ifasync,
        success: function (result) {
            result_success_func(result);
            return false;//需要加,否则window.location.href跳转无法执行
            // if (result.resultCode == 200)
        },
        error: function () {
            if (error_func) error_func();
        }
    });
}

//表单提交
function getFormSubmit(form_jq, url, type = "POST", ifasync = false) {
    var r = null, status = false;
    $.ajax({
        type: type,//方法类型
        url: url,//url
        data: form_jq != null ? form_jq.serialize() : null,
        //使用异步返回必然为null
        async: ifasync,
        success: function (result) {
            r = result;
            return false;//需要加,否则window.location.href跳转无法执行
            // if (result.resultCode == 200)
        },
        error: function () {
            r = null;
        }
    });
    return r;
}

//自动同步
function auto(url, jq, timeout, method = 'GET', data = null) {
    var fn = function () {
        ajaxChange(url, jq, method, data);
        setTimeout(fn, timeout);
    }
    fn();
}


//文件上传,旧版使用仅保留
function upload(url, e_or_id, ifasync = false, note = '正在上传...') {
    var formData;
    if (typeof e_or_id == 'string') formData = new FormData(document.getElementById(e_or_id));
    else formData = new FormData(e_or_id);
    var r = null;
    auto_alert(note, t = -1);
    $.ajax({
        url: url,
        type: "post",
        data: formData,
        async: ifasync,
        processData: false,
        contentType: false,
        success: function (res) {
            if (res) {
                close_auto_alert();
                alert(res);
                r = res;
            }
            return false;
        },
        error: function (err) {
            close_auto_alert();
            console.log(err);
            alert("上传失败!\n" + err);
            r = err;
        }
    })
    return r;
}

//ajax发射类
class Ajax {
    //构造方法
    constructor(type = 'POST') {
        var my = this;
        this.kwarg = {
            type: type,//方法类型
            //使用异步返回必然为null
            async: false,
            success: function (result) {
                console.log(`请求成功: ${result}`);
                my.result = result;
                return false;
            },
            error: function (err) {
                console.log(`请求失败: ${result}`);
                my.result = err;
            }
        };
        this.result = null;
    }

    setKwarg(dt) {
        for (var k in dt) this.kwarg[k] = dt[k];
    }

    setSuccessFunc(result_func) {
        var my = this;
        this.kwarg.success = function (result) {
            result_func(result);
            console.log(`请求成功: ${result}`);
            my.result = result;
            return false;
        }
    }

    setErrorFunc(result_func) {
        var my = this;
        this.kwarg.error = function (err) {
            result_func(err);
            console.log(`请求失败: ${result}`);
            my.result = err;
        }
    }

    setAsync(on = true) {
        this.kwarg.async = on;
    }

    //通用执行方式
    run(url, data, kwarg = null) {
        if (kwarg == null) {
            kwarg = JSON.parse(JSON.stringify(this.kwarg));
            //方法不会拷贝
            kwarg.success = this.kwarg.success;
            kwarg.error = this.kwarg.error;
        }
        kwarg.url = url;
        kwarg.data = data;
        //自动设置数据格式类型
        if (typeof data == 'string') {
            delete kwarg.processData;
            delete kwarg.contentType;
        } else {
            //类型为对象
            kwarg.processData = false;
            kwarg.contentType = false;
        }
        $.ajax(kwarg);
        return this.result;
    }

    //djiango获取不到json传输的post数据,使用以下方法获取
    // datadt=json.loads(request.body)
    run_json(url, data, kwarg = null) {
        if (kwarg == null) {
            kwarg = JSON.parse(JSON.stringify(this.kwarg));
            //方法不会拷贝
            kwarg.success = this.kwarg.success;
            kwarg.error = this.kwarg.error;
        }
        kwarg.url = url;
        kwarg.data = JSON.stringify(data);
        kwarg.contentType = "application/json;charset=utf-8";
        //kwarg.dataType = "json"; //返回结果为j
        $.ajax(kwarg);
        return this.result;
    }

    //文件上传
    upload(url, data, note = '正在上传...') {
        if (typeof data == 'string') throw 'upload用于文件上传使用,输入参数不能为字符串!';
        auto_alert(note, -1);
        var kwarg = JSON.parse(JSON.stringify(this.kwarg))
        var aer = this;
        kwarg.success = function (res) {
            close_auto_alert();
            return aer.kwarg.success(res);
        };
        kwarg.error = function (err) {
            close_auto_alert();
            aer.kwarg.error(res);
        };

        return this.run(url, data, kwarg);
    }
}