const form = document.getElementById('analyzeForm');
const loading = document.getElementById('loading');
const resultEl = document.getElementById('result');
const btn = document.getElementById('btn');

function setLoading(on) {
  loading.style.display = on ? 'flex' : 'none';
  btn.disabled = on;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  setLoading(true);
  resultEl.textContent = '{}';

  try {
    const fd = new FormData();
    const text = document.getElementById('text').value;
    const file = document.getElementById('file').files[0];
    if (text && text.trim().length) fd.append('text', text);
    if (file) fd.append('file', file, file.name);

    const res = await fetch('/analyze', { method: 'POST', body: fd });
    const data = await res.json();
    resultEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultEl.textContent = JSON.stringify({ error: String(err) }, null, 2);
  } finally {
    setLoading(false);
  }
});

