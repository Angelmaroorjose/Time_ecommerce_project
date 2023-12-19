$(document).ready(function(){

    $('.payWithRazorPay').click(function (e){
        e.preventDefault();

        const csrftoken = getToken('csrftoken')

        // swal({
        //     title: "Are you sure?",
        //     text: "Your will not be able to recover this imaginary file!",
        //     type: "warning",
        //     showCancelButton: true,
        //     confirmButtonColor: "#DD6B55",
        //     confirmButtonText: "Yes, delete it!",
        //     closeOnConfirm: true,
        //     closeOnCancel: true,
            
        // },)
        // return false

        $.ajax({
            method: "GET", 
            url: "/shop/proceed-to-pay",
            success: function(response){
                console.log(response)
                var options = {
                    "key": "rzp_test_w7NKZWV87Rx7B8", // Enter the Key ID generated from the Dashboard
                    "amount": response.total_price * 100 * 80, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                    "currency": "INR",
                    "name": "Time Zone", //your business name
                    "description": "Thank You for Buying with us",
                    "image": "https://example.com/your_logo",
                    "handler": function(responseb){
                      
                        data = {
                            "payment_mode": "RazorPay",
                            "payment_id": responseb.razorpay_payment_id,
                            csrfmiddlewaretoken: csrftoken
                        }
                        $.ajax({
                            method: "POST",
                            url: '/shop/razor_pay',
                            data: data,
                            success: function(responsec){
                                swal("Congratulations!", responsec.status,"success").then((value) =>{
                                    window.location.href = "/shop/confirmation"
                                })
                                
                            }
                        })
                    },
                    // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                    // "callback_url": "https://eneqd3r9zrjok.x.pipedream.net/",
                    "prefill": {
                        "name": response.user, //your customer's name
                        "contact": "",
                    },
                    
                    "theme": {
                        "color": "#3399cc"
                    }
                };
                var rzp1 = new Razorpay(options);
                rzp1.open()
            }
        })

        
    })
})

function getToken(name){
    var cookieValue = null;
    if (document.cookie && document.cookie !== ''){
        var cookies = document.cookie.split(';');
        for(var i = 0;i < cookies.length;i++ ){
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length +1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

