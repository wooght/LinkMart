///**
//JS基本操作函数库
//by wooght
//2018-10-09
///**

// 利润计算  返回序列
function totle_income(all_data){
    result_list = [[],[],[],[]]    //[时间序列，纯利, 开支, 收入]
    for(key of Object.keys(all_data['month_list'])){
        // 时间序列
        result_list[0].push(all_data['month_list'][key])
        //开支序列
        loss =all_data['wages'][key] + all_data['insurance'][key] + all_data['meituan'][key] +
                    all_data['rent'][key] + all_data['hydropower'][key] + all_data['expenditure'][key] + all_data['loss'][key]
        //收入系列
        income = all_data['profit'][key] + all_data['income'][key]
        //纯利序列
        net_profit = income - loss
        result_list[1].push(net_profit)
        result_list[2].push(loss)
        result_list[3].push(income)
    }
    return result_list
}

// 数组求和
function array_sums(array){
    result = 0
    for(value of Object.values(array)){
        result += parseFloat(value)
    }
    //console.log(result)
    return result
}

//数组求和函数
function array_sum(arr,sk1,sk2){
    sum=0
    for(i=sk1,j=sk2;i<sk2;i++){
        sum+=arr[i]
    }
    return sum;
}

// 数组求平均值 并返回数组
function array_average(arr){
    average_arr = []
    for(i=0;i<arr.length;i++){
       if(i<30){
            average_arr.push(array_sum(arr,0,i)/(i+1))
       }else{
            average_arr.push(array_sum(arr,i-30,i)/30)
       }
    }
    return average_arr;
}

// 页面跳转
function gotolaction(value){
    window.location.href=value;
}
// 获取状态改变结果
function get_change_result(url,id){
    $.get(url,function(data){
//        data = eval(data);
        alert(data);
        document.getElementById(id).style.display='none';
    });
}
//确认及跳转
function are_ok(name,str_code,id){
    if(confirm('已进货操作？'+name)){
        get_change_result(str_code,id)
    }
}

// 获取踩点门店列表
function get_cd_stores(url,id){
    $.get(url,function(data){
        alert(data)
    })
}


//删除表格非第一行
function delete_tr(deltable)
{
    l = deltable.getElementsByTagName("tr").length;
    for(var i=0;i<l;i++){
        if(i>0){
            deltable.deleteRow(1);
        }
    }
}
//copy到剪贴板
function copy_text(thetr,nums)
{
    box = document.getElementById("smailbox")
    copyTocopy=document.getElementById("copyTocopy")
    copyTocopy.value = nums
    copyTocopy.select();
    document.execCommand("Copy"); // 执行浏览器复制命令
    box.innerText = nums+'已复制条码'
    alert_box(box,1000)
    thetr.focus()
}
//弹窗
function alert_box(box,time){
    box.style.display = 'block'
    setTimeout(function(){box.style.display = 'none';},time)
}

//
//  echarts 表格封装函数
//
// 饼装图
function set_pie(chart_doc, all_data, chart_name){
    //all_data [[项目，数字],..]
    classify_data = []
    var i=0;
    for(key in all_data){
        if(all_data[key][1]<1){continue;}
        classify_data.push({value:all_data[key][1],name:all_data[key][0]})
    }
    //图标使用格式 [{value:XX,name:XX},{}]
    option = {
        title: {
            text: chart_name,
            subtext: 'LinkMart Data',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [
            {
              name: chart_name,
              type: 'pie',
              radius: '50%',
              data: classify_data.sort(function (a, b) { return a.value - b.value; }),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
        ]
    };
    chart_doc.setOption(option);
}

// 普通图表
function set_charts(chart_doc, all_data, x_list, chart_name, legend_list){
    /*
        all_data Y轴数据[{name:X,type:line/bar,data:[x,..]},{}]
    */
    var option = {
        title: {
            text: chart_name        //图表标题
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
              label: {
                show: true
              }
            }},
        legend: {
            data:legend_list,       //头部导航[名称，..]
            right:0,
        },
        xAxis: {
            data: x_list            // X坐标数据
        },
        yAxis: {},
        series: all_data            // Y轴数据[{name:X,type:line/bar,data:[x,..]},{}]
    };
    chart_doc.setOption(option)
}

//热力图标
function hotmap(chart_doc, all_data, chart_name){
    const hours = []
    for(i=0;i<24;i++){
        hours.push(i)
    }
    // prettier-ignore
    const days = [
        '星期一', '星期二', '星期三',
        '星期四', '星期五', '星期六', '星期天'
    ];
    // prettier-ignore
    const data = all_data.map(function (item) {
        return [item[1], item[0], parseInt(item[2]) || '-'];
    });
    option = {
      tooltip: {
        position: 'top'
      },
      grid: {
        height: '50%',
        top: '10%'
      },
      xAxis: {
        type: 'category',
        data: hours,
        splitArea: {
          show: true
        }
      },
      yAxis: {
        type: 'category',
        data: days,
        splitArea: {
          show: true
        }
      },
      visualMap: {
        min: 0,
        max: 80,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '15%'
      },
      series: [
        {
          name: '商品数',
          type: 'heatmap',
          data: data,
          label: {
            show: true
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
    chart_doc.setOption(option)
}