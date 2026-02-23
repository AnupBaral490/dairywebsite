$('.plus-cart').click(function () {
    var id = $(this).attr("cart_id").toString();

    // find quantity span in the SAME cart row
    var quantitySpan = $(this).closest('.row').find('.quantity');

    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            cart_id: id
        },
        success: function (data) {
            quantitySpan.text(data.quantity);
            $('#amount').text("Rs." + data.amount);
            $('#shippingamount').text("Rs." + data.shipping);
            $('#totalamount').text("Rs." + data.totalamount);
        }
    });
});

$('.minus-cart').click(function () {
    var id = $(this).attr("cart_id").toString();

    // find quantity span in same cart row
    var quantitySpan = $(this).closest('.row').find('.quantity');

    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            cart_id: id
        },
        success: function (data) {
            quantitySpan.text(data.quantity);
            $('#amount').text("Rs." + data.amount);
            $('#shippingamount').text("Rs." + data.shipping);
            $('#totalamount').text("Rs." + data.totalamount);
        }
    });
});

$('.remove-cart').click(function () {
    var id = $(this).attr("cart_id").toString();
    var cartRow = $(this).closest('.row');

    $.ajax({
        type: "GET",
        url: "/removecart",
        data: {
            cart_id: id
        },
        success: function (data) {
            $('#amount').text("Rs." + data.amount);
            $('#shippingamount').text("Rs." + data.shipping);
            $('#totalamount').text("Rs." + data.totalamount);
            cartRow.remove();
        }
    });
});


$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.reload();
        }
    })
})

$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.reload();
        }
    })
})

$('.variant-option').on('change', function(){
    var discounted = $(this).data('discounted');
    var selling = $(this).data('selling');
    $('#productDiscounted').text(`Rs.${discounted}/-`);
    $('#productSelling').text(`Rs. ${selling}/-`);
    $('#variantInput').val($(this).val());
});