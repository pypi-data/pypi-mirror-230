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

        $(".reset-to-random-password-field .view").click(function(){
            if($(this).hasClass("disabled")){
                return false;
            }
            var field = $(this).parents(".reset-to-random-password-field");
            var value = field.children(".value");
            if(value.attr("value") == value.attr("data")){
                hide_value(field);
            }else{
                show_value(field);
            }
            return false;
        });

        $(".reset-to-random-password-field .reset").click(function(){
            var field = $(this).parents(".reset-to-random-password-field");
            var value = field.children(".value");
            var view = field.children(".view");
            var url = value.attr("url");
            var params = JSON.parse(value.attr("params"));
            $.ajax({
                method: "GET",
                dataType: "json",
                url: url,
                data: params,
                success: function(data){
                    if(data && data.success){
                        value.attr("data", data.result);
                        show_value(field);
                        view.addClass("disabled");
                        value.attr("reseted", "true");
                        value.attr("name", value.attr("field-name"));
                    }else{
                        if(data && data.error && data.error.message){
                            alert(data.error.message);
                        }else{
                            alert("刷新随机密码遇到服务器错误，请重试或联系管理员！")
                        }
                    }
                },
                error: function(){
                    alert("刷新随机密码遇到网络错误，请重试或联系管理员！");
                }
            });
            return false;
        });

        $(".reset-to-random-password-field").each(function(){
            if($(this).hasClass("add-flag")){
                $(this).find(".reset").click();
            }
        });
    });
})(jQuery);
