//dt格式:{'name': name, 'type': 'line', 'stack': '总量', 'data': []}
function lines0(doc, title, names, xs, yss) {
    let dts = [];
    for (let i = 0, len = names.length; i < len; i++) {
        dts.push({name: names[i], type: 'line', stack: '总量', data: yss[i]});
    }
    let option = {
        title: {
            text: title
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: names
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: xs
        },
        yAxis: {
            type: 'value'
        },
        series: dts
    };
    let myChart = echarts.init(doc);
    option && myChart.setOption(option);
}

//单线渐变折线图
function line0(doc, title, xs, ys) {
    //计算小区间及大区间
    let mean = 0;
    let len = ys.length;
    for (let i = 0; i < len; i++) {
        mean += ys[i];
    }
    mean /= len;
    let min = (Math.min.apply(null, ys) + mean) / 2;
    let max = (Math.max.apply(null, ys) + mean) / 2;

    let option = {
        // Make gradient line here
        visualMap: {
            show: false,
            type: 'continuous',
            seriesIndex: 0,
            min: min,
            max: max
        },
        title: {
            left: 'center',
            text: title
        },
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            data: xs
        },
        yAxis: {},
        grid: {
            bottom: '30%'
        },
        series: {
            type: 'line',
            showSymbol: false,
            data: ys
        }
    };
    let myChart = echarts.init(doc);
    option && myChart.setOption(option);
}