//用于功能的初始化使用
function fold_init() {
    //用于各项功能的初始化
    let es = document.getElementsByClassName('view_slide');
    for (let i = 0; i < es.length; i++) {
        setView(es[i], false);
    }
}

/**用于折叠栏实现**/
function _showdiv(a) {
    a.parentNode.previousElementSibling.style.display = "block";
    a.innerHTML = "收起-";
    a.onclick = function () {
        _hidediv(a)
    };
}

function _hidediv(a) {
    a.parentNode.previousElementSibling.style.display = "none";
    a.innerHTML = "展开+";
    a.onclick = function () {
        _showdiv(a)
    };
}

//添加class=view_slide
function setView(e, if_show = true) {
    var temp = document.createElement('div')
    temp.className = "slide";
    temp.innerHTML = '<a href="javascript:null" onclick="_hidediv(this);" class="btn-slide">收起-</a>';
    e.after(temp);
    if (!if_show) temp.childNodes[0].click();
}

