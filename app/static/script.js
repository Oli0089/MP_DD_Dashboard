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
