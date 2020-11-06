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
    if(confirm('确定进货操作？'+name)){
        get_change_result(str_code,id)
    }
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
            average_arr.push(arr[i])
       }else{
            average_arr.push(array_sum(arr,i-30,i)/30)
       }
    }
    return average_arr;
}
//arr=[1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4]
//alert(array_average(arr))