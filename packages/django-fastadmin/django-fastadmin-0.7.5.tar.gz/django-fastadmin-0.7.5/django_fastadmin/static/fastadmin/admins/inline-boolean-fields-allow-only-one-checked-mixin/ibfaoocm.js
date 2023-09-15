;!(function($){
    $.fn.inline_boolean_fields_allow_only_one_checked = function(options){
        var config = $.extend({field_name_prefix: "inline-boolean-fields-allow-only-one-checked-mixin-"}, options);
        return $(this).each(function(index, element){
            var formset = $(element);
            formset.click(function(event){
                var target_parent = $(event.target).parent();
                if(target_parent){
                    $.each(formset.classes(), function(index, className){
                        if(className.startsWith(config.field_name_prefix)){
                            var field_name = "field-" + className.substring(config.field_name_prefix.length);
                            if(target_parent.hasClass(field_name)){
                                formset.find("." + field_name + " input").each(function(index, checkbox){
                                    if($(checkbox).attr("id") != $(event.target).attr("id")){
                                        $(checkbox).prop("checked", false);
                                    }
                                });
                            }
                        }
                    });
                }
            });
        });
    };

    $(document).ready(function(){
        $(".inline-boolean-fields-allow-only-one-checked-mixin").inline_boolean_fields_allow_only_one_checked();
    });

})(jQuery);
