// Pay tax
document.getElementById('payTaxForm').addEventListener('submit', async e => {
  e.preventDefault();
  const data = {
    citizenName: document.getElementById('citizenName').value.trim(),
    cnic: document.getElementById('cnic').value.trim(),
    assetId: document.getElementById('assetId').value.trim(),
    amount: parseInt(document.getElementById('amount').value.trim())
  };
  try {
    const res = await fetch('/api/pay_tax', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
    });
    const result = await res.json();
    document.getElementById('taxResponse').textContent = res.ok ? `Success! Receipt ID: ${result.receiptId}` : `Error: ${result.error}`;
  } catch (err) {
    document.getElementById('taxResponse').textContent = `Error: ${err.message}`;
  }
});

// Vehicle registration
document.getElementById('vehicleRegisterForm').addEventListener('submit', async e => {
  e.preventDefault();
  const data = {
    vehicleId: document.getElementById('vehicleIdReg').value.trim(),
    ownerCNIC: document.getElementById('ownerCNICReg').value.trim()
  };
  try {
    const res = await fetch('/api/register_vehicle', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
    });
    const result = await res.json();
    document.getElementById('vehicleRegisterResponse').textContent = res.ok ? result.status : `Error: ${result.error}`;
  } catch (err) {
    document.getElementById('vehicleRegisterResponse').textContent = `Error: ${err.message}`;
  }
});

// Number plate application
document.getElementById('numberPlateApplyForm').addEventListener('submit', async e => {
  e.preventDefault();
  const data = { vehicleId: document.getElementById('vehicleIdPlate').value.trim() };
  try {
    const res = await fetch('/api/apply_number_plate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
    const result = await res.json();
    document.getElementById('numberPlateApplyResponse').textContent = res.ok ? result.status : `Error: ${result.error}`;
  } catch (err) {
    document.getElementById('numberPlateApplyResponse').textContent = `Error: ${err.message}`;
  }
});

// Ownership transfer request
document.getElementById('ownershipTransferForm').addEventListener('submit', async e => {
  e.preventDefault();
  const data = {
    vehicleId: document.getElementById('vehicleIdTransfer').value.trim(),
    newOwnerCNIC: document.getElementById('newOwnerCNIC').value.trim()
  };
  try {
    const res = await fetch('/api/request_ownership_transfer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
    const result = await res.json();
    document.getElementById('ownershipTransferResponse').textContent = res.ok ? result.status : `Error: ${result.error}`;
  } catch (err) {
    document.getElementById('ownershipTransferResponse').textContent = `Error: ${err.message}`;
  }
});
