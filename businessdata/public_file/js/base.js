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
//function are_ok(name,str_code,id){
//    if(confirm('确定进货操作？'+name)){
//        get_change_result(str_code,id)
//    }
//}
//copy到剪贴板
function copy_text(txt)
{
    box = document.getElementById("smailbox")
    copyTocopy=document.getElementById("copyTocopy")
    copyTocopy.value = txt
    copyTocopy.select();
    document.execCommand("Copy"); // 执行浏览器复制命令
    box.innerText = 'OK'
    alert_box(box,1000)
}
//弹窗
function alert_box(box,time){
    box.style.display = 'block'
    setTimeout(function(){box.style.display = 'none';},time)
}