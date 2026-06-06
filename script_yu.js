// ===============================
// 全域資料
// ===============================
let cases = [];
let activeCases = [];
let currentCase = null;
let currentIndex = -1;

let records = [];
let lastRecord = null;

let sequentialQueue = [];
let sequentialPointer = 0;

// Skewb 幾何資料
let skewbGeometry = null;

// idle    = 還沒開始
// ready   = 空白鍵按住，準備開始
// running = 計時中
let timerState = "idle";

let startTime = 0;
let elapsedTime = 0;
let timerInterval = null;

// 星星題目
let starredCases = new Set();

const STORAGE_RECORDS_KEY = "skewbTrainerRecords";
const STORAGE_STARS_KEY = "skewbTrainerStars";

// ===============================
// DOM
// ===============================
const depthChecks = document.querySelectorAll(".depth-check");

const starredOnlyCheck = document.getElementById("starredOnlyCheck");
const excludeStarredCheck = document.getElementById("excludeStarredCheck");

const practiceModeRadios = document.querySelectorAll('input[name="practiceMode"]');

const reloadButton = document.getElementById("reloadButton");
const nextButton = document.getElementById("nextButton");
const resetButton = document.getElementById("resetButton");
const clearButton = document.getElementById("clearButton");
const clearStarsButton = document.getElementById("clearStarsButton");
const starButton = document.getElementById("starButton");

const caseCount = document.getElementById("caseCount");
const selectedDepthText = document.getElementById("selectedDepthText");
const currentIndexText = document.getElementById("currentIndexText");
const timerStateText = document.getElementById("timerStateText");

const caseTitle = document.getElementById("caseTitle");
const scrambleText = document.getElementById("scrambleText");

const caseCanvas = document.getElementById("caseCanvas");
const prevCanvas = document.getElementById("prevCanvas");
const noImageText = document.getElementById("noImageText");

const timerDisplay = document.getElementById("timerDisplay");

const prevTime = document.getElementById("prevTime");
const prevDepth = document.getElementById("prevDepth");
const prevCase = document.getElementById("prevCase");
const prevScramble = document.getElementById("prevScramble");
const prevSolution = document.getElementById("prevSolution");
const prevNote = document.getElementById("prevNote");

const solveCount = document.getElementById("solveCount");
const bestTime = document.getElementById("bestTime");
const avgTime = document.getElementById("avgTime");
const lastTime = document.getElementById("lastTime");
const recordBody = document.getElementById("recordBody");

// ===============================
// 初始化事件
// ===============================
reloadButton.addEventListener("click", loadSelectedDatasets);
nextButton.addEventListener("click", nextCase);
resetButton.addEventListener("click", resetTimer);
clearButton.addEventListener("click", clearRecords);

if (clearStarsButton) {
  clearStarsButton.addEventListener("click", clearStars);
}

starButton.addEventListener("click", toggleLastRecordStar);

depthChecks.forEach(check => {
  check.addEventListener("change", loadSelectedDatasets);
});

starredOnlyCheck.addEventListener("change", () => {
  if (starredOnlyCheck.checked) {
    excludeStarredCheck.checked = false;
  }

  handleReviewModeChange();
});

excludeStarredCheck.addEventListener("change", () => {
  if (excludeStarredCheck.checked) {
    starredOnlyCheck.checked = false;
  }

  handleReviewModeChange();
});

practiceModeRadios.forEach(radio => {
  radio.addEventListener("change", () => {
    rebuildSequentialQueue();

    if (activeCases.length > 0) {
      nextCase();
    }
  });
});

// 避免點 radio / checkbox 後，下一次空白鍵變成切換選項
document.querySelectorAll("input[type='radio'], input[type='checkbox']").forEach(input => {
  input.addEventListener("change", () => {
    input.blur();
  });
});

// ===============================
// 工具函式
// ===============================
function isTypingInput() {
  const el = document.activeElement;

  if (!el) return false;

  const tag = el.tagName.toLowerCase();

  if (tag === "textarea" || tag === "select") {
    return true;
  }

  if (tag === "input") {
    const type = el.type;

    return (
      type === "text" ||
      type === "number" ||
      type === "email" ||
      type === "password" ||
      type === "search" ||
      type === "url"
    );
  }

  return false;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function parseDepthFromCategory(category) {
  const match = String(category).match(/^(\d+)step$/);

  if (!match) {
    return null;
  }

  return Number(match[1]);
}

// ===============================
// 取得已勾選步數
// ===============================
function getSelectedDepths() {
  return Array.from(depthChecks)
    .filter(check => check.checked)
    .map(check => check.value);
}

// ===============================
// 複習模式
// ===============================
function getReviewMode() {
  if (starredOnlyCheck.checked) {
    return "starred";
  }

  if (excludeStarredCheck.checked) {
    return "unstarred";
  }

  return "all";
}

function handleReviewModeChange() {
  updateActiveCases();

  if (activeCases.length > 0) {
    nextCase();
  } else {
    caseTitle.textContent = "目前沒有符合條件的題目";
    scrambleText.textContent = "請取消篩選，或先把題目標星星";
    hideCurrentImage();
  }
}

function updateActiveCases() {
  const mode = getReviewMode();

  if (mode === "all") {
    activeCases = [...cases];
  }

  if (mode === "starred") {
    activeCases = cases.filter(item => starredCases.has(getCaseKey(item)));
  }

  if (mode === "unstarred") {
    activeCases = cases.filter(item => !starredCases.has(getCaseKey(item)));
  }

  caseCount.textContent = activeCases.length;

  rebuildSequentialQueue();
}

// ===============================
// 出題模式
// ===============================
function getPracticeMode() {
  const checked = document.querySelector('input[name="practiceMode"]:checked');
  return checked ? checked.value : "random";
}

function rebuildSequentialQueue() {
  sequentialQueue = activeCases.map((_, index) => index);

  // 洗牌：逐一練習但順序隨機、不重複
  for (let i = sequentialQueue.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [sequentialQueue[i], sequentialQueue[j]] = [sequentialQueue[j], sequentialQueue[i]];
  }

  sequentialPointer = 0;
}

// ===============================
// Skewb geometry + Canvas
// ===============================
async function loadSkewbGeometry() {
  const response = await fetch("skewb_geometry.json");

  if (!response.ok) {
    throw new Error("讀取 skewb_geometry.json 失敗");
  }

  skewbGeometry = await response.json();
}

function drawSkewbToCanvas(canvas, colors, scale = 4) {
  if (!canvas || !skewbGeometry || !colors || colors.length === 0) {
    if (canvas) {
      canvas.style.display = "none";
    }
    return;
  }

  const baseWidth = skewbGeometry.width;
  const baseHeight = skewbGeometry.height;

  canvas.width = baseWidth * scale;
  canvas.height = baseHeight * scale;

  const ctx = canvas.getContext("2d");

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  skewbGeometry.polygons.forEach((poly, index) => {
    const points = poly.points;
    const color = colors[index] || "#CCCCCC";

    if (!points || points.length === 0) return;

    ctx.beginPath();

    ctx.moveTo(
      points[0][0] * scale,
      points[0][1] * scale
    );

    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(
        points[i][0] * scale,
        points[i][1] * scale
      );
    }

    ctx.closePath();

    ctx.fillStyle = color;
    ctx.fill();

    ctx.strokeStyle = "black";
    ctx.lineWidth = 1.2 * scale;
    ctx.stroke();
  });

  canvas.style.display = "block";
}

function showCurrentSkewb(colors) {
  if (colors && colors.length > 0) {
    noImageText.style.display = "none";
    drawSkewbToCanvas(caseCanvas, colors, 4);
  } else {
    hideCurrentImage();
  }
}

function hideCurrentImage() {
  if (caseCanvas) {
    caseCanvas.style.display = "none";
  }

  if (noImageText) {
    noImageText.style.display = "block";
    noImageText.textContent = "此題沒有圖片資料";
  }
}

// ===============================
// 讀取多個 dataset
// ===============================
async function loadSelectedDatasets() {
  const selectedCategories = getSelectedDepths();

  selectedDepthText.textContent = selectedCategories.length > 0
    ? selectedCategories.join(", ")
    : "-";

  if (selectedCategories.length === 0) {
    cases = [];
    activeCases = [];
    caseCount.textContent = "0";
    caseTitle.textContent = "請至少選擇一個分類";
    scrambleText.textContent = "尚未載入題庫";
    hideCurrentImage();
    return;
  }

  caseTitle.textContent = "正在載入題庫...";
  scrambleText.textContent = selectedCategories
    .map(category => `dataset/${category}.json`)
    .join(" / ");

  hideCurrentImage();

  const allCases = [];

  for (const category of selectedCategories) {
    const jsonPath = `dataset/${category}.json`;

    try {
      const response = await fetch(jsonPath);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const normalized = data
        .map((item, index) => {
          const depthFromCategory = parseDepthFromCategory(category);

          return {
            scramble: String(item.scramble || "").trim(),
            name: String(item.case || item.name || `${category} #${index + 1}`).trim(),
            solution: String(item.solution || "").trim(),
            note: String(item.note || "").trim(),

            // 不使用 PNG，改用 colors 即時畫圖
            colors: Array.isArray(item.colors) ? item.colors : [],

            // 2step / 3step 會自動變成 2 / 3
            // cust1 這類就用 item.depth，沒有的話顯示 category
            depth: item.depth || depthFromCategory || category,

            // 新增分類名稱，方便之後顯示 / 星星 key 使用
            category: category,

            source: jsonPath
          };
        })
        .filter(item => item.scramble.length > 0);

      allCases.push(...normalized);

      console.log(`${jsonPath} 載入完成：${normalized.length} 題`);
    } catch (error) {
      console.error(`讀取失敗：${jsonPath}`, error);
      alert(`讀取失敗：${jsonPath}\n請確認 dataset 資料夾和 JSON 檔案是否存在，並用 Live Server 開啟。`);
    }
  }

  cases = allCases;
  updateActiveCases();

  if (cases.length === 0) {
    caseTitle.textContent = "沒有成功載入任何題目";
    scrambleText.textContent = "請確認 JSON 格式";
    hideCurrentImage();
    return;
  }

  if (activeCases.length === 0) {
    caseTitle.textContent = "目前篩選條件沒有題目";
    scrambleText.textContent = "請切回全部題目，或先標記星星題";
    hideCurrentImage();
    return;
  }

  nextCase();
}

// ===============================
// 題目控制
// ===============================
function algToChinese(alg) {
  const map = {
    "r'": "下",
    "r": "上",
    "R'": "右",
    "R": "左"
  };

  return String(alg)
    .trim()
    .split(/\s+/)
    .map(move => map[move] || move)
    .join(" ");
}
function nextCase() {
  if (timerState === "running") {
    if (!confirm("目前正在計時，確定要跳到下一題嗎？")) {
      return;
    }
  }

  if (activeCases.length === 0) {
    updateActiveCases();
  }

  if (activeCases.length === 0) {
    alert("目前篩選條件下沒有題目。請改成全部題目，或先標記星星題。");
    return;
  }

  resetTimer();

  const practiceMode = getPracticeMode();

  if (practiceMode === "random") {
    currentIndex = Math.floor(Math.random() * activeCases.length);
  }

  if (practiceMode === "sequential") {
    if (sequentialQueue.length === 0 || sequentialPointer >= sequentialQueue.length) {
      alert("逐一練習已完成一輪，將重新開始。");
      rebuildSequentialQueue();
    }

    currentIndex = sequentialQueue[sequentialPointer];
    sequentialPointer += 1;
  }

  currentCase = activeCases[currentIndex];

  currentIndexText.textContent = currentIndex + 1;

  caseTitle.textContent = `${formatCategoryLabel(currentCase)}｜${currentCase.name}`;
  //scrambleText.textContent = currentCase.scramble || "-";
  scrambleText.textContent = algToChinese(currentCase.scramble || "-");

  showCurrentSkewb(currentCase.colors);
}

function formatCategoryLabel(item) {
  if (typeof item.depth === "number") {
    return `${item.depth}-step`;
  }

  return String(item.category || item.depth || "custom");
}

// ===============================
// Timer
// ===============================
function setTimerState(newState) {
  timerState = newState;

  timerDisplay.classList.remove("ready", "running", "stopped");

  if (newState === "idle") {
    timerStateText.textContent = "待機";
    timerDisplay.classList.add("stopped");
  }

  if (newState === "ready") {
    timerStateText.textContent = "準備中，放開空白鍵開始";
    timerDisplay.classList.add("ready");
  }

  if (newState === "running") {
    timerStateText.textContent = "計時中";
    timerDisplay.classList.add("running");
  }
}

function prepareTimer() {
  if (!currentCase) {
    alert("請先載入題庫");
    return;
  }

  if (timerState !== "idle") return;

  setTimerState("ready");
  timerDisplay.textContent = "0.00";
  elapsedTime = 0;
}

function startTimer() {
  if (!currentCase) return;
  if (timerState !== "ready") return;

  elapsedTime = 0;
  startTime = Date.now();

  setTimerState("running");

  clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    elapsedTime = Date.now() - startTime;
    timerDisplay.textContent = formatTime(elapsedTime);
  }, 10);
}

function stopTimer() {
  if (timerState !== "running") return;

  clearInterval(timerInterval);
  elapsedTime = Date.now() - startTime;

  const timeText = formatTime(elapsedTime);
  const timeNumber = elapsedTime / 1000;

  const record = {
    timeText,
    timeNumber,
    depth: currentCase.depth,
    caseName: currentCase.name || `Case ${currentIndex + 1}`,
    scramble: currentCase.scramble,
    solution: currentCase.solution,
    note: currentCase.note,
    colors: currentCase.colors
  };

  records.push(record);
  lastRecord = record;

  saveRecordsToStorage();

  updatePrevious(record);
  updateStats();
  renderRecords();

  setTimerState("idle");
  nextCase();
}

function resetTimer() {
  clearInterval(timerInterval);

  elapsedTime = 0;
  startTime = 0;
  timerDisplay.textContent = "0.00";

  setTimerState("idle");
}

function formatTime(ms) {
  return (ms / 1000).toFixed(2);
}

// ===============================
// 紀錄與統計
// ===============================
function updatePrevious(record) {
  lastRecord = record;

  prevTime.textContent = record.timeText;
  prevDepth.textContent = formatCategoryLabel(record);
  prevCase.textContent = record.caseName || "-";
  //prevScramble.textContent = record.scramble || "-";
  //prevSolution.textContent = record.solution || "-";
  prevScramble.textContent = algToChinese(record.scramble || "-");
  prevSolution.textContent = algToChinese(record.solution || "-");
  prevNote.textContent = record.note || "-";

  if (record.colors && record.colors.length > 0) {
    drawSkewbToCanvas(prevCanvas, record.colors,2);
  } else if (prevCanvas) {
    prevCanvas.style.display = "none";
  }

  updateStarButton();
}

function updateStats() {
  solveCount.textContent = records.length;

  if (records.length === 0) {
    bestTime.textContent = "-";
    avgTime.textContent = "-";
    lastTime.textContent = "-";
    return;
  }

  const times = records.map(r => r.timeNumber);
  const best = Math.min(...times);
  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  const last = records[records.length - 1].timeNumber;

  bestTime.textContent = best.toFixed(2);
  avgTime.textContent = avg.toFixed(2);
  lastTime.textContent = last.toFixed(2);
}

function renderRecords() {
  recordBody.innerHTML = "";

  records.slice().reverse().forEach((record, reverseIndex) => {
    const originalIndex = records.length - reverseIndex;
    const starred = starredCases.has(getCaseKey(record)) ? "★" : "";

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${originalIndex}</td>
      <td>${record.timeText}</td>
      <td>${record.depth}-step ${starred}</td>
      <td>${escapeHtml(record.caseName)}</td>
    `;

    recordBody.appendChild(tr);
  });
}

function clearRecords() {
  if (!confirm("確定要清除所有訓練紀錄嗎？")) {
    return;
  }

  records = [];
  lastRecord = null;

  localStorage.removeItem(STORAGE_RECORDS_KEY);

  prevTime.textContent = "-";
  prevDepth.textContent = "-";
  prevCase.textContent = "-";
  prevScramble.textContent = "-";
  prevSolution.textContent = "-";
  prevNote.textContent = "-";

  if (prevCanvas) {
    prevCanvas.style.display = "none";
  }

  starButton.disabled = true;
  starButton.classList.remove("starred");
  starButton.textContent = "☆ 加入星星複習";

  recordBody.innerHTML = "";
  updateStats();
}

function clearStars() {
  if (!confirm("確定要清除所有星星標記嗎？")) {
    return;
  }

  starredCases = new Set();
  localStorage.removeItem(STORAGE_STARS_KEY);

  updateStarButton();
  updateActiveCases();
  renderRecords();

  if (activeCases.length === 0) {
    caseTitle.textContent = "目前沒有符合條件的題目";
    scrambleText.textContent = "請取消星星篩選，或重新標記星星題";
    hideCurrentImage();
    return;
  }

  nextCase();
}

// ===============================
// 星星功能
// ===============================
function getCaseKey(item) {
  return [
    item.depth || "",
    item.scramble || "",
    item.solution || ""
  ].join("||");
}

function toggleLastRecordStar() {
  if (!lastRecord) return;

  const key = getCaseKey(lastRecord);

  if (starredCases.has(key)) {
    starredCases.delete(key);
  } else {
    starredCases.add(key);
  }

  saveStarsToStorage();
  updateStarButton();
  updateActiveCases();
  renderRecords();
}

function updateStarButton() {
  if (!lastRecord) {
    starButton.disabled = true;
    starButton.classList.remove("starred");
    starButton.textContent = "☆ 加入星星複習";
    return;
  }

  const key = getCaseKey(lastRecord);
  const isStarred = starredCases.has(key);

  starButton.disabled = false;

  if (isStarred) {
    starButton.classList.add("starred");
    starButton.textContent = "★ 已加入星星複習";
  } else {
    starButton.classList.remove("starred");
    starButton.textContent = "☆ 加入星星複習";
  }
}

// ===============================
// localStorage
// ===============================
function saveRecordsToStorage() {
  localStorage.setItem(STORAGE_RECORDS_KEY, JSON.stringify(records));
}

function loadRecordsFromStorage() {
  const raw = localStorage.getItem(STORAGE_RECORDS_KEY);

  if (!raw) {
    records = [];
    return;
  }

  try {
    records = JSON.parse(raw) || [];
  } catch {
    records = [];
  }
}

function saveStarsToStorage() {
  localStorage.setItem(
    STORAGE_STARS_KEY,
    JSON.stringify(Array.from(starredCases))
  );
}

function loadStarsFromStorage() {
  const raw = localStorage.getItem(STORAGE_STARS_KEY);

  if (!raw) {
    starredCases = new Set();
    return;
  }

  try {
    starredCases = new Set(JSON.parse(raw) || []);
  } catch {
    starredCases = new Set();
  }
}

// ===============================
// 鍵盤控制
// ===============================
document.addEventListener("keydown", function(event) {
  if (isTypingInput()) {
    return;
  }

  if (event.code === "Space") {
    event.preventDefault();

    // 防止長按空白鍵一直觸發
    if (event.repeat) return;

    if (timerState === "idle") {
      prepareTimer();
      return;
    }

    if (timerState === "running") {
      stopTimer();
      return;
    }
  }

  if (event.key.toLowerCase() === "n") {
    nextCase();
  }

  if (event.key.toLowerCase() === "r") {
    resetTimer();
  }
});

document.addEventListener("keyup", function(event) {
  if (isTypingInput()) {
    return;
  }

  if (event.code === "Space") {
    event.preventDefault();

    if (timerState === "ready") {
      startTimer();
    }
  }
});

// ===============================
// 頁面載入
// ===============================
window.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadSkewbGeometry();

    loadRecordsFromStorage();
    loadStarsFromStorage();

    renderRecords();
    updateStats();

    if (records.length > 0) {
      lastRecord = records[records.length - 1];
      updatePrevious(lastRecord);
    } else {
      updateStarButton();
    }

    loadSelectedDatasets();

  } catch (error) {
    console.error(error);
    caseTitle.textContent = "Skewb 幾何資料載入失敗";
    scrambleText.textContent = "請確認 skewb_geometry.json 是否存在";
    hideCurrentImage();
  }
});
