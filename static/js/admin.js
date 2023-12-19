$(document).ready(function(){
    $(document).on('click','.order-button',function(e){
        e.preventDefault();
        
        var selectedValue = $('#order-select').val();
        var token = $('input[name=csrfmiddlewaretoken]').val()

        console.log(selectedValue)
        $.ajax({
            url: '/custom_admin/order-chart-data',
            method: 'POST',
            data:{
                'selectedValue': selectedValue,
                csrfmiddlewaretoken: token
            },
            success: function(data) {
                const ctx = document.getElementById('myOrders');
        
                const labels = data.labels
                console.log(labels)
                
        
        
                
                myChart.data = {
                    labels: labels,
                    datasets: [{
                      label: 'Order By ' + data.name,
                      data: data.values,
                      backgroundColor: 'rgb(255, 99, 132)',
                      borderColor: 'rgb(255, 99, 132)',
                    }]
                  }
                  
                myChart.options = {
                    scales: {
                        y: {
                              
                              
                              ticks: {
                                stepSize: 1 // Set the step size of the y-axis ticks to 1
                              }
                            
                        }
                      }
                }
            
                myChart.update()
                
            }
          });
    })

    $(document).on('click','.user-button',function(e){
        e.preventDefault();
        
        var selectedValue = $('#user-select').val();
        var token = $('input[name=csrfmiddlewaretoken]').val()

        console.log(selectedValue)
        $.ajax({
            url: '/custom_admin/user-chart-data',
            method: 'POST',
            data:{
                'selectedValue': selectedValue,
                csrfmiddlewaretoken: token
            },
            success: function(data) {
                const ctx = document.getElementById('myOrders');
        
                const labels = data.labels
                console.log(labels)
                
        
        
                
                myUser.data = {
                    labels: labels,
                    datasets: [{
                      label: 'Order By ' + data.name,
                      data: data.values,
                      backgroundColor: 'rgb(255, 99, 132)',
                      borderColor: 'rgb(255, 99, 132)',
                    }]
                  }
                  
                myUser.options = {
                    scales: {
                        y: {
                              
                              
                              ticks: {
                                stepSize: 1 // Set the step size of the y-axis ticks to 1
                              }
                            
                        }
                      }
                }
            
                myUser.update()
                
            }
          });
    })
})
