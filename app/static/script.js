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

// Comparison page - update variant badges when SWH transaction changes

const swhDropdown = document.getElementById("swh_transaction");
const caBadge = document.getElementById("var-ca");
const cvBadge = document.getElementById("var-cv");
const cxBadge = document.getElementById("var-cx");

function resetBadge(badge, last = false) {
  if (last) {
    badge.className = "badge bg-light text-dark border";
  } else {
    badge.className = "badge bg-light text-dark border me-2";
  }
}

function setBadge(badge, variant, expectedVariants, foundVariants, last = false) {
  resetBadge(badge, last);

  if (!expectedVariants.includes(variant)) {
    return;
  }

  if (foundVariants.includes(variant)) {
    if (last) {
      badge.className = "badge bg-success";
    } else {
      badge.className = "badge bg-success me-2";
    }
    return;
  }

  if (last) {
    badge.className = "badge bg-danger";
  } else {
    badge.className = "badge bg-danger me-2";
  }
}

function updateVariantBadges() {
  if (!swhDropdown) {
    return;
  }

  const selectedOption = swhDropdown.options[swhDropdown.selectedIndex];

  if (!selectedOption || !selectedOption.value) {
    resetBadge(caBadge);
    resetBadge(cvBadge);
    resetBadge(cxBadge, true);
    return;
  }

  const expectedVariants = JSON.parse(
    selectedOption.dataset.variants || "[]"
  );

  const foundVariants = JSON.parse(
    selectedOption.dataset.foundVariants || "[]"
  );

  setBadge(caBadge, "CA", expectedVariants, foundVariants);
  setBadge(cvBadge, "CV", expectedVariants, foundVariants);
  setBadge(cxBadge, "CX", expectedVariants, foundVariants, true);
}

if (swhDropdown) {
  swhDropdown.addEventListener("change", updateVariantBadges);
}
