// Toggle user menu
const btn = document.getElementById('userMenuButton');
const menu = document.getElementById('userMenu');
btn.addEventListener('click', () => {
  menu.classList.toggle('hidden');
});

// Slider logic
const sliderWrapper = document.getElementById("sliderWrapper");
const dots = document.querySelectorAll(".dot");
let currentIndex = 0;

function changeSlide(index) {
  currentIndex = index;
  const slideWidth = document.querySelector("#sliderWrapper img").clientWidth;
  const offset = -index * slideWidth;
  sliderWrapper.style.transform = `translateX(${offset}px)`;
  updateDots();
}

function updateDots() {
  dots.forEach((dot, i) => {
    if (i === currentIndex) {
      dot.classList.add("bg-green-500");
      dot.classList.remove("bg-gray-300");
    } else {
      dot.classList.add("bg-gray-300");
      dot.classList.remove("bg-green-500");
    }
  });
}

// Khởi tạo
updateDots();