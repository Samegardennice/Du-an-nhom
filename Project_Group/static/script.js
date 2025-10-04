document.addEventListener('DOMContentLoaded', function () {
  console.log('Green Campus website đã tải xong!');

  // ===== Scroll mượt + Active nav =====
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      if (this.hash) {
        e.preventDefault();
        const target = document.querySelector(this.hash);
        if (target) {
          window.scrollTo({
            top: target.offsetTop - 80,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // ===== Like bằng API =====
  function attachLikeHandlers() {
    const likeDivs = document.querySelectorAll('.likes');
    likeDivs.forEach(div => {
      div.removeEventListener('click', div._likeHandler); // remove old if any
      const handler = async () => {
        const postItem = div.closest('.post-item');
        if (!postItem) return;
        const imageId = postItem.getAttribute('data-image-id');
        if (!imageId) return;
        try {
          const resp = await fetch(`/like/${imageId}`, { method: 'POST' });
          if (!resp.ok) {
            const json = await resp.json().catch(()=>({}));
            alert(json.msg || 'Không thể like (cần đăng nhập).');
            return;
          }
          const data = await resp.json();
          if (data.ok) {
            const countSpan = div.querySelector('.like-count');
            countSpan.textContent = data.likes;
            div.classList.add('liked');
            setTimeout(()=> div.classList.remove('liked'), 400);
          }
        } catch (e) {
          console.error(e);
        }
      };
      div.addEventListener('click', handler);
      div._likeHandler = handler;
    });
  }
  attachLikeHandlers();

  // ===== Preview ảnh trên upload form =====
  const imageInput = document.getElementById('image');
  const preview = document.getElementById('preview');
  if (imageInput) {
    imageInput.addEventListener('change', () => {
      preview.innerHTML = '';
      const file = imageInput.files[0];
      if (file) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = '100%';
        img.style.marginTop = '10px';
        preview.appendChild(img);
      }
    });
  }


  // 🌿 Sự kiện LIKE ảnh
document.addEventListener("click", (e) => {
  const likeBtn = e.target.closest(".likes");
  if (!likeBtn) return;

  const imageId = likeBtn.dataset.id;
  if (!imageId) return;

  fetch(`/like/${imageId}`, {
    method: "POST",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.ok) {
        const count = likeBtn.querySelector(".like-count");
        count.textContent = data.likes;
        likeBtn.classList.add("liked");
      } else {
        alert(data.msg || "Không thể like ảnh này!");
      }
    })
    .catch((err) => console.error("Lỗi khi gửi yêu cầu like:", err));
});

  // Nếu sau khi upload có nội dung động được thêm, re-attach like handlers
  // (useful if you later change to return new HTML via AJAX)
  // call attachLikeHandlers() after DOM updates if needed
});
