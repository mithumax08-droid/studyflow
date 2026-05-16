// ── Toggle password visibility ──
function togglePw(inputId, iconEl) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    iconEl.textContent = '🙈';
  } else {
    inp.type = 'password';
    iconEl.textContent = '👁️';
  }
}

// ── Password strength meter ──
function checkStrength(input) {
  const pw  = input.value;
  const bar = document.getElementById('pw-bar');
  const lbl = document.getElementById('pw-label');
  if (!bar || !lbl) return;

  let score = 0;
  if (pw.length >= 6)  score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  const levels = [
    { w: '25%', c: '#ff6b6b', t: 'Weak' },
    { w: '50%', c: '#f5a623', t: 'Fair' },
    { w: '75%', c: '#5ac8fa', t: 'Good' },
    { w: '100%',c: '#2dd4a0', t: 'Strong' }
  ];
  const lv = levels[Math.min(score, 3)];
  bar.style.width      = pw ? lv.w : '0%';
  bar.style.background = lv.c;
  lbl.textContent      = pw ? lv.t : '';
  lbl.style.color      = lv.c;
}

// ── Auto-dismiss flash messages ──
document.addEventListener('DOMContentLoaded', function () {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });
});
