;!(function($){
    $(document).ready(function() {
        var fixHeight = function(element){
            var outerHeight = $(element).outerHeight();
            var scrollHeight = element.scrollHeight;
            if(outerHeight < scrollHeight){
                $(element).height(scrollHeight);
            }
        };
        $("textarea").each(function(index, element){
            fixHeight(element);
        });
        $("textarea").keyup(function(e) {
            var element = this;
            fixHeight(element);
        });
    });
})(jQuery);
