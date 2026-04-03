// Reusable confirm modal logic
function showConfirm(message, onConfirm) {
  const modal = new bootstrap.Modal(document.getElementById("confirmModal"));
  const msgEl = document.getElementById("confirmModalMessage");
  const confirmBtn = document.getElementById("confirmModalConfirmBtn");

  msgEl.textContent = message;
  confirmBtn.onclick = () => {
    modal.hide();
    if (typeof onConfirm === "function") onConfirm();
  };

  modal.show();
}

// Used to check if the user is changing own role
function confirmOwnRoleChange() {
  document.querySelectorAll("form[data-self='true']").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!window.confirm("You are about to change your own role. Continue?")) {
        e.preventDefault();
      }
    });
  });
}
document.addEventListener("DOMContentLoaded", confirmOwnRoleChange);

// Comparison page variant display logic
const swhDropdown = document.getElementById("swh_transaction");
const caBadge = document.getElementById("var-ca");
const cvBadge = document.getElementById("var-cv");
const cxBadge = document.getElementById("var-cx");

if (swhDropdown && caBadge && cvBadge && cxBadge) {
  swhDropdown.addEventListener("change", function () {
    const selectedOption = swhDropdown.options[swhDropdown.selectedIndex];

    // reset all to grey
    caBadge.className = "badge bg-light text-dark border me-2";
    cvBadge.className = "badge bg-light text-dark border me-2";
    cxBadge.className = "badge bg-light text-dark border";

    const variants = JSON.parse(selectedOption.dataset.variants || "[]");

    // highlight based on config
    if (variants.includes("CA")) {
      caBadge.className = "badge bg-secondary me-2";
    }

    if (variants.includes("CV")) {
      cvBadge.className = "badge bg-secondary me-2";
    }

    if (variants.includes("CX")) {
      cxBadge.className = "badge bg-secondary";
    }
  });
}


// Set Previous DD to latest option on page load
document.addEventListener("DOMContentLoaded", function () {
  const previousDD = document.getElementById("previous_dd");

  if (previousDD && previousDD.options.length > 0) {
    // Select the last option (latest DD)
    previousDD.selectedIndex = previousDD.options.length - 1;
  }
});
