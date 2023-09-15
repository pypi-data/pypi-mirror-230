;!(function($){



    $.fn.django_admin_get_sibling_field = function(sibling_field_name){
        var parent = $(this).parent();
        while(parent){
            var classes = parent.classes();
            var i;
            for(i=0; i<classes.length; i++){
                var klass = classes[i];
                if(klass.startsWith("field-")){
                    var target = parent.siblings(".field-" + sibling_field_name);
                    return target;
                }
            }
            parent = parent.parent();
        }
    };

})(jQuery);
