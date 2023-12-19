$(document).ready(function(){
    $(".sales_submit").click(function(e){
        e.preventDefault();


        var start_time = $("#starting-time").val()
        var end_time = $('#ending-time').val()
        var token = $('input[name=csrfmiddlewaretoken]').val()
        console.log(end_time)
        console.log(start_time)
        console.log(token)
        if(start_time == '' || end_time== ""){
            alertify.error("Provide the time")
            return false
        }
        $.ajax({
            method: "POST",
            url: "/custom_admin/sales-report",
            data: {
                "starting_date": start_time,
                "ending_date": end_time,
                
                csrfmiddlewaretoken: token
            },
            dataType: "json",
            success: function(response){
                console.log(response)
                $(".order-sales").html(response.status)
                
            }
        })
    })



    $(".sales_report_pdf").click(function(e){
        e.preventDefault();


        var start_time = $("#starting-time").val()
        var end_time = $('#ending-time').val()
        var token = $('input[name=csrfmiddlewaretoken]').val()
        console.log(end_time)
        console.log(start_time)
        console.log(token)

        $.ajax({
            method: "POST",
            url: "/custom_admin/sales_report_pdf",
            data: {
                "starting_date": start_time,
                "ending_date": end_time,
                
                csrfmiddlewaretoken: token
            },
            dataType: "json",
            success: function(response){
                console.log(response)
               
                
            }
        }) 
    })
})
