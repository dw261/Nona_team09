const dimmed = document.getElementById("dimmed");

/* home sort bottom sheet */
const sortOpenBtn = document.getElementById("sortOpenBtn");
const sortCloseBtn = document.getElementById("sortCloseBtn");
const sortSheet = document.getElementById("sortSheet");

if (sortOpenBtn && sortSheet && dimmed) {
  sortOpenBtn.addEventListener("click", () => {
    sortSheet.classList.add("show");
    dimmed.classList.add("show");
  });
}

if (sortCloseBtn && sortSheet && dimmed) {
  sortCloseBtn.addEventListener("click", closeSortSheet);
}

function closeSortSheet() {
  if (sortSheet) sortSheet.classList.remove("show");
  if (dimmed) dimmed.classList.remove("show");
}

const sortOptions = document.querySelectorAll(".sort-option");

sortOptions.forEach((option) => {
  option.addEventListener("click", () => {
    sortOptions.forEach((item) => {
      item.classList.remove("selected");

      const checkBox = item.querySelector("strong");
      if (checkBox) checkBox.textContent = "";
    });

    option.classList.add("selected");

    const selectedCheckBox = option.querySelector("strong");
    if (selectedCheckBox) selectedCheckBox.textContent = "✓";

    closeSortSheet();
  });
});

/* create page people count */
const minusBtn = document.getElementById("minusBtn");
const plusBtn = document.getElementById("plusBtn");
const peopleCount = document.getElementById("peopleCount");
const peopleRange = document.getElementById("peopleRange");

let count = peopleRange ? Number(peopleRange.value) : 4;

function updatePeopleCount(value) {
  count = Number(value);

  if (peopleCount) {
    peopleCount.textContent = `${count}명`;
  }

  if (peopleRange) {
    peopleRange.value = count;
  }
}

if (minusBtn && plusBtn && peopleRange) {
  minusBtn.addEventListener("click", () => {
    if (count > Number(peopleRange.min)) {
      updatePeopleCount(count - 1);
    }
  });

  plusBtn.addEventListener("click", () => {
    if (count < Number(peopleRange.max)) {
      updatePeopleCount(count + 1);
    }
  });

  peopleRange.addEventListener("input", (event) => {
    updatePeopleCount(event.target.value);
  });

  updatePeopleCount(count);
}

/* create page category chips + bottom sheet */
const categoryOpenBtn = document.getElementById("categoryOpenBtn");
const categorySheet = document.getElementById("categorySheet");
const categoryResetBtn = document.getElementById("categoryResetBtn");
const categoryApplyBtn = document.getElementById("categoryApplyBtn");
const categoryButtons = document.querySelectorAll(".category");
const categorySheetOptions = document.querySelectorAll(
  ".category-sheet-option",
);
const categoryInput = document.getElementById("categoryInput");

let selectedCategory = null;
let pendingCategory = null;

function openCategorySheet() {
  if (!categorySheet || !dimmed) return;

  pendingCategory = selectedCategory;
  updateCategorySheetSelection(pendingCategory);

  categorySheet.classList.add("show");
  dimmed.classList.add("show");
}

function closeCategorySheet() {
  if (categorySheet) categorySheet.classList.remove("show");

  if (dimmed && (!sortSheet || !sortSheet.classList.contains("show"))) {
    dimmed.classList.remove("show");
  }
}

function updateCategoryChips(category) {
  categoryButtons.forEach((button) => {
    button.classList.toggle("active", category !== null && button.dataset.category === category);
  });
 
  if (categoryInput) {
    categoryInput.value = category ?? "";
  }
}

function updateCategorySheetSelection(category) {
  categorySheetOptions.forEach((option) => {
    const isSelected = option.dataset.category === category;
    option.classList.toggle("selected", isSelected);

    const checkBox = option.querySelector("strong");
    if (checkBox) checkBox.textContent = isSelected ? "✓" : "";
  });
}

if (categoryOpenBtn) {
  categoryOpenBtn.addEventListener("click", openCategorySheet);
}

categoryButtons.forEach((button) => {
  button.addEventListener("click", () => {
    pendingCategory = button.dataset.category;
    openCategorySheet();
  });
});

categorySheetOptions.forEach((option) => {
  option.addEventListener("click", () => {
    if (pendingCategory === option.dataset.category) {
      pendingCategory = null;
    } else {
      pendingCategory = option.dataset.category;
    }
    updateCategorySheetSelection(pendingCategory);
  });
});

if (categoryResetBtn) {
  categoryResetBtn.addEventListener("click", () => {
    pendingCategory = null;
    updateCategorySheetSelection(pendingCategory);
  });
}

if (categoryApplyBtn) {
  categoryApplyBtn.addEventListener("click", () => {
    selectedCategory = pendingCategory;
    updateCategoryChips(selectedCategory);
    closeCategorySheet();
  });
}

if (dimmed) {
  dimmed.addEventListener("click", () => {
    closeSortSheet();
    closeCategorySheet();
  });
}

updateCategoryChips(selectedCategory);
updateCategorySheetSelection(selectedCategory);

/* text counters */
const titleInput = document.querySelector('input[name="title"]');
const titleCount = document.querySelector(".input-count-row span");

if (titleInput && titleCount) {
  titleInput.addEventListener("input", () => {
    titleCount.textContent = `${titleInput.value.length} / ${titleInput.maxLength}`;
  });
}

const descriptionTextarea = document.querySelector(
  'textarea[name="description"]',
);
const textareaCount = document.querySelector(".textarea-count");

if (descriptionTextarea && textareaCount) {
  descriptionTextarea.addEventListener("input", () => {
    textareaCount.textContent = `${descriptionTextarea.value.length} / ${descriptionTextarea.maxLength}`;
  });
}

document.querySelectorAll('.sort-option').forEach(btn => {
  btn.addEventListener('click', () => {
    const sort = btn.dataset.sort;
    const url = new URL(window.location.href);
    url.searchParams.set('sort', sort);
    window.location.href = url.toString();
  });
});

document.querySelectorAll(".heart-btn").forEach(btn => {
    btn.addEventListener("click", async function(e){
        // 상세페이지 이동 막기
        e.stopPropagation();
        const url=this.dataset.url;
        const response=await fetch(url,{
            method:"POST",
            headers:{
                "X-CSRFToken":"{{ csrf_token }}",
                "X-Requested-With":"XMLHttpRequest"
            }
        });

        if(response.ok){
            const data=await response.json();
            this.innerText=data.wished ? "♥":"♡";
        }
    });
});