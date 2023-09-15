;!(function($){
    $(document).ready(function(){
        var show_value = function(field){
            var value = field.find(".value");
            var view_icon = field.find(".view i");
            var view_label = field.find(".view span");
            value.attr("value", value.attr("data"));
            view_icon.removeClass("fa-eye");
            view_icon.addClass("fa-eye-slash");
            view_label.text("隐藏");
        };
        var hide_value = function(field){
            var value = field.find(".value");
            var view_icon = field.find(".view i");
            var view_label = field.find(".view span");
            value.attr("value", "******");
            view_icon.removeClass("fa-eye-slash");
            view_icon.addClass("fa-eye");
            view_label.text("查看");
        };

        $(".editable-password-field .view").click(function(){
            if($(this).hasClass("disabled")){
                return false;
            }
            var field = $(this).parents(".editable-password-field");
            var value = field.children(".value");
            if(value.attr("value") == value.attr("data")){
                hide_value(field);
            }else{
                show_value(field);
            }
            return false;
        });

        $(".editable-password-field .change").click(function(){
            var field = $(this).parents(".editable-password-field");
            var value = field.children(".value");
            var view = field.children(".view");
            show_value(field);
            value.removeClass("readonly");
            value.removeAttr("readonly");
            value.focus();
            value.select();
            view.addClass("disabled");
            return false;
        });

        $(".editable-password-field").each(function(){
            if($(this).hasClass("add-flag")){
                $(this).find(".reset").click();
            }
        });
    });
})((jQuery);