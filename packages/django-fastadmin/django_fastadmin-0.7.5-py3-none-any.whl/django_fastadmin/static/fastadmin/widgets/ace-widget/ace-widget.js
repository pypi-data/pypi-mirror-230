;!(function($){
    $.fn.ace_editor = function(){
        return $(this).each(function(index, element){
            var source = $(element);
            var width = source.attr("width");
            var height = source.attr("height");
            var ace_options = $.parseJSON(source.attr("ace-widget-options"));
            var editor_wrapper = $("<div class='django-fastadmin-ace-widget-wrapper'></div>");
            var id = $.randomId(16, "AceWidget");
            editor_wrapper.insertAfter(source);
            editor_wrapper.attr("id", id);
            editor_wrapper.css("width", width);
            editor_wrapper.css("height", height);
            var editor = ace.edit(id, ace_options);
            editor.getSession().setValue(source.val());
            editor.getSession().on("change", function(){
                source.val(editor.getSession().getValue());
            });
            source.hide();
            editor_wrapper.show();
        });
    };

    $(document).ready(function(){
        $(".django-fastadmin-ace-widget").each(function(){
            var self = $(this);
            if(!self.parents(".form-row").hasClass("empty-form")){
                self.ace_editor();
            }
        });
    });

    $(document).on("formset:added", function(event, $row, formsetName){
        $row.find(".django-fastadmin-ace-widget").ace_editor();
    });
})(jQuery);