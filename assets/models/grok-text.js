document.querySelectorAll('[data-copy]').forEach((button) => {
  button.addEventListener('click', async () => {
    const initial = button.textContent;
    const chinese = document.documentElement.lang === 'zh-CN';
    try {
      await navigator.clipboard.writeText(button.closest('.gt-code').querySelector('code').textContent);
      button.textContent = chinese ? '已复制' : 'Copied';
    } catch {
      button.textContent = chinese ? '请选择代码复制' : 'Select code to copy';
    }
    window.setTimeout(() => { button.textContent = initial; }, 2000);
  });
});
