;!(function($){

    $.fn.cascade_select = function() {
        var wrapper = this;
        var level_1_selects = wrapper.children(".cascade-select-level-1");
        var level_2_selects = wrapper.children(".cascade-select-level-2");
        if(level_1_selects.length < 1){
            level_2_selects.show();
        }
        wrapper.children(".cascade-select-level-1").change(function(){
            var v1 = $(this).val();
            var s2 = wrapper.children(".cascade-select-level-2-" + v1);
            level_2_selects.hide();
            level_2_selects.removeAttr("name");
            s2.attr("name", "subclass_model");
            s2.show();
            s2.val("0");
        });
        wrapper.children(".cascade-select-level-2").change(function(){
            var option = $(this).children("option:selected");
            var description = option.attr("description");
            var image = option.attr("image");
            if(description){
                console.log(wrapper.parents("fieldset"));
                wrapper.parents("fieldset").find(".cascade-select-field-description").show();
                wrapper.parents("fieldset").find(".cascade-select-field-description-content").text(description);
            }else{
                wrapper.parents("fieldset").find(".cascade-select-field-description").hide();
                wrapper.parents("fieldset").find(".cascade-select-field-description-content").text("");
            }
            if(image){
                console.log(wrapper.parents("fieldset"));
                wrapper.parents("fieldset").find(".cascade-select-field-image").show();
                wrapper.parents("fieldset").find(".cascade-select-field-image-content").attr("src", image);
            }else{
                wrapper.parents("fieldset").find(".cascade-select-field-image").hide();
                wrapper.parents("fieldset").find(".cascade-select-field-image-content").attr("src", "");
            }
        });
    };

    $(document).ready(function(){
        $(".cascade-select").cascade_select();
    });
})(jQuery);
