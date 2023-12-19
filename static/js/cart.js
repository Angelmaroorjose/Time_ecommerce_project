


$(document).ready(function() {
    $(".increment-btn").click(function(e){
        e.preventDefault();

        
        
        var productId = $(this).closest(".product_data").find(".guest-user-product-id").val()
        
        var totalQuantity = $(this).closest(".product_data").find(".guest-user-product-quantity").val()
        var price = $(this).closest(".product_data").find('#selling_price').text()
        var inc_value =  $(this).closest(".product_data").find('.qty-input').val();
        var value = parseInt(inc_value,10);


        value = isNaN(value) ? 0: value;
        if(totalQuantity > value){
            value++
            console.log("HHHHhh")
            if(user == 'AnonymousUser'){
            cart[productId]["quantity"] = parseInt(value)
            document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
          
            }
            var total = value * price
            $(this).closest(".product_data").find('.qty-input').val(value);
            $(this).closest(".product_data").find('#item-total').text("$"+total);
            
            
            
            console.log(totalQuantity)
        }else if (value >= totalQuantity){
            alertify.error("Out of Stock")
        }

    })

    $(".decrement-btn").click(function(e){
        e.preventDefault();

        
        var productId = $(this).closest(".product_data").find(".guest-user-product-id").val()
        var price = $(this).closest(".product_data").find('#selling_price').text()
        var dec_value =  $(this).closest(".product_data").find('.qty-input').val();
        var value = parseInt(dec_value,10);
        value = isNaN(value) ? 0: value;
       
        if(value > 1){
            value--
            
            if(user == 'AnonymousUser'){
            cart[productId]["quantity"] = parseInt(value)
            document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
            console.log(cart)
            }
            var total = value * price
            $(this).closest(".product_data").find('.qty-input').val(value);
            $(this).closest(".product_data").find('#item-total').text("$"+total);
           
           
        }
        

    })

    

    $(".changeQuantity").click(function(e){
        e.preventDefault();

        var totalQuantity = $(this).closest(".product_data").find(".guest-user-product-quantity").val()
        var product_id = $(this).closest('.product_data').find('input[name = product_id]').val();
        var product_qty = $(this).closest('.product_data').find('.qty-input').val();
        var token = $('input[name=csrfmiddlewaretoken]').val()
        var action = $(this).data('action');
        
        if(user == 'AnonymousUser'){
            cart[product_id]["quantity"] = parseInt(product_qty)
            document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
            console.log(cart)
            return
            }
        console.log(action)
        $.ajax({
            method: "POST",
            url: "/shop/cart/update-cart",
            data: {
                "product_id": product_id,
                "product_qty": product_qty,
                "action": action,
                csrfmiddlewaretoken: token
            },
            dataType: "json",
            success: function(response){
                if(response.value){
                $('#lblCartCount').html(response.num_of_items)
                }
                console.log(response)
                $('.order-cart-total').load(location.href + " .order-cart-total")
                $('.guest-user-product-quantity').val(response.product_quantity)
                console.log(totalQuantity)
                
            }
        })

    })

    $(document).on('click','.delete-cart-item',function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('input[name = product_id]').val();
        
        var token = $('input[name=csrfmiddlewaretoken]').val()

        console.log(token)
        console.log(product_id);
        swal({
            title: "Are you sure?",
            text: "Once deleted, you will not be able to recover this ",
            icon: "warning",
            buttons: true,
            dangerMode: true,
          })
          .then((willDelete) => {
            if (willDelete) {
                if(user == "AnonymousUser"){
                    delete cart[product_id]
                    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
                    $('.cart-data').load(location.href + " .cart-data" )
                    swal("Poof! Your product has been removed from the cart!", {
                        icon: "success",
                      });
                    console.log(cart)
                    return
                }
                $.ajax({
                    method: "POST",
                    url: "/shop/cart/delete_cart",
                    data: {
                        "product_id": product_id,
                        
                        csrfmiddlewaretoken: token
                    },
                   
                    success: function(response){
                        console.log(response)
                        $('.cart-lg-logo').html(response.num_of_items)
                        alertify.success(response.status)
                        $('.cart-data').load(location.href + " .cart-data" )
                        swal("Poof! Your product has been removed from the cart!", {
                            icon: "success",
                          });
                    }
                })
              
            } else {
              
              return false
            }
          });
        

    })

    $('.addToWishlist').click(function (e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('input[name = product_id]').val();
        var token = $('input[name=csrfmiddlewaretoken]').val()
        
        $.ajax({
            method: "POST",
            url: "/shop/add-to-wishlist",
            data: {
                "product_id": product_id,
                
                csrfmiddlewaretoken: token
            },
            

            success: function(response){
                console.log(response)
                alertify.success(response.status)
               
            }
        })
    })

    $(document).on('click','.delete-wishlist-item',function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('input[name = product_id]').val();
        
        var token = $('input[name=csrfmiddlewaretoken]').val()

        console.log(token)
        console.log(product_id);
      
        $.ajax({
            method: "POST",
            url: "/shop/cart/delete_wishlist",
            data: {
                "product_id": product_id,
                
                csrfmiddlewaretoken: token
            },
           
            success: function(response){
                console.log(response)
                $('.wishlist-data').load(location.href + " .wishlist-data" )
            }
        })

    })

    $(document).on('click','.activate-address',function(e){
        e.preventDefault();
    
        var _aid = $(this).attr('data-address')
        var _vm = $(this);
        
     
      
        $.ajax({
        
            url: "/activate-address",
            data: {
                
                "id": _aid,
            },
            dataType : 'json',
            beforeSend:function(){
                _vm.attr('disabled', true)
            },
           
            success: function(response){
                if (response.bool == true){
                    $('.address-change').load(location.href + " .address-change" )
                    
                    
                   
                }
               
            }
        })
    
    })

  
})


   

