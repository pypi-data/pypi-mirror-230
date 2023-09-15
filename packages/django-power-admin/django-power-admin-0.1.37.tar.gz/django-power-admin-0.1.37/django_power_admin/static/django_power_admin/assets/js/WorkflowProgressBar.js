; (function ($) {

    $.fn.WorkflowProgressBar = function (options) {
        var settings = $.extend({
            icons: {
                finished: "fa fa-check-circle",
                doing: "fa fa-clock",
                todo: "fa fa-info-circle",
                canceled: "fa fa-minus-circle"
            }
        }, options);

        $(this).each(function (index, item) {
            var i;
            var wrapper = $(item);
            var bar = $("<ol class=\"worflow-progress-bar\"></ol>");
            bar.appendTo(wrapper);
            for (i = 0; i < settings.nodes.length; i++) {
                var node_config = settings.nodes[i];
                var node = $("<li><p class=\"workflow-progress-title\"><i></i><span class=\"workflow-progress-title-text\">&nbsp;</span></p><p class=\"workflow-progress-content\">&nbsp;</p></li>");
                var node_tail = $("<span class=\"workflow-progress-title-bar\"></span>");
                node.appendTo(bar);
                node.addClass("worflow-progress-" + node_config.status);
                node.find("i").addClass(settings.icons[node_config.status]);
                node.find(".workflow-progress-title-text").text(node_config.title);
                if (i !== settings.nodes.length - 1) {
                    node_tail.appendTo(node.find(".workflow-progress-title"));
                }
                if (node_config.content) {
                    node.find(".workflow-progress-content").text(node_config.content);
                }
            }
        });
        return $(this);
    };

})(jQuery);