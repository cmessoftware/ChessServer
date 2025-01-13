    let confirmHandler = null;
    let modalInstance;

    
    const handleResignation = () => {
      resign();
      hideModal();
    }

    const createModal =  () => {
      // Create modal container
      const modalHTML = `
        <div class="modal fade" id="dynamicModal" tabindex="-1" aria-labelledby="dynamicModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="dynamicModalLabel"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body" id="dynamicModalBody"></div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" id="modalCancelBtn" data-bs-dismiss="modal"></button>
                <button type="button" class="btn btn-danger" id="modalConfirmBtn"></button>
              </div>
            </div>
          </div>
        </div>
      `;
      document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    function openModal(title, bodyText, cancelText, confirmText, confirmAction) {
      if (!document.getElementById('dynamicModal')) {
        createModal();
      }
    
      document.getElementById('dynamicModalLabel').textContent = title;
      document.getElementById('dynamicModalBody').textContent = bodyText;
      document.getElementById('modalCancelBtn').textContent = cancelText;
      document.getElementById('modalConfirmBtn').textContent = confirmText;
    
      const confirmBtn = document.getElementById('modalConfirmBtn');
      confirmBtn.onclick = null;
      confirmBtn.addEventListener('click', confirmAction);

      const cancelBtn = document.getElementById('modalCancelBtn');
      cancelBtn.onclick = null;
      cancelBtn.addEventListener('click', hideModal);
    
      // Create a new modal instance and store it
      const modalElement = document.getElementById('dynamicModal');
      modalInstance = new bootstrap.Modal(modalElement);
      modalInstance.show();
    }
    
    function hideModal() {
      if (modalInstance) modalInstance.hide();
    }