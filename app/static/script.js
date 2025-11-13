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

