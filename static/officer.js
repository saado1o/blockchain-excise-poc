let paymentsData = [];
let paymentsShowingAll = false;

async function fetchPayments() {
  const tbody = document.getElementById('paymentsTableBody');
  try {
    const response = await fetch('/api/payments');
    if (!response.ok) throw new Error('Failed to fetch payments');
    paymentsData = await response.json();
    renderPayments();
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-danger">Error loading payments</td></tr>`;
    console.error(error);
  }
}

function renderPayments() {
  const tbody = document.getElementById('paymentsTableBody');
  tbody.innerHTML = '';
  const displayData = paymentsShowingAll ? paymentsData : paymentsData.slice(0, 8);

  if (displayData.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4">No payments found.</td></tr>';
    return;
  }
  for (const p of displayData) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.receiptId}</td>
      <td>${p.citizenName}</td>
      <td>${p.assetId}</td>
      <td>${p.amount}</td>
    `;
    tbody.appendChild(tr);
  }
  document.getElementById('togglePaymentsBtn').textContent = paymentsShowingAll ? 'View Less' : 'View More';
}

document.addEventListener('DOMContentLoaded', () => {
  fetchPayments();
  fetchPendingNumberplates();
  fetchPendingOwnershipTransfers();
  document.getElementById('togglePaymentsBtn').addEventListener('click', () => {
    paymentsShowingAll = !paymentsShowingAll;
    renderPayments();
  });
});

async function fetchPendingNumberplates() {
  const tbody = document.getElementById('pendingNumberplatesBody');
  try {
    const res = await fetch('/api/pending_numberplates');
    if (!res.ok) throw new Error('Failed');
    const data = await res.json();
    tbody.innerHTML = '';
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3">No pending number plates.</td></tr>';
      return;
    }
    for (const item of data) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${item.vehicleId}</td><td>${item.ownerCNIC}</td><td><button class="btn btn-success btn-sm" onclick="approveNumberPlate('${item.vehicleId}')">Approve</button></td>`;
      tbody.appendChild(tr);
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="3" class="text-danger">Error loading data.</td></tr>';
  }
}

async function fetchPendingOwnershipTransfers() {
  const tbody = document.getElementById('pendingOwnershipTransfersBody');
  try {
    const res = await fetch('/api/pending_ownershiptransfers');
    if (!res.ok) throw new Error('Failed');
    const data = await res.json();
    tbody.innerHTML = '';
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4">No pending ownership transfers.</td></tr>';
      return;
    }
    for (const item of data) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${item.vehicleId}</td><td>${item.oldOwnerCNIC}</td><td>${item.newOwnerCNIC}</td><td><button class="btn btn-success btn-sm" onclick="approveOwnershipTransfer('${item.vehicleId}')">Approve</button></td>`;
      tbody.appendChild(tr);
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-danger">Error loading data.</td></tr>';
  }
}

async function approveNumberPlate(vehicleId) {
  if (!confirm('Approve number plate for vehicle: ' + vehicleId + '?')) return;
  const res = await fetch('/api/approve_number_plate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({vehicleId})
  });
  const data = await res.json();
  if (res.ok) {
    alert(data.status);
    fetchPendingNumberplates();
  } else {
    alert(data.error || 'Approval failed');
  }
}

async function approveOwnershipTransfer(vehicleId) {
  if (!confirm('Approve ownership transfer for vehicle: ' + vehicleId + '?')) return;
  const res = await fetch('/api/approve_ownership_transfer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({vehicleId})
  });
  const data = await res.json();
  if (res.ok) {
    alert(data.status);
    fetchPendingOwnershipTransfers();
  } else {
    alert(data.error || 'Approval failed');
  }
}
