document.addEventListener('DOMContentLoaded', function () {
  console.log('🌱 Green Campus website đã tải xong!');

  // ------------------------------
  // Cuộn mượt khi bấm nav-link
  // ------------------------------
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function (e) {
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

  // ------------------------------
  // Xử lý LIKE ảnh qua API Flask
  // ------------------------------
  function attachLikeHandlers() {
    const likeDivs = document.querySelectorAll('.likes');

    likeDivs.forEach(div => {
      // Gỡ sự kiện cũ (nếu có) để tránh nhân đôi
      div.removeEventListener('click', div._likeHandler);

      // Định nghĩa sự kiện click
      const handler = async () => {
        const postItem = div.closest('.post-item');
        if (!postItem) return;

        const imageId = div.getAttribute('data-id');
        if (!imageId) return;

        try {
          const resp = await fetch(`/like/${imageId}`, { method: 'POST' });

          // Nếu lỗi quyền truy cập
          if (!resp.ok) {
            const json = await resp.json().catch(() => ({}));
            alert(json.msg || '⚠️ Bạn cần đăng nhập để like ảnh!');
            return;
          }

          const data = await resp.json();
          if (data.ok) {
            const countSpan = div.querySelector('.like-count');
            countSpan.textContent = data.likes;

            // Hiệu ứng khi like
            div.classList.add('liked');
            setTimeout(() => div.classList.remove('liked'), 400);
          } else {
            alert(data.msg || 'Không thể like ảnh này!');
          }
        } catch (err) {
          console.error('❌ Lỗi khi gửi yêu cầu like:', err);
        }
      };

      // Gắn sự kiện mới
      div.addEventListener('click', handler);
      div._likeHandler = handler;
    });
  }

  // Gọi khi trang tải
  attachLikeHandlers();

  // ------------------------------
  // Xem trước ảnh khi upload
  // ------------------------------
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
    // ------------------------------
  // Gửi form upload qua fetch + hiện flashbox
  // ------------------------------
  const uploadForm = document.getElementById('upload-form');
  const flashbox = document.getElementById('flashbox');
  const flashMsg = document.getElementById('flash-message');

  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault(); // chặn reload
      const formData = new FormData(uploadForm);

      try {
        const resp = await fetch(uploadForm.action, {
          method: 'POST',
          body: formData
        });

        if (resp.ok) {
          showFlash("📨 Ảnh của bạn đã được gửi, vui lòng kiên nhẫn đợi quản trị viên xử lý 💚");
          uploadForm.reset();
          document.getElementById('preview').innerHTML = '';
        } else {
          showFlash("⚠️ Gửi ảnh thất bại, vui lòng thử lại sau!", true);
        }
      } catch (err) {
        console.error('❌ Lỗi khi gửi form:', err);
        showFlash("Ảnh đã được gửi thành công,bạn chờ quản trị viên duyệt chút xíu nha", true);
      }
    });
  }

  // ------------------------------
  // Hàm hiển thị flashbox
  // ------------------------------
  function showFlash(message, isError = false) {
    if (!flashbox) return;
    flashMsg.textContent = message;
    flashbox.style.backgroundColor = isError ? '#e74c3c' : '#4caf50';
    flashbox.classList.remove('hidden');
    flashbox.classList.add('show');

    setTimeout(() => {
      flashbox.classList.remove('show');
      setTimeout(() => flashbox.classList.add('hidden'), 400);
    }, 3000);
  }
});