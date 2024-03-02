/*
    baidumap 基本功能API
    by wooght 2019-10
*/
// 打开绘图编辑功能
function editor(map,BMapGLLib){
    document.getElementById('editor').style.display = 'block'
    var styleOptions = {
        strokeColor: '#5E87DB',   // 边线颜色
        fillColor: '#5E87DB',     // 填充颜色。当参数为空时，圆形没有填充颜色
        strokeWeight: 2,          // 边线宽度，以像素为单位
        strokeOpacity: 1,         // 边线透明度，取值范围0-1
        fillOpacity: 0.2          // 填充透明度，取值范围0-1
    };
    var labelOptions = {
        borderRadius: '2px',
        background: '#FFFBCC',
        border: '1px solid #E1E1E1',
        color: '#703A04',
        fontSize: '12px',
        letterSpacing: '0',
        padding: '5px'
    };

    // 实例化鼠标绘制工具
    var drawingManager = new BMapGLLib.DrawingManager(map, {
        // isOpen: true,        // 是否开启绘制模式
        enableCalculate: false, // 绘制是否进行测距测面
        enableSorption: true,   // 是否开启边界吸附功能
        sorptiondistance: 20,   // 边界吸附距离
        circleOptions: styleOptions,     // 圆的样式
        polylineOptions: styleOptions,   // 线的样式
        polygonOptions: styleOptions,    // 多边形的样式
        rectangleOptions: styleOptions,  // 矩形的样式
        labelOptions: labelOptions,      // label样式
    });

    function draw(e) {
        var arr = document.getElementsByClassName('bmap-btn');
        for(var i = 0; i<arr.length; i++) {
            arr[i].style.backgroundPositionY = '0';
        }
        e.style.backgroundPositionY = '-52px';
        switch(e.id) {
            case 'marker': {
                var drawingType = BMAP_DRAWING_MARKER;
                break;
            }
            case 'polyline': {
                var drawingType = BMAP_DRAWING_POLYLINE;
                break;
            }
            case 'rectangle': {
                var drawingType = BMAP_DRAWING_RECTANGLE;
                break;
            }
            case 'polygon': {
                var drawingType = BMAP_DRAWING_POLYGON;
                break;
            }
            case 'circle': {
                var drawingType = BMAP_DRAWING_CIRCLE;
                break;
            }
        }
        // 进行绘制
        if (drawingManager._isOpen && drawingManager.getDrawingMode() === drawingType) {
            drawingManager.close();
        } else {
            drawingManager.setDrawingMode(drawingType);
            drawingManager.open();
        }
    };
}

// 显示行政区域
function add_city(map,city_name){
    var dist = new BMapGL.DistrictLayer({
        name: '('+city_name+')',
        kind: 1,
        fillColor: '#618bf8',
        fillOpacity: 0.3,
        strokeColor: '#ffffff',
        viewport: true,
    });
    map.addDistrictLayer(dist);
    // --- 行政区划添加鼠标事件 ---
    dist.addEventListener('mouseover', function (e) {
        e.currentTarget.setFillColor('#9169db');
    });
    dist.addEventListener('mouseout', function (e) {
        e.currentTarget.setFillColor(e.currentTarget.style.fillColor);
    });
}


// 添加地铁站占位
function add_dtz(map,points,text,isbig){
    iconsize = isbig?26:12
    myicon = new BMapGL.Icon("/wooght_echarts/pic/dtz.gif", new BMapGL.Size(iconsize,iconsize));
    //添加标记点
    var marker1 = new BMapGL.Marker(new BMapGL.Point(points[0],points[1]),{icon:myicon});
    map.addOverlay(marker1);
    var opts = {
        position: new BMapGL.Point(points[0],points[1]), // 指定文本标注所在的地理位置
        offset: new BMapGL.Size(15, -20) // 设置文本偏移量
    };
    // 创建文本标注对象
    var label = new BMapGL.Label(text, opts);
    // 自定义文本标注样式
    label.setStyle({
        color: isbig?'#222':'#999',
        borderRadius: isbig ? '5px':'3px',
        borderColor: '#6666cc',
        padding: isbig ? '4px':'2px',
        fontSize: isbig ? '14px':'10px',
        height: isbig ? '16px':'12px',
        lineHeight: isbig ? '16px': '12px',
        fontFamily: '微软雅黑',
    })
    if(text.length>0){
        map.addOverlay(label)
    }
}
//添加标注
function add_text(map,points,text){
    var opts = {
        position: new BMapGL.Point(points[0],points[1]), // 指定文本标注所在的地理位置
        offset: new BMapGL.Size(0, 0) // 设置文本偏移量
    };
    // 创建文本标注对象
    var label = new BMapGL.Label(text, opts);
    // 自定义文本标注样式
    label.setStyle({
        color: '#222',
        borderRadius: '5px',
        borderColor: '#6666cc',
        padding: '4px',
        fontSize: '24px',
        height: '26px',
        lineHeight: '26px',
        fontFamily: '微软雅黑',
        background: '#ee9'
    })
    map.addOverlay(label)
}
//添加静态标注
function add_smail_text(map,points,text){
    var opts = {
        position: new BMapGL.Point(points[0],points[1]), // 指定文本标注所在的地理位置
        offset: new BMapGL.Size(0, 0) // 设置文本偏移量
    };
    // 创建文本标注对象
    var label = new BMapGL.Label(text, opts);
    // 自定义文本标注样式
    label.setStyle({
        color: '#fff',
        borderRadius: '4px',
        borderColor: '#bbb',
        padding: '2px',
        fontSize: '12px',
        height: '14px',
        lineHeight: '12px',
        fontFamily: '微软雅黑',
        background: '#aaa'
    })
    map.addOverlay(label)
}

// 显示公交线路
function add_bus(map,name){
        var busline = new BMapGL.BusLineSearch(map,{
            renderOptions:{map:map,panel:"r-result"},
            onGetBusListComplete: function(result){
                if(result) {
                    var fstLine = result.getBusListItem(0);//获取第一个公交列表显示到map上
                    busline.getBusLine(fstLine);
                }
            }
        });
        function busSearch(){
            var busName = '地铁9号线';
            busline.getBusList(busName);
        }
        setTimeout(function(){
            busSearch();
        },1500);
}

//添加地铁线路
function add_line(pointlist,color,isbig){
    var point = [];//创建轨迹点
    for (var i = 0; i < pointlist.length; i++) {
        the_point = [pointlist[i]['point'][0], pointlist[i]['point'][1]]
        point.push(new BMapGL.Point(the_point[0],the_point[1]));
        //是否显示站点名标注
        if(pointlist[i]['xianshi']){
            add_dtz(map,the_point,pointlist[i]['name'],isbig)
        }
    }
    //创建线路
    var pl = new BMapGL.Polyline(point,{
        strokeWeight:isbig?10:6,
        strokeColor:color
    });
    //绘制线路
    map.addOverlay(pl)
}

// 添加楼盘房价
function add_fangjia(map,points,name,price,isbig=false){
    if(isbig==false){
        myicon = new BMapGL.Icon("/static/pic/fangjia_point.gif", new BMapGL.Size(20,30));
        //添加标记点
        var marker1 = new BMapGL.Marker(new BMapGL.Point(points[0],points[1]),{icon:myicon});
        map.addOverlay(marker1);
    }
    point = new BMapGL.Point(points[0],points[1])
    var opts = {
        position: point, // 指定文本标注所在的地理位置
        offset: new BMapGL.Size(isbig?-25:15, -20), // 设置文本偏移量
    };
    // 创建文本标注对象
    var label = new BMapGL.Label(name+price, opts);
    // 自定义文本标注样式
    label.setStyle({
        color: isbig?'#222':'#333',
        borderRadius: isbig ? '6px':'4px', //圆角边框幅度
        borderColor: '#6666cc',
        padding: isbig ? '2px':'1px',
        fontSize: isbig ? '14px':'8px',
        height: isbig ? '24px':'16px',
        lineHeight: isbig ? '20px': '12px',
        fontFamily: '微软雅黑',
        maxWidth:'200px'
    })
    map.addOverlay(label)
    return label
}
//地图显示门店
function map_add_stores(map){
    map.clearOverlays()
    $.get('get_cd_stores',function(data){
        all_data = eval(data)
        stores_list = []
        market_list = []    // 门店覆盖列表
        info_list = []      //窗口内容列表
        // 组装门店数据供地图展示使用
        for(item of all_data){
            store_label = []
            label_score = 0
            if(item.cd_label){
                //标签ID列表化
                label_list = item.cd_label.split(',')
                for(i=0;i<label_list.length;i++){
                    //获取标签名称
                    store_label.push(all_label[label_list[i]][0])
                    label_score += all_label[label_list[i]][1]
                }
            }
            market_list[item.id] = add_fangjia(map,[item.store_x,item.store_y],item.store_name,'<b style="color:#f00;">'+item.store_orders+'</b>',false)

            info_html = '面积：'+item.store_size+',门头：'+item.door_header+' 米，员工： '+item.store_waiters+'人<br />'
            info_html +='标签：<b>'+store_label.join(',')+'</b><br />打分：'+label_score

            info_list[item.id] = {'info_html':info_html,'info_opts':{width:250,height:100,title:item.store_name},'x':item.store_x,'y':item.store_y}
            market_list[item.id].addEventListener('click', function(i){
                return function(){
                    var infoWindow = new BMapGL.InfoWindow(info_list[i].info_html, info_list[i].info_opts);
                    map.openInfoWindow(infoWindow, new BMapGL.Point(info_list[i].x,info_list[i].y));
                }
            }(item.id))
        }
    });
}

//复制坐标地址到前贴吧
function copy_zb(objx,objy,x,y){
    objx.value = x
    objy.value = y
    document.execCommand("copy"); // 执行浏览器复制命令
}
//获取字典name的值,返回name列表
function get_name(arr){
    return_arr = []
    for(var item of arr){
        return_arr.push(item.name)
    }
    return return_arr
}
function array_sum(arr){
	totle = 0
	for(item of arr){
		totle += item
	}
	return totle
}
//平均值
function array_average(arr){
	return array_sum(arr)/arr.length
}