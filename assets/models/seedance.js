document.documentElement.classList.remove('no-js');
document.querySelectorAll('.o-copy').forEach((button) => {
  button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.target);
    if (!target) return;
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(target.innerText);
      button.textContent = document.documentElement.lang === 'en' ? 'Copied' : '已复制';
    } catch {
      button.textContent = document.documentElement.lang === 'en' ? 'Select code to copy' : '请选中代码复制';
    }
    setTimeout(() => { button.textContent = original; }, 1800);
  });
});
