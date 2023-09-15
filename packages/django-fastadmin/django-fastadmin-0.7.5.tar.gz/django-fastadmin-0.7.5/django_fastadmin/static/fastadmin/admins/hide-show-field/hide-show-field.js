;!(function($){
    $(document).ready(function(){
        $(".hide-show-field .view").click(function(){
            var value = $(this).prev(".value");
            var icon = $(this).children("i");
            var label = $(this).children("span");
            if(value.attr("value") == value.attr("data")){
                // hide
                value.attr("value", "******");
                icon.removeClass("fa-eye-slash");
                icon.addClass("fa-eye");
                label.text("查看");
            }else{
                // show
                value.attr("value", value.attr("data"));
                icon.removeClass("fa-eye");
                icon.addClass("fa-eye-slash");
                label.text("隐藏");
            }
            
            return false;
        });
    });
})((jQuery);
