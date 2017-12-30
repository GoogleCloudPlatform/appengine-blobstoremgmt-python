/**
 * Copyright 2018 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Initializer
$(function(){
  // Initialize the date pickers.
  $.datepicker.setDefaults(
    $.extend($.datepicker.regional[""])
  );
  var filterStart = $("#filter_creation_start");
  var filterEnd = $("#filter_creation_end");
  filterStart.datepicker();
  filterEnd.datepicker();
  if (filterStart.val()) {
    var startDate = new Date(parseInt(filterStart.val())*1000);
    filterStart.datepicker('setDate', startDate);
  }
  if (filterEnd.val()) {
    var endDate = new Date(parseInt(filterEnd.val())*1000);
    filterEnd.datepicker('setDate', endDate);
  }
  // Emit timestamps in local format.
  $(".date_utc").map(function(index, tag) {
    var elem = $(this);
    var epochMillis = parseInt(elem.attr("epoch"))*1000;
    elem.html(new Date(epochMillis).toLocaleString());
  });
  $("#filter_filename_prefix").keyup(function(event) {
    if (event.keyCode === 13) {
      $("#filter-button").click();
    }
  });
  $("#filter_content_type").keyup(function(event) {
    if (event.keyCode === 13) {
      $("#filter-button").click();
    }
  });
  $("#filter_size").keyup(function(event) {
    if (event.keyCode === 13) {
      $("#filter-button").click();
    }
  });
});

// Bind the next page button click event.
$(".next-page").bind("click", function() {
  location.search = $.query.set("start", "{{cursor}}");
});

// Bind the column headers' click events.
["filename", "content_type", "size", "creation"].map(function(name) {
  var link = $("#nav_" + name);
  var selected = link.hasClass("selected");
  link.bind("click", function() {
    q = $.query.empty()
               .set("sort_col", name);
    if (selected) {
      q = q.set("sort_dir", "{{opp_sort_dir}}");
    }
    location.search = q;
  });
});

// Process filter button click event.
$("#filter-button").bind("click", function() {
  var filterVal = $("#filter-select").val();
  var q = $.query.empty();

  if (filterVal == "filename") {
    var prefixVal = $.trim($("#filter_filename_prefix").val());
    if (prefixVal == "") {
      alert("Please enter a prefix.");
      return;
    }
    location.search = q.set("filter", "filename")
                       .set("filename_prefix", prefixVal);
    return;
  }

  if (filterVal == "content_type") {
    var contentTypeVal = $.trim($("#filter_content_type").val());
    if (contentTypeVal == "") {
      alert("Please enter a content type.");
      return;
    }
    location.search = q.set("filter", "content_type")
                       .set("content_type", contentTypeVal);
    return;
  }

  if (filterVal == "size") {
    var sizeVal = $.trim($("#filter_size").val());
    if (!$.isNumeric(sizeVal)) {
      alert("Size must be an integer.");
      return;
    }
    location.search = q.set("filter", "size")
                       .set("size_op", $("#filter_size_op").val())
                       .set("size_unit", $("#filter_size_unit").val())
                       .set("size", parseFloat(sizeVal));
    return;
  }

  if (filterVal == "creation") {
    var creationOp = $("#filter_creation_op").val();

    q = q.set("filter", "creation")
         .set("creation_op", creationOp)

    if (creationOp == 'range') {
      var startDate = $("#filter_creation_start").datepicker('getDate');
      var endDate = $("#filter_creation_end").datepicker('getDate');
      if (!startDate && !endDate) {
        alert("Please enter a start date, end date, or both.");
        return;
      }
      if (startDate && endDate && endDate < startDate) {
        alert("End date must be after start date.");
        return;
      }
      if (startDate) {
        q = q.set("creation_start", startDate.getTime()/1000);
      }
      if (endDate) {
        var onedaySeconds = 60*60*24-1;
        q = q.set("creation_end", endDate.getTime()/1000+onedaySeconds);
      }
    }

    location.search = q;
    return;
  }
});

$("#filter-select").bind("change", function() {
  $(".filter-panel").hide();
  var filterPanel = $("#filter_panel_" + this.value);
  filterPanel.find("input").val("");
  filterPanel.find("select").find(".default").prop("selected", "selected");
  filterPanel.show();
});

$("#filter_creation_op").bind("change", function() {
  var creationRangePanel = $("#filter_panel_creation_range");
  creationRangePanel.hide();
  if (this.value == "range") {
    creationRangePanel.show();
  }
});

$(".blob-check").bind("click", function() {
  if (this.checked) {
    $("button.blob-delete").removeAttr("disabled");
  } else {
    var checked = false;
    $(".all-check").prop('checked', false);
    $(".blob-check").map(function() {
      if (this.checked) {
        checked = true;
      }
    });
    if (checked) {
      $("button.blob-delete").removeAttr("disabled");
    } else {
      $("button.blob-delete").attr("disabled", "disabled");
    }
  }
});

$("button.blob-delete").bind("click", function() {
  var keys = $(".blob-check").map(function() {
    if (this.checked) {
      return this.id;
    }
  }).get();

  var okay = confirm("This will delete " + keys.length
                     + " blob" + (keys.length == 1 ? "" : "s")
                     + ". Okay to continue?");
  if (!okay) {
    return;
  }

  var result = $.post('/api/delete', {'keys': keys.join()})
    .done(function(data) {
    })
    .fail(function() {
      alert("An error occurred, please try again.");
    });
  location.reload();

});

$(".all-check").bind("click", function() {
  var checked = this.checked;
  if (checked) {
    $("button.blob-delete").removeAttr("disabled");
  } else {
    $("button.blob-delete").attr("disabled", "disabled");
  }
  $(".blob-check").map(function() {
    this.checked = checked;
  });
});
