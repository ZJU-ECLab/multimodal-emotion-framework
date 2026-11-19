(() => {
  const search = document.querySelector('#emotion-search');
  const modality = document.querySelector('#modality-filter');
  const reset = document.querySelector('#reset');
  const expand = document.querySelector('#expand');
  const rows = Array.from(document.querySelectorAll('.matrix-table tbody tr'));
  let expanded = false;
  function update() {
    const query = search.value.trim();
    let visible = 0;
    rows.forEach(row => {
      const matchesEmotion = row.dataset.emotion.includes(query);
      const matchesModality = modality.value === 'all' || row.dataset.modalities.split(',').includes(modality.value);
      row.hidden = !(matchesEmotion && matchesModality);
      if (!row.hidden) visible++;
      row.querySelectorAll('details').forEach(detail => { detail.open = expanded && !row.hidden; });
    });
    document.querySelector('#result-count').textContent = `显示 ${visible} / ${rows.length} 类情绪及相关状态`;
    document.querySelector('#empty-state').hidden = visible !== 0;
  }
  search.addEventListener('input', update);
  modality.addEventListener('change', update);
  reset.addEventListener('click', () => {
    search.value = '';
    modality.value = 'all';
    update();
  });
  expand.addEventListener('click', () => {
    expanded = !expanded;
    expand.textContent = expanded ? '收起当前证据' : '展开当前证据';
    expand.setAttribute('aria-pressed', String(expanded));
    update();
  });
  document.querySelector('.filter-panel').hidden = false;
  update();
})();
