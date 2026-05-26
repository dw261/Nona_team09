const sortOpenBtn = document.getElementById("sortOpenBtn");
const sortCloseBtn = document.getElementById("sortCloseBtn");
const sortSheet = document.getElementById("sortSheet");
const dimmed = document.getElementById("dimmed");

if (sortOpenBtn && sortSheet && dimmed) {
  sortOpenBtn.addEventListener("click", () => {
    sortSheet.classList.add("show");
    dimmed.classList.add("show");
  });
}

if (sortCloseBtn && sortSheet && dimmed) {
  sortCloseBtn.addEventListener("click", closeSortSheet);
  dimmed.addEventListener("click", closeSortSheet);
}

function closeSortSheet() {
  sortSheet.classList.remove("show");
  dimmed.classList.remove("show");
}

const sortOptions = document.querySelectorAll(".sort-option");

sortOptions.forEach((option) => {
  option.addEventListener("click", () => {
    sortOptions.forEach((item) => {
      item.classList.remove("selected");
      item.querySelector("strong").textContent = "";
    });

    option.classList.add("selected");
    option.querySelector("strong").textContent = "✓";
  });
});

const minusBtn = document.getElementById("minusBtn");
const plusBtn = document.getElementById("plusBtn");
const peopleCount = document.getElementById("peopleCount");
const peopleRange = document.getElementById("peopleRange");

let count = 4;

function updatePeopleCount(value) {
  count = Number(value);
  if (peopleCount) peopleCount.textContent = `${count}명`;
  if (peopleRange) peopleRange.value = count;
}

if (minusBtn && plusBtn && peopleRange) {
  minusBtn.addEventListener("click", () => {
    if (count > 2) updatePeopleCount(count - 1);
  });

  plusBtn.addEventListener("click", () => {
    if (count < 10) updatePeopleCount(count + 1);
  });

  peopleRange.addEventListener("input", (event) => {
    updatePeopleCount(event.target.value);
  });
}
