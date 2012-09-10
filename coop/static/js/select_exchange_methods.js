function pick(arg, def) {
    return (typeof arg == 'undefined' ? def : arg);
}

function show_target_methods(select, reset) {
    reset = pick(reset, false); // si arg reset pas passé = false
    etype = select.children("option:selected").val();
    //console.log(etype);
    methods_group = select.parent(".controls").parent(".control-group").next(".control-group");
    methods = methods_group.find("ul.methods").children("li");
    //console.log(methods);
    if (methods_group.is(":visible")) {
        methods_group.hide();
        methods.hide();
        if (reset) {
            methods.find("label input").attr('checked', false);
        }
    }

    targets = methods.children("label.met" + etype);
    if (targets.length > 0) {
        methods_group.slideDown();
        targets.parent().show();
    }

}

(function($) {

    //console.log($.fn.jquery) // which jquery are we using ?
    $(function() {
        $("select[name$='-etype']").each(function() {
            show_target_methods($(this));

        });


        $("select[name$='-etype']").bind("change", function(e) {
            //console.log($(this));
            show_target_methods($(this), true);
        });

    });

})((typeof window.jQuery == 'undefined' && typeof window.django != 'undefined') ? django.jQuery : jQuery);

// si jQuery 1.7 est pas encore chargé et que django.jQuery l'est, il prendra celui de django admin