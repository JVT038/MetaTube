// Numeric only control handler
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
$(document).on('focus', '.num_input', function() {
    $(this).ForceNumericOnly()
});