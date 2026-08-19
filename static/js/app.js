// ---------- Tabs ----------
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");

    if (tab.dataset.tab === "closet") loadWardrobe();
    if (tab.dataset.tab === "insights") loadInsights();
  });
});

// ---------- Pill single-select helper ----------
function setupPillGroup(groupEl) {
  const pills = groupEl.querySelectorAll(".pill");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
    });
  });
}
setupPillGroup(document.getElementById("occasion-group"));
setupPillGroup(document.getElementById("mood-group"));

function selectedPillValue(groupEl) {
  const active = groupEl.querySelector(".pill.active");
  return active ? active.dataset.value : "";
}

// ---------- AI Stylist ----------
const getOutfitBtn = document.getElementById("get-outfit-btn");
const tryAnotherBtn = document.getElementById("try-another-btn");
const resultEmpty = document.getElementById("result-empty");
const resultFilled = document.getElementById("result-filled");
const outfitText = document.getElementById("outfit-text");
const weatherBadge = document.getElementById("weather-badge");

async function requestOutfit() {
  const occasion = selectedPillValue(document.getElementById("occasion-group"));
  const mood = selectedPillValue(document.getElementById("mood-group"));
  const preferences = document.getElementById("preferences").value;
  const city = document.getElementById("city").value;
  const manual_weather = document.getElementById("manual-weather").value;

  getOutfitBtn.disabled = true;
  getOutfitBtn.textContent = "Styling...";

  try {
    const res = await fetch("/api/outfit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ occasion, mood, preferences, city, manual_weather }),
    });
    const data = await res.json();

    if (data.weather) {
      weatherBadge.textContent = `${data.weather.temp}°C · ${data.weather.description} · ${data.weather.city}`;
      weatherBadge.classList.remove("hidden");
    } else if (data.weather_text) {
      weatherBadge.textContent = data.weather_text;
      weatherBadge.classList.remove("hidden");
    } else {
      weatherBadge.classList.add("hidden");
    }

    outfitText.textContent = data.outfit;
    resultEmpty.classList.add("hidden");
    resultFilled.classList.remove("hidden");
  } catch (err) {
    outfitText.textContent = "Something went wrong reaching the stylist. Please try again.";
    resultEmpty.classList.add("hidden");
    resultFilled.classList.remove("hidden");
  } finally {
    getOutfitBtn.disabled = false;
    getOutfitBtn.textContent = "✨ Get My Outfit";
  }
}

getOutfitBtn.addEventListener("click", requestOutfit);
tryAnotherBtn.addEventListener("click", requestOutfit);

// ---------- My Closet ----------
const wardrobeGrid = document.getElementById("wardrobe-grid");
const categoryFilter = document.getElementById("category-filter");
let currentCategory = "All";
let wardrobeCache = [];

setupPillGroup(categoryFilter);
categoryFilter.addEventListener("click", (e) => {
  if (e.target.classList.contains("pill")) {
    currentCategory = e.target.dataset.value;
    renderWardrobe();
  }
});

async function loadWardrobe() {
  const res = await fetch("/api/wardrobe");
  wardrobeCache = await res.json();
  renderWardrobe();
}

function renderWardrobe() {
  const items = currentCategory === "All"
    ? wardrobeCache
    : wardrobeCache.filter((i) => i.category === currentCategory);

  wardrobeGrid.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "wardrobe-card";
    card.innerHTML = `
      <div class="wardrobe-avatar">${item.name.charAt(0).toUpperCase()}</div>
      <div class="wardrobe-name">${item.name}</div>
      <div class="wardrobe-category">${item.category}</div>
      <div class="wardrobe-worn">${item.worn > 0 ? `worn ${item.worn}x` : "never worn"}</div>
      <div class="wardrobe-actions">
        <button class="wear-btn" data-id="${item.id}">✓ Worn</button>
        <button class="delete-btn" data-id="${item.id}">✕</button>
      </div>
    `;
    wardrobeGrid.appendChild(card);
  });

  wardrobeGrid.querySelectorAll(".wear-btn").forEach((btn) => {
    btn.addEventListener("click", () => markWorn(btn.dataset.id));
  });
  wardrobeGrid.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => deleteItem(btn.dataset.id));
  });
}

async function markWorn(id) {
  const res = await fetch(`/api/wardrobe/${id}/wear`, { method: "POST" });
  const updated = await res.json();
  wardrobeCache = wardrobeCache.map((i) => (i.id === id ? updated : i));
  renderWardrobe();
}

async function deleteItem(id) {
  await fetch(`/api/wardrobe/${id}`, { method: "DELETE" });
  wardrobeCache = wardrobeCache.filter((i) => i.id !== id);
  renderWardrobe();
}

// Add item modal
const modal = document.getElementById("add-item-modal");
document.getElementById("add-item-btn").addEventListener("click", () => modal.classList.remove("hidden"));
document.getElementById("cancel-add-item").addEventListener("click", () => modal.classList.add("hidden"));

document.getElementById("confirm-add-item").addEventListener("click", async () => {
  const name = document.getElementById("new-item-name").value.trim();
  const category = document.getElementById("new-item-category").value;
  const priceRaw = document.getElementById("new-item-price").value;
  const price = priceRaw ? parseFloat(priceRaw) : null;

  if (!name) return;

  const res = await fetch("/api/wardrobe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, category, price }),
  });
  const newItem = await res.json();
  wardrobeCache.push(newItem);
  renderWardrobe();

  document.getElementById("new-item-name").value = "";
  document.getElementById("new-item-price").value = "";
  modal.classList.add("hidden");
});

// ---------- Insights ----------
async function loadInsights() {
  const res = await fetch("/api/insights");
  const data = await res.json();

  document.getElementById("stat-total-items").textContent = data.total_items;
  document.getElementById("stat-total-wears").textContent = data.total_wears;

  renderBarList("most-worn-list", data.most_worn, data.most_worn[0]?.worn || 1, "worn");
  renderBarList("least-worn-list", data.least_worn, data.most_worn[0]?.worn || 1, "worn");

  const neverList = document.getElementById("never-worn-list");
  neverList.innerHTML = data.never_worn.map((i) => `<li>${i.name}</li>`).join("");

  const maxCategoryCount = Math.max(1, ...Object.values(data.category_breakdown));
  const catList = document.getElementById("category-list");
  catList.innerHTML = Object.entries(data.category_breakdown).map(([cat, count]) => `
    <li>
      <div class="bar-row-label"><span>${cat}</span><span>${count}</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${(count / maxCategoryCount) * 100}%"></div></div>
    </li>
  `).join("");
}

function renderBarList(elId, items, max, unitLabel) {
  const el = document.getElementById(elId);
  if (!items || items.length === 0) {
    el.innerHTML = `<li style="color:#8a7a85; font-size:12px;">Not enough data yet.</li>`;
    return;
  }
  el.innerHTML = items.map((i) => `
    <li>
      <div class="bar-row-label"><span>${i.name}</span><span>${i.worn}x ${unitLabel}</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${(i.worn / max) * 100}%"></div></div>
    </li>
  `).join("");
}

// Initial load
loadWardrobe();
