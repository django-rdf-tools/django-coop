function pick(arg, def) {
   return (typeof arg == 'undefined' ? def : arg);
}

function show_target_methods(select,reset){
    reset = pick(reset, false);
    etype = select.children("option:selected").val();
    //console.log(etype);
    methods_group = select.parent(".controls").parent(".control-group").next(".control-group");
    methods = methods_group.find("ul.methods").children("li");
    //console.log(methods);
    
    //if(methods_group.is(":visible")){   
    methods_group.hide();
    methods.hide();
    if(reset){
        methods.find("label input").attr('checked', false);
    }

    targets = methods.children("label.met"+etype);
    if(targets.length > 0){
        methods_group.slideDown();
        targets.parent().show();
    }
}


$(function(){
    $(document).ready(function(){
        $("select[name$='-etype']").each(function(){
            show_target_methods($(this));
        });
    });
    $("select[name$='-etype']").bind("change",function(e){
        show_target_methods($(this),true);
    });

});