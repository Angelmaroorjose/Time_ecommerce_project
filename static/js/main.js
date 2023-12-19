
let btns = document.querySelectorAll(".add-cart")
console.log(btns)
btns.forEach(btn => {
    btn.addEventListener("click", addtoCart)
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }




if (user == 'AnonymousUser'){
var cart = JSON.parse(getCookie('cart'))
if(cart == undefined){
    cart = {}
}

document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

}

function addtoCart(e){

    let product_id = e.target.value
    let data = {id:product_id}
    var token = $('input[name=csrfmiddlewaretoken]').val()
    var totalQty = $('#'+product_id).val()
    console.log(totalQty)

    if(user == 'AnonymousUser'){
        addCOokieItem(product_id, totalQty)
        return
    }else{

    let url = "/shop/cart/add_to_cart"
    fetch(url, {
        method: "POST",
        headers: {"Content-Type":"application/json","X-CSRFToken":token},
        body: JSON.stringify(data)
    })
    .then(res=>res.json())
    .then(data =>{
        if(data.status){
            alertify.error(data.status)
        }
        else{
        document.getElementById('lblCartCounts').innerHTML = data.num_of_items
        document.getElementById('lblCartCount').innerHTML = data.num_of_items
        
        alertify.success(data.msg)
        console.log(data.num_of_items)
        }
    })
    .catch(error =>{
        console.log(error)

    })
    }

}

function addCOokieItem(productId, totalQty){
    if(totalQty == 0){
        alertify.error("Out of Stock")
        return
    }
    if (cart[productId] == undefined){
        
        cart[productId] = {'quantity': 1}
    }else{
        if(totalQty > cart[productId]['quantity']){
        cart[productId]['quantity'] += 1
        }else{
            alertify.error("Out of Stock")
        }
    }
    console.log(cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    
}

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
const csrftoken = getToken('csrftoken')

function addToCart(proId) {
  var elem = document.getElementById('prod_qty')
 
  var proQty = elem ? elem.value : null;
  var totalQty = document.getElementById('product_quantity').value
  console.log(totalQty)
    if(proQty == null){
      alertify.error("Out of Stock")
      return false
    }
    
    if (user == 'AnonymousUser'){
        console.log("In anonymous user")
      var cart = JSON.parse(getCookie('cart'))
      if(cart == undefined){
          cart = {}
      }
      document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
      addCookieItem(proId, proQty, totalQty)
      }
      else{

    var token = $('input[name=csrfmiddlewaretoken]').val()
    $.ajax({
        method: "POST",
        url: "/add-to-cart",
        data: {
            product_id: proId,
            product_qty: proQty,
            csrfmiddlewaretoken: csrftoken
        },
        dataType: "json",
        success: function(response){
            if (response.failure){
              alertify.error(response.failure)
            }
            else{
            alertify.success(response.status)
            $('.left_items').load(location.href + " .left_items")
            if(response.num_of_items){
                console.log("in num of items")
            $('#lblCartCount').html(response.num_of_items)
            }
            }
           console.log(response)
        }
    })
  }
}

function addCookieItem(productId, proQty, totalQty){
 
  console.log(proQty)
  if (cart[productId] == undefined){
      cart[productId] = {'quantity': parseInt(proQty)}
  }else{
      cart[productId]['quantity'] += parseInt(proQty)
  }
  if(cart[productId]['quantity'] > totalQty){
      cart[productId]['quantity'] = parseInt(totalQty)
  }
  console.log(cart)
  document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
  
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

$(document).ready(function() {
    $('.addToWishlist').click(function (e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('input[name = product_id]').val();
        var token = $('input[name=csrfmiddlewaretoken]').val()
        if(product_id == undefined){
            product_id = $('.home-page-product-id').val()
        
        }
        console.log(product_id)
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
                    $('.address-change').load(location.href + " .address-changes" )
                    
                    
                   
                }
               
            }
        })
    
    })


    $(".increment_btn").click(function(e){
        e.preventDefault();

        
        var productId = $(".prod_id").val()
        
        var totalQuantity = $(".product-page-quantity").val()
        var price = $(this).closest(".product_data").find('#selling_price').text()
        var inc_value =  $(this).closest(".product_data").find('.qty-input').val();
        var value = parseInt(inc_value,10);
        console.log(value)
        console.log(totalQuantity)

        value = isNaN(value) ? 0: value;
        if(totalQuantity > value){
            value++
            
      
            var total = value * price
            $(this).closest(".product_data").find('.qty-input').val(value);
            $(this).closest(".product_data").find('#item-total').text("$"+total);
            
            
        }else if (value >= totalQuantity){
            alertify.error("Out of Stock")
        }

    })

    $(".decrement_btn").click(function(e){
        e.preventDefault();

        
        var productId = $(".prod_id").val()
        var price = $(this).closest(".product_data").find('#selling_price').text()
        var dec_value =  $(this).closest(".product_data").find('.qty-input').val();
        var value = parseInt(dec_value,10);
        value = isNaN(value) ? 0: value;
        if(value > 1){
            value--
            
           
            var total = value * price
            $(this).closest(".product_data").find('.qty-input').val(value);
            $(this).closest(".product_data").find('#item-total').text("$"+total);
           
           
        }
        

    })
})