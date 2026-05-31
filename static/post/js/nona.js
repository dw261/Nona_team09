const dimmed = document.getElementById("dimmed");

/* sort bottom sheet */
const sortOpenBtn = document.getElementById("sortOpenBtn");
const sortCloseBtn = document.getElementById("sortCloseBtn");
const sortSheet = document.getElementById("sortSheet");
const sortOptions = document.querySelectorAll(".sort-option");

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
const categorySearchInput = document.getElementById("categorySearchInput");

function closeSortSheet() {
  if (sortSheet) sortSheet.classList.remove("show");

  if (dimmed && (!categorySheet || !categorySheet.classList.contains("show"))) {
    dimmed.classList.remove("show");
  }
}

function closeCategorySheet() {
  if (categorySheet) categorySheet.classList.remove("show");

  if (dimmed && (!sortSheet || !sortSheet.classList.contains("show"))) {
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

const currentSort =
  new URLSearchParams(window.location.search).get("sort") || "latest";

sortOptions.forEach((option) => {
  const isSelected = option.dataset.sort === currentSort;
  option.classList.toggle("selected", isSelected);

  const checkBox = option.querySelector("strong");
  if (checkBox) checkBox.textContent = isSelected ? "✓" : "";

  if (isSelected && sortOpenBtn && option.dataset.sortLabel) {
    sortOpenBtn.textContent = option.dataset.sortLabel;
  }

  option.addEventListener("click", () => {
    sortOptions.forEach((item) => {
      item.classList.remove("selected");

      const itemCheckBox = item.querySelector("strong");
      if (itemCheckBox) itemCheckBox.textContent = "";
    });

    option.classList.add("selected");

    const selectedCheckBox = option.querySelector("strong");
    if (selectedCheckBox) selectedCheckBox.textContent = "✓";

    if (sortOpenBtn && option.dataset.sortLabel) {
      sortOpenBtn.textContent = option.dataset.sortLabel;
    }

    if (option.dataset.sort) {
      const params = new URLSearchParams(window.location.search);
      params.set("sort", option.dataset.sort);

      window.location.href = `${window.location.pathname}?${params.toString()}`;
    } else {
      closeSortSheet();
    }
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

    if (!button.dataset.authenticated) {
      window.location.href = button.dataset.loginUrl || '/accounts/login/';
      return;
    }

    const iconTarget = button.querySelector(".heart-icon") || button;
    const countTarget = button.querySelector(".heart-count");

    button.classList.toggle("active");
    iconTarget.textContent = button.classList.contains("active") ? "♥" : "♡";

    if (countTarget) {
      const currentCount = Number(countTarget.textContent || 0);
      countTarget.textContent = button.classList.contains("active")
        ? currentCount + 1
        : Math.max(currentCount - 1, 0);
    }

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
      iconTarget.textContent = button.classList.contains("active") ? "♥" : "♡";

      if (countTarget) {
        const currentCount = Number(countTarget.textContent || 0);
        countTarget.textContent = button.classList.contains("active")
          ? currentCount + 1
          : Math.max(currentCount - 1, 0);
      }
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
let selectedCategory = categoryInput ? categoryInput.value : null;
let pendingCategory = selectedCategory;

function updateCategoryChips(category) {
  categoryButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.category === category);
  });

  if (categoryInput && category) {
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

function openCategorySheet() {
  if (!categorySheet || !dimmed) return;

  pendingCategory = selectedCategory;
  updateCategorySheetSelection(pendingCategory);

  categorySheet.classList.add("show");
  dimmed.classList.add("show");
}

if (categoryOpenBtn) {
  categoryOpenBtn.addEventListener("click", openCategorySheet);
}

categoryButtons.forEach((button) => {
  button.addEventListener("click", () => {
    pendingCategory = button.dataset.category;
    selectedCategory = pendingCategory;

    updateCategoryChips(selectedCategory);
    updateCategorySheetSelection(selectedCategory);
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
    pendingCategory = selectedCategory;
    updateCategorySheetSelection(pendingCategory);
  });
}

if (categoryApplyBtn) {
  categoryApplyBtn.addEventListener("click", () => {
    if (pendingCategory) {
      selectedCategory = pendingCategory;
      updateCategoryChips(selectedCategory);
    }

    closeCategorySheet();
  });
}

if (categorySearchInput) {
  categorySearchInput.addEventListener("input", () => {
    const keyword = categorySearchInput.value.trim().toLowerCase();

    categorySheetOptions.forEach((option) => {
      const label = (
        option.dataset.label ||
        option.textContent ||
        ""
      ).toLowerCase();

      option.style.display = label.includes(keyword) ? "" : "none";
    });
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

const contentTextarea = document.querySelector(
  'textarea[name="content"], textarea[name="description"]',
);
const textareaCount = document.querySelector(".textarea-count");

if (contentTextarea && textareaCount) {
  contentTextarea.addEventListener("input", () => {
    textareaCount.textContent = `${contentTextarea.value.length} / ${contentTextarea.maxLength}`;
  });
}

/* editable inputs */
document.querySelectorAll(".info-input").forEach((input) => {
  input.addEventListener("focus", () => {
    if (input.type !== "date" && input.type !== "time") {
      input.select();
    }
  });
});

/* cancel button */
const cancelBtn = document.getElementById("cancelBtn");

if (cancelBtn) {
  cancelBtn.addEventListener("click", () => {
    const url = cancelBtn.dataset.url;
    if (url) window.location.href = url;
  });
}

/* default deadline */
document.addEventListener("DOMContentLoaded", () => {
  const dateInput = document.getElementById("deadlineDate");
  const timeInput = document.getElementById("deadlineTime");

  if (dateInput && timeInput && !dateInput.value && !timeInput.value) {
    const now = new Date();

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const formattedDate = `${year}-${month}-${day}`;

    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const formattedTime = `${hours}:${minutes}`;

    dateInput.value = formattedDate;
    timeInput.value = formattedTime;
  }
});
document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.querySelector('.delete-btn');

    if (deleteBtn) {
        deleteBtn.addEventListener('click', function () {
            if (!confirm('정말 이 게시글을 삭제하시겠습니까?')) {
                return;
            }

            const postId = this.getAttribute('data-id');
            const postType = this.getAttribute('data-type'); // 'group' 또는 'shares'
            const csrftoken = getCookie('csrftoken'); 

            // 규칙적인 URL 생성
            const url = `/posts/${postType}/${postId}/delete/`;

            // 서버로 삭제 요청 (동일한 폼으로 처리)
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('삭제 권한이 없거나 오류가 발생했습니다.');
                }
            })
            .then(data => {
                // 서버가 보낸 성공 메시지 알림
                alert(data.message);
                
                // 삭제 완료 후 각 카테고리의 목록 페이지로 이동
                window.location.href = `/posts/${postType}/`; 
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || '오류가 발생했습니다. 다시 시도해 주세요.');
            });
        });
    }
});

// CSRF 토큰 획득 함수 (기존과 동일)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}