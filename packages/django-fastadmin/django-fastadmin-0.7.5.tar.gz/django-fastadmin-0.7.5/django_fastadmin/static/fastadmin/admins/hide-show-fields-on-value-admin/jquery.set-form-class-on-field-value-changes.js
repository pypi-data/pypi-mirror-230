;(function($){

    $.fn.set_form_class_on_field_value_changes = function(prefix){
        return this.each(function(index, element){
            var target_field = $(element);
            var target_field_name = target_field.attr("name");
            var form = target_field.parents("form");
            var last_class_name = null;
            console.log(prefix, target_field_name, target_field, form);
            target_field.change(function(){
                console.log("last_class_name=", last_class_name);
                if(last_class_name && form.hasClass(last_class_name)){
                    form.removeClass(last_class_name);
                }
                last_class_name = prefix + target_field_name + "-" + target_field.val();
                form.addClass(last_class_name);
                console.log("new_class_name=", last_class_name);
            });
            target_field.change();
        });
    };

})(jQuery);
