/*
This is a JavaScript file meant to be used globally, across the entire application, in every single page
*/
$(document).ready(function() {
    // Numeric only control handler
    // Force the user to only enter numeric numbers. Returns false when a key code doesn't match a number or any keycode given in extraKeys
    jQuery.fn.ForceNumericOnly =
    function(extraKeys = [])
    {
        return this.each(function()
        {
            $(this).keydown(function(e)
            {
                var key = e.charCode || e.keyCode || 0;
                // allow backspace, tab, delete, enter, arrows, numbers and keypad numbers ONLY
                // home, end, period
                return (
                    key == 8 || 
                    key == 9 ||
                    key == 13 ||
                    key == 46 ||
                    key == 110 ||
                    (key >= 35 && key <= 40) ||
                    (key >= 48 && key <= 57) ||
                    (extraKeys.includes(key)) ||
                    (key >= 96 && key <= 105)) ||
                    (key >= 112 && key <= 123);
            });
        });
    };
    
    $.fn.hasAttr = function(name) {  
        return this.attr(name) !== undefined;
    };


    function navtoggler() {
        if($(window).width() < 992) {
            $("#darkSwitch").parent('span').removeClass('nav-link');
        } else {
            $("#darkSwitch").parent('span').addClass('nav-link');
        }
    }
    navtoggler();
    
    $(document).on('focus', '.num_input', function() {
        $(this).ForceNumericOnly()
    });

    $('body').tooltip({
        selector: '[data-toggle=tooltip]'
    });

    $(window).resize(navtoggler);
});
