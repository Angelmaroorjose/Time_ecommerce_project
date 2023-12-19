$(document).ready(function(){
    $(".ajaxLoader").hide()
    
    $(".filter-checkbox,#priceFilterBtn").on('click', function(){
        var _filterObj = {}
        var _minPrice = $('#maxPrice').attr('min')
        var _maxPrice = $('#maxPrice').val()
        if (_minPrice == _maxPrice){
            _maxPrice = $('#maxPrice').attr('max')
        }
        _filterObj.minPrice = _minPrice
        _filterObj.maxPrice = _maxPrice

        console.log(_minPrice, _maxPrice)

        $(".filter-checkbox").each(function(index, ele){
            var _filterVal = $(this).val()
            var _fitlerKey = $(this).data('filter')
            _filterObj[_fitlerKey] = Array.from(document.querySelectorAll('input[data-filter='+_fitlerKey+']:checked')).map(function(el){
                return el.value
            })
        })
        
        //run ajax
        $.ajax({
            url: 'filter-data',
            data: _filterObj,
            dataType: 'json',
            beforeSend:function(){
                $(".ajaxLoader").show();
            },
            success:function(res){
                console.log(res)
                $("#filteredProducts").html(res.data)
                $(".ajaxLoader").hide()
                $('#pagination-product').remove();
                
                
            }
        })
    })

    $('#search').on('keyup', function () {
        var query = $(this).val();
        console.log(query)
        if (query.length < 1) {
            $('#suggestions').empty();
            console.log("HHH")
            return;
        }
        $.getJSON('/shop/search/suggestions/', {q: query}, function (data) {
            $('#suggestions').empty();
            data.suggestions.forEach(function (suggestion) {
                var li = $('<li>').addClass('suggestion-item').text(suggestion);
                li.click(function() {
                    $('#search').val(suggestion);
                    $('#suggestions').empty();
                });
                $('#suggestions').append(li);
            });
        });
    });

});
