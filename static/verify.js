document.getElementById('verifyForm').addEventListener('submit', async e => {
  e.preventDefault();
  const receiptId = document.getElementById('receiptId').value.trim();
  const resultEl = document.getElementById('result');
  resultEl.textContent = 'Verifying...';
  try {
    const res = await fetch(`/api/verify/${receiptId}`);
    const data = await res.json();
    if (res.ok) {
      const date = new Date(data.timestamp * 1000).toLocaleString();
      resultEl.innerHTML = `
        <ul>
          <li><strong>Citizen Name:</strong> ${data.citizenName}</li>
          <li><strong>CNIC:</strong> ${data.cnic}</li>
          <li><strong>Asset ID:</strong> ${data.assetId}</li>
          <li><strong>Amount:</strong> ${data.amount}</li>
          <li><strong>Timestamp:</strong> ${date}</li>
        </ul>`;
    } else {
      resultEl.textContent = `Error: ${data.error}`;
    }
  } catch (err) {
    resultEl.textContent = 'Error: ' + err.message;
  }
});
