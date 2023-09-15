;!(function($){
    $.fn.title_to_code = function(){
        return $(this).each(function(index, element){
            var input = $(element);
            var options = $.parseJSON(input.attr("django-fastadmin-title-to-code-options"));
            var from_field_name = options.from;
            var from_field = input.django_admin_get_sibling_field(from_field_name).find("input,textarea,select,file");
            var get_code_timeout_id = 0;
            var get_code = function(){
                var new_value = from_field.val();
                $.ajax({
                    method: "GET",
                    url: options.api_title_to_code_url,
                    dataType: "json",
                    data: {
                        title: new_value,
                    },
                    success: function(data){
                        input.val(data.result);
                    }
                })
            };
            var on_from_field_update = function(){
                if(input.attr("django-fastadmin-title-to-code-disabled") != "true"){
                    if(get_code_timeout_id != 0){
                        window.clearTimeout(get_code_timeout_id);
                        get_code_timeout_id = 0;
                    }
                    get_code_timeout_id = setTimeout(get_code, options.api_request_delay);
                }
            };
            from_field.keyup(on_from_field_update);
            from_field.change(on_from_field_update);
        });
    };

    $(document).ready(function(){
        $(".django-fastadmin-title-to-code").each(function(){
            var self = $(this);
            if(!self.parents(".form-row").hasClass("empty-form")){
                self.title_to_code();
            }
        });
    });

    $(document).on("formset:added", function(event, $row, formsetName){
        $row.find(".django-fastadmin-title-to-code").title_to_code();
    });
})(jQuery);
