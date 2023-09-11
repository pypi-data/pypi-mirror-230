//直接弹窗弹窗
function actionWindow(body_txt, func_txt, title = '') {
    var txt = '<div class="modal fade" id="tc_{2}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">\
                    <div class="modal-dialog">\
                        <div class="modal-content">\
                            <div class="modal-header">\
                                <h4 class="modal-title">{3}</h4>\
                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>\
                            </div>\
                            <div class="modal-body">\
                            {0}\
                            </div>\
                            <div class="modal-footer">\
                                <button type="button" class="btn btn-default" data-dismiss="modal">关闭</button>\
                                <button type="button" class="btn btn-primary" onclick="{1};this.previousElementSibling.click();">提交</button>\
                            </div>\
                        </div>\
                    </div>\
                </div>';
    var en = md5(body_txt + func_txt);
    txt = format(txt, [body_txt, func_txt, en, title]);
    //不存在则添加元素
    var wd = document.getElementById('temp_window');
    var button_e = document.getElementById('temp_button');
    if (wd == null) {
        wd = document.createElement('div');
        wd.setAttribute("id", "temp_window");
    }
    if (button_e == null) {
        button_e = document.createElement('button');
        button_e.setAttribute("id", "temp_button");
    }
    wd.innerHTML = txt;
    document.body.appendChild(button_e);
    button_e.style.visibility = "hidden";
    button_e.after(wd);
    button_e.setAttribute("data-toggle", "modal");
    button_e.setAttribute("data-target", "#tc_" + en);
    button_e.click();
}