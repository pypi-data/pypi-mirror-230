;(function($){
    $(document).ready(function(){
        $(".form-row .vCheckboxLabel").each(function(){
            var box = $(this);
            box.insertBefore(box.prev());
            box.removeClass("vCheckboxLabel");
            box.addClass("vCheckboxLabelDeleted");
            box.parents(".checkbox-row").removeClass("checkbox-row");
        });
    });
})(jQuery);
