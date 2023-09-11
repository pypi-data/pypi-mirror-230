function _showOption(e) {
    show(e);
    shows(e.children);
}


function _search(e0, value) {
    show(e0);
    var e;
    for (var i = 0; i < e0.children.length; i++) {
        e = e0.children[i];
        if (e.textContent.indexOf(value) == -1) hide(e);
        else show(e);
    }
}


function setSelectInput(input_e, values) {
    input_e.className = "iput";
    input_e.setAttribute("placeholder", "请点击或输入搜索字段...");
    input_e.setAttribute("onclick", "_showOption(this.nextElementSibling)");
    input_e.setAttribute("oninput", "_search(this.nextElementSibling,this.value)");
    input_e.setAttribute("onporpertychange", "_search(this.nextElementSibling,this.value)");
    input_e.setAttribute("onchange", "_search(this.nextElementSibling,this.value)");
    var div = document.createElement('div');
    div.className = "op-list";
    div.style.display = 'none';
    var e;
    for (var i = 0; i < values.length; i++) {
        e = document.createElement('div');
        e.className = "iop";
        e.innerHTML = values[i];
        div.append(e);
    }
    input_e.after(div);

    $(document).on('click', '.iop', function () {
        hides($('.op-list'));
        var text = $(this).text();
        $('.iput').val(text);
    });
    $(document).click(function (e) {
        if ('iput' != e.target.className) {
            hides($('.op-list'));
        }
    });
}