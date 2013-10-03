
(function($) {

    function hide_person_filter(value){
        console.log('function...');
        console.log(value == 3);
            // if(value === "3"){
            //     console.log('org only');
            //     $("#id_person_category").val("");
            //     $("#id_person_category").parent().parent("div.controls").hide();
            // }else{
            //     $("#id_person_category").parent().parent("div.controls").show();
            // }
    }

    hide_person_filter($("#id_subscription_option").val());

    $("#id_subscription_option").change(function() {
        hide_person_filter($(this).val());
    });

})((typeof window.jQuery == 'undefined' && typeof window.django != 'undefined') ? django.jQuery : jQuery);