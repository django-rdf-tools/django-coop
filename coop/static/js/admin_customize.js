(function($) {
    
    if($('ul.groupbox-list').length > 0 && typeof django.jQuery.fn.columnize == 'function'){
        $('.groupbox ul').columnize({columns:3});
    }

    
    // Only for stacked inlines
    $('div.inline-group div.inline-related:not(.tabular):not(.empty-form)').each(function() {
        fs = $(this).find('fieldset')
        h3 = $(this).find('h3:first')

        // Don't collapse if fieldset contains errors
        if (fs.find('div').hasClass('errors'))
            fs.addClass('stacked_collapse');
        else
            fs.addClass('stacked_collapse collapsed');
        
        // Add toggle link
        h3.prepend('<a class="stacked_collapse-toggle" href="#">(' + gettext('Show') + ')</a> ');
        h3.find('a.stacked_collapse-toggle').bind("click", function(){
            fs = $(this).parent('h3').next('fieldset');
            if (!fs.hasClass('collapsed'))
            {
                fs.addClass('collapsed');
                $(this).html('(' + gettext('Show') + ')');
            }
            else
            {
                fs.removeClass('collapsed');
                $(this).html('(' + gettext('Hide') + ')');
            }
        }).removeAttr('href').css('cursor', 'pointer');
    });
})(django.jQuery);
