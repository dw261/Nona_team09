const dimmed = document.getElementById("dimmed");

/* sort bottom sheet */
const sortOpenBtn = document.getElementById("sortOpenBtn");
const sortCloseBtn = document.getElementById("sortCloseBtn");
const sortSheet = document.getElementById("sortSheet");
const sortOptions = document.querySelectorAll(".sort-option");

function closeSortSheet() {
  if (sortSheet) sortSheet.classList.remove("show");

  if (dimmed && (!categorySheet || !categorySheet.classList.contains("show"))) {
    dimmed.classList.remove("show");
  }
}

if (sortOpenBtn && sortSheet && dimmed) {
  sortOpenBtn.addEventListener("click", () => {
    sortSheet.classList.add("show");
    dimmed.classList.add("show");
  });
}

if (sortCloseBtn) {
  sortCloseBtn.addEventListener("click", closeSortSheet);
}

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

    if (sortOpenBtn && option.dataset.sortLabel) {
      sortOpenBtn.textContent = option.dataset.sortLabel;
    }

    if (option.dataset.sort) {
      const url = new URL(window.location.href);
      url.searchParams.set("sort", option.dataset.sort);
      window.location.href = url.toString();
      return;
    }

    closeSortSheet();
  });
});

/* home write menu */
const writeOpenBtn = document.getElementById("writeOpenBtn");
const writeMenu = document.getElementById("writeMenu");

if (writeOpenBtn && writeMenu) {
  writeOpenBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    writeMenu.classList.toggle("show");
  });

  document.addEventListener("click", (event) => {
    if (!writeMenu.contains(event.target) && event.target !== writeOpenBtn) {
      writeMenu.classList.remove("show");
    }
  });
}

/* heart buttons */
document.querySelectorAll(".heart-btn").forEach((button) => {
  button.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();

    button.classList.toggle("active");
    button.textContent = button.classList.contains("active") ? "♥" : "♡";

    const url = button.dataset.url;
    if (!url) return;

    try {
      await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
      });
    } catch (error) {
      button.classList.toggle("active");
      button.textContent = button.classList.contains("active") ? "♥" : "♡";
    }
  });
});

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];

  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.slice(name.length + 1));
    }
  }

  return "";
}

/* image preview */
const imageInput = document.querySelector("[data-image-input]");
const imageUpload = document.querySelector("[data-image-upload]");
const imagePreview = document.querySelector(".image-preview");
const imageUploadText = document.querySelector(".image-upload-text");

if (imageInput && imageUpload && imagePreview) {
  imageInput.addEventListener("change", () => {
    const file = imageInput.files && imageInput.files[0];
    if (!file) return;

    imagePreview.src = URL.createObjectURL(file);
    imagePreview.hidden = false;

    if (imageUploadText) imageUploadText.hidden = true;

    imageUpload.classList.add("has-image");
  });
}

/* people / quantity control */
const minusBtn = document.getElementById("minusBtn");
const plusBtn = document.getElementById("plusBtn");
const peopleCount = document.getElementById("peopleCount");
const peopleSubText = document.getElementById("peopleSubText");
const peopleRange = document.getElementById("peopleRange");

let count = peopleRange ? Number(peopleRange.value) : 4;

function updatePeopleCount(value) {
  if (!peopleRange) return;

  const min = Number(peopleRange.min);
  const max = Number(peopleRange.max);
  const unit = peopleRange.dataset.unit || "명";

  count = Math.min(Math.max(Number(value), min), max);

  if (peopleCount) {
    peopleCount.textContent = `${count}${unit}`;
  }

  if (peopleSubText) {
    peopleSubText.textContent =
      unit === "개" ? `최대 ${max}개` : `${count}명 모집`;
  }

  peopleRange.value = count;
}

if (minusBtn && plusBtn && peopleRange) {
  minusBtn.addEventListener("click", () => updatePeopleCount(count - 1));
  plusBtn.addEventListener("click", () => updatePeopleCount(count + 1));

  peopleRange.addEventListener("input", (event) => {
    updatePeopleCount(event.target.value);
  });

  updatePeopleCount(count);
}

/* category bottom sheet */
const categoryOpenBtn = document.getElementById("categoryOpenBtn");
const categorySheet = document.getElementById("categorySheet");
const categoryResetBtn = document.getElementById("categoryResetBtn");
const categoryApplyBtn = document.getElementById("categoryApplyBtn");
const categoryButtons = document.querySelectorAll(".category");
const categorySheetOptions = document.querySelectorAll(
  ".category-sheet-option",
);
const categoryInput = document.getElementById("categoryInput");

let selectedCategory = categoryInput ? categoryInput.value : "야채";
let pendingCategory = selectedCategory;

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
    button.classList.toggle("active", button.dataset.category === category);
  });

  if (categoryInput) {
    categoryInput.value = category;
  }
}

function updateCategorySheetSelection(category) {
  categorySheetOptions.forEach((option) => {
    const isSelected = option.dataset.category === category;
    option.classList.toggle("selected", isSelected);

    const checkBox = option.querySelector("strong");
    if (checkBox) {
      checkBox.textContent = isSelected ? "✓" : "";
    }
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
    pendingCategory = option.dataset.category;
    updateCategorySheetSelection(pendingCategory);
  });
});

if (categoryResetBtn) {
  categoryResetBtn.addEventListener("click", () => {
    pendingCategory = "야채";
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

/* editable inputs */
document.querySelectorAll(".info-input").forEach((input) => {
  input.addEventListener("focus", () => input.select());
});
