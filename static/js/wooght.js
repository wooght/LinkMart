function set_pie(all_data, chart_name){
            var myChart = echarts.init(document.getElementById('main_pie'));
            classify_data = []
            var i=0;
            for(key in all_data){
                if(all_data[key][1]<1){continue;}
                classify_data.push({value:all_data[key][1],name:all_data[key][0]})
            }
            option = {
                backgroundColor: '#2c343c',
                title: {
                    text: chart_name,
                    left: 'center',
                    top: 20,
                    textStyle: {
                        color: '#ccc'
                    }
                },

                tooltip : {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                series:[
                    {
                        name:'',
                        type:'pie',
                        radius : '75%',
                        center: ['50%', '50%'],
                        data:classify_data.sort(function (a, b) { return a.value - b.value; }),
                        roseType: 'radius',
                        label: {
                            normal: {
                                textStyle: {
                                    color: 'rgba(255, 255, 255, 0.3)'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                lineStyle: {
                                    color: 'rgba(255, 255, 255, 0.3)'
                                },
                                smooth: 0.2,
                                length: 10,
                                length2: 20
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: '#c23531',
                                shadowBlur: 200,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        },

                        animationType: 'scale',
                        animationEasing: 'elasticOut',
                        animationDelay: function (idx) {
                            return Math.random() * 200;
                        }
                    }
                ]
            };
            myChart.setOption(option);
        }