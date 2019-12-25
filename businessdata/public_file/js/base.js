// 页面跳转
function gotolaction(value){
    window.location.href=value;
}
//确认及跳转
function are_ok(name,str_code){
    if(confirm('确定进货操作？'+name)){
        gotolaction(str_code)
    }
}