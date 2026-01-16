$('.plus-cart').click(function () {
    var id = $(this).attr("pid").toString();

    // find quantity span in the SAME cart row
    var quantitySpan = $(this).closest('.row').find('.quantity');

    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            prod_id: id
        },
        success: function (data) {
            quantitySpan.text(data.quantity);
            $('#amount').text("Rs." + data.amount);
            $('#totalamount').text("Rs." + data.totalamount);
        }
    });
});

$('.minus-cart').click(function () {
    var id = $(this).attr("pid").toString();

    // find quantity span in same cart row
    var quantitySpan = $(this).closest('.row').find('.quantity');

    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            prod_id: id
        },
        success: function (data) {
            quantitySpan.text(data.quantity);
            $('#amount').text("Rs." + data.amount);
            $('#totalamount').text("Rs." + data.totalamount);
        }
    });
});

$('.remove-cart').click(function () {
    var id = $(this).attr("pid").toString();
    var cartRow = $(this).closest('.row');

    $.ajax({
        type: "GET",
        url: "/removecart",
        data: {
            prod_id: id
        },
        success: function (data) {
            $('#amount').text("Rs." + data.amount);
            $('#totalamount').text("Rs." + data.totalamount);
            cartRow.remove();
        }
    });
});
