; (function ($) {
  $.fn.PopupConfigTable = function () {
    $.each($(this), function () {
      var wrapper = $(this);
      var form_row = wrapper.parents(".form-row");
      if(form_row.hasClass("empty-form")){
        return;
      }
      var popup_config_table_config_items = wrapper.find(".django_power_admin_widgets_popup_config_table_item");
      var popup_config_table_textarea = wrapper.children(".django_power_admin_widgets_popup_config_table_textarea");
      var popup_config_table_dialog = wrapper.children(".django_power_admin_widgets_popup_config_table_popup");
      var popup_config_table_btn = wrapper.children(".popup_config_table_more_configs");
      var popup_config_table_config = JSON.parse(popup_config_table_textarea.attr("popup_config_table_config"));
      var popup_config_table_load_values = function () {
        var values = JSON.parse(popup_config_table_textarea.val() || "{}");
        popup_config_table_config_items.each(function (index, item) {
          var key = $(item).children(".django_power_admin_widgets_popup_config_table_item_key").text();
          var value = values[key];
          if (value == undefined) {
            value = "";
          }
          $(item).find(".django_power_admin_widgets_popup_config_table_item_value input").val(value);
        });
      };
      var popup_config_table_save_values = function () {
        var values = JSON.parse(popup_config_table_textarea.val() || "{}");
        var text;
        popup_config_table_config_items.each(function (index, item) {
          var key = $(item).children(".django_power_admin_widgets_popup_config_table_item_key").text();
          var value = $(item).find(".django_power_admin_widgets_popup_config_table_item_value input").val();
          values[key] = value;
        });
        text = JSON.stringify(values);
        popup_config_table_textarea.val(text);
      };
      popup_config_table_btn.click(function () {
        popup_config_table_dialog.dialog({
          modal: true,
          title: popup_config_table_config.moreConfigBtnLabel,
          minWidth: popup_config_table_config.minWidth,
          maxWidth: popup_config_table_config.maxWidth,
          minHeight: popup_config_table_config.minHeight,
          maxHeight: popup_config_table_config.maxHeight,
          buttons: [{
            text: popup_config_table_config.cancelBtnLabel,
            click: function () {
              popup_config_table_dialog.dialog("close");
            }
          }, {
            text: popup_config_table_config.submitBtnLabel,
            class: "dialog-btn-primary",
            click: function () {
              popup_config_table_save_values();
              popup_config_table_dialog.dialog("close");
            }
          }]
        });
      });
      // init
      popup_config_table_load_values();
    });
    return $(this);
  };

  $(document).ready(function () {
    $(".django_power_admin_widgets_popup_config_table_wrapper").PopupConfigTable();
    $(document).on("formset:added", function (event, $row, formsetName) {
      $row.find(".django_power_admin_widgets_popup_config_table_wrapper").PopupConfigTable();
    });
  });
})(jQuery);
