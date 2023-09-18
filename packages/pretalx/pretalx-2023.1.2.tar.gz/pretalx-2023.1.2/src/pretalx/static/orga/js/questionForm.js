function question_page_toggle_view() {
  console.log("yeah")
  const variant = document.querySelector("#id_variant").value
  setVisibility(
    "#answer-options",
    variant === "choices" || variant === "multiple_choice"
  )
  setVisibility(
    "#alert-required-boolean",
    variant === "boolean" && document.querySelector("#id_question_required input[value=required]").checked
  )
  setVisibility("#limit-length", variant === "text" || variant === "string")
  setVisibility("#limit-number", variant === "number")
  setVisibility("#limit-date", variant === "date")
  setVisibility("#limit-datetime", variant === "datetime")
}

function question_page_toggle_target_view() {
  if (document.querySelector(".limit-submission")) {
    setVisibility(
      ".limit-submission",
      document.querySelector("#id_target").value === "submission"
    )
  }
  setVisibility(
    "#is-visible-to-reviewers",
    document.querySelector("#id_target").value !== "reviewer"
  )
}

function setVisibility(element, value) {
  if (typeof element === "string") {
    element = document.querySelector(element);
  }
  if (element) {
    if (value) {
      element.classList.remove("d-none");
    } else {
      element.classList.add("d-none");
    }
  }
}
document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("#id_variant").addEventListener("change", question_page_toggle_view)
    document.querySelectorAll("#id_question_required input").forEach(e => e.addEventListener("change", question_page_toggle_view))
    question_page_toggle_view()
    document.querySelector("#id_target").addEventListener("change", question_page_toggle_target_view)
    question_page_toggle_target_view()

    let deadline = $("#id_deadline")
    /* require after deadline case */
    if ($("#id_question_required_0, #id_question_required_1").is(':checked')) {
        deadline.attr("disabled", true);
        deadline.attr("required", false);
    }
    $("#id_question_required_0, #id_question_required_1").click(function () {
        deadline.val("");
        deadline.attr("disabled", true);
        deadline.attr("required", false);
    });
    /* always required and always optional cases */
    if ($("#id_question_required_2").is(':checked')) {
        deadline.attr("disabled", false);
        deadline.attr("required", true);
    }

    $("#id_question_required_2").click(function () {
        deadline.attr("disabled", false);
        deadline.attr("required", true);
    });
})
