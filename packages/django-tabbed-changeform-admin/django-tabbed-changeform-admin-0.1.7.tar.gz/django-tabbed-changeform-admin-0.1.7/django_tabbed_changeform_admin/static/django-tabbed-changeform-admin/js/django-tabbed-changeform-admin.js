;!(function($){
    $(document).ready(function(){
        $(".django-tabbed-changeform-admin-content").each(function(index, element){
            var content_wrapper = $(this);
            var form = $(this).parents("form");
            var content_classes = $(this).attr("data-content-classes").trim();
            $.each(content_classes.split(" "), function(index, value){
                var fieldset = form.find("." + value);
                if(fieldset.length > 0){
                    var inlinegroup = fieldset.parents(".inline-group");
                    if(inlinegroup.length > 0){
                        inlinegroup.appendTo(content_wrapper);
                    }else{
                        fieldset.appendTo(content_wrapper);
                    }
                }
            });
        });
        $(".django-tabbed-changeform-admin-tabs").tabs({
        });
    });
})(jQuery);
