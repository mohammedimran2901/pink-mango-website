// === DAILY CHECK-IN ===
function initCheckIn() {
  const log = JSON.parse(localStorage.getItem('adhdCheckin') || '[]');
  document.querySelectorAll('.mood-btn').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.mood-btn').forEach(x => x.classlist.remove('selected'));
      b.classlist.add('selected');
    };
  });
  document.getElementById('energy').oninput = function() { this.nextElementSibling.textContent = this.value + '/10'; };
  document.getElementById('focus').oninput = function() { this.nextElementSibling.textContent = this.value + '/10'; };
  document.getElementById('overwhelm').oninput = function() { this.nextElementSibling.textContent = this.value + '/10'; };
  document.querySelector('.checkin-log').textContent = log.length > 0 ? `Last check-in: ${log[log.length-1].date}` : 'No check-ins yet.';
}
function saveCheckIn() {
  const mood = document.querySelector('.mood-btn.selected');
  const energy = document.getElementById('energy').value;
  const focus = document.getElementById('focus').value;
  const overwhelm = document.getElementById('overwhelm').value;
  if (!mood) { alert('Select your mood first.'); return; }
  const log = JSON.parse(localStorage.getItem('adhdCheckin') || '[]');
  log.push({ date: new Date().toLocaleDateString(), mood: mood.textContent, energy, focus, overwhelm });
  localStorage.setItem('adhdCheckin', JSON.stringify(log));
  document.querySelector('.checkin-log').textContent = `Saved! Streak: ${log.length} days`;
}

// === RSD PULSE ===
function initRSD() {
  document.querySelectorAll('.rsd-btn').forEach(b => {
    b.onclick = () => {
      const g = b.parentElement;
      g.querySelectorAll('.rsd-btn').forEach(x => x.classlist.remove('active'));
      b.classlist.add('active');
    };
  });
}
function saveRSD() {
  const trigger = document.querySelector('.rsd-buttons .active');
  const intensity = document.getElementById('rsd-intensity').value;
  if (!trigger) { alert('Select your trigger first.'); return; }
  const log = JSON.parse(localStorage.getItem('rsdLog') || '[]');
  log.push({ date: new Date().toLocaleDateString(), trigger: trigger.textContent.trim(), intensity });
  localStorage.setItem('rsdLog', JSON.stringify(log));
  const c = document.getElementById('rsd-console');
  c.textContent = `Logged! ${log.length} entries tracked.`;
  setTimeout(() => c.textContent = '', 3000);
}

// === ADHD TAX CALCULATOR ===
function calcTax() {
  let total = 0;
  document.querySelectorAll('.calc-row input').forEach(i => {
    const val = parseFloat(i.value) || 0;
    total += val * (i.dataset.mult || 1);
  });
  document.getElementById('calc-result').innerHTML = `$${total.toLocaleString()}/yr <span style="color:var(--muted);font-size:14px;">— saved with the right systems</span>`;
}

// === QUIZ ===
const QUIZ = [
  { q: 'What describes your biggest daily struggle?',
    o: ['Starting tasks, finishing nothing', 'Taking everything personally', 'Emotional burnout from masking', 'Losing hours to hyperfocus'] },
  { q: 'When you are overwhelmed, you usually:',
    o: ['Shut down and scroll for hours', 'Have an emotional reaction you regret', 'Withdraw and ghost everyone', 'Binge eat or spend money'] },
  { q: 'Your social life feels:',
    o: ['Exhausting — I mask the whole time', 'Lonely — I forget to reply to people', 'Dramatic — I take things too personally', 'Fine but I have no energy for it'] },
  { q: 'Work is hard because:',
    o: ['I cannot focus on one thing', 'I am terrified of criticism', 'I burn out every 3 months', 'I procrastinate until the last minute'] },
  { q: 'The book I need most right now:',
    o: ['Executive function and focus', 'RSD and emotional regulation', 'AuDHD overwhelm and burnout', 'ADHD money management'] }
];
let quizStep = 0, quizAnswers = [];

function initQuiz() {
  renderQuiz();
}
function renderQuiz() {
  if (quizStep >= QUIZ.length) { showQuizResult(); return; }
  const q = QUIZ[quizStep];
  let html = `<div class="quiz-question">${quizStep+1}. ${q.q}</div><div class="quiz-options">`;
  q.o.forEach((opt, i) => {
    html += `<div class="quiz-opt" onclick="selectQuiz(${i})">${opt}</div>`;
  });
  html += '</div>';
  document.getElementById('quiz-body').innerHTML = html;
}
function selectQuiz(idx) {
  quizAnswers.push(idx);
  quizStep++;
  renderQuiz();
}
function showQuizResult() {
  const counts = {};
  quizAnswers.forEach(a => { counts[a] = (counts[a] || 0) + 1; });
  let top = 0, topVal = 0;
  for (const [k,v] of Object.entries(counts)) {
    if (v > topVal) { top = parseInt(k); topVal = v; }
  }
  const recs = [
    { book: 'The Spark Within', author: 'Clara Bennett', note: 'Focus, executive function, and thriving with an ADHD brain' },
    { book: 'The RSD Effect', author: 'Clara Bennett', note: 'Rejection sensitivity, emotional regulation, and turning intensity into strength' },
    { book: 'The Overwhelm Fix', author: 'Clara Bennett', note: 'AuDHD overwhelm, burnout recovery, and finding your pace' },
    { book: 'The ADHD Money Fix', author: 'Clara Bennett', note: 'Impulse spending, ADHD tax, and financial systems that work' },
  ];
  const r = recs[top] || recs[0];
  document.getElementById('quiz-body').innerHTML = `<div class="quiz-result" style="display:block;">
    <h4>📖 Your Book: <em>${r.book}</em></h4>
    <p>by ${r.author} — ${r.note}</p>
    <p style="margin-top:8px;"><a href="https://play.google.com/store/search?q=${r.book.replace(' ','+')}+${r.author.replace(' ','+')}&c=books" target="_blank">Find on Google Play Books →</a></p>
    <button onclick="resetQuiz()" style="padding:6px 14px;border-radius:12px;border:1px solid var(--border);cursor:pointer;">Take again</button>
  </div>`;
}
function resetQuiz() { quizStep = 0; quizAnswers = []; renderQuiz(); }

// === POMODORO TIMER ===
let timerRunning = false, timerSeconds = 1500, timerInterval = null;
function initTimer() {
  updateTimerDisplay();
}
function updateTimerDisplay() {
  const m = String(Math.floor(timerSeconds/60)).padStart(2,'0');
  const s = String(timerSeconds%60).padStart(2,'0');
  document.getElementById('timer-display').textContent = `${m}:${s}`;
}
function toggleTimer() {
  if (timerRunning) { clearInterval(timerInterval); timerRunning = false; document.getElementById('timer-btn-start').textContent = '▶ Resume'; }
  else {
    timerRunning = true;
    document.getElementById('timer-btn-start').textContent = '⏸ Pause';
    timerInterval = setInterval(() => {
      if (timerSeconds > 0) { timerSeconds--; updateTimerDisplay(); }
      else { clearInterval(timerInterval); timerRunning = false; document.getElementById('timer-btn-start').textContent = '✅ Done!'; }
    }, 1000);
  }
}
function resetTimer() {
  clearInterval(timerInterval); timerRunning = false;
  timerSeconds = parseInt(document.getElementById('timer-duration').value || '25') * 60;
  updateTimerDisplay();
  document.getElementById('timer-btn-start').textContent = '▶ Start';
}

// === BRAIN DUMP ===
function saveBrainDump() {
  const text = document.getElementById('brain-text').value;
  localStorage.setItem('brainDump', text);
  document.querySelector('.brain-save').textContent = '✅ Saved!';
  setTimeout(() => document.querySelector('.brain-save').textContent = 'Save', 2000);
}
function loadBrainDump() {
  const saved = localStorage.getItem('brainDump');
  if (saved) document.getElementById('brain-text').value = saved;
}

// === INIT ===
window.onload = function() {
  initCheckIn();
  initRSD();
  initQuiz();
  initTimer();
  loadBrainDump();
  calcTax();
};
