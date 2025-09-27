document.addEventListener('DOMContentLoaded', function() {
    console.log('Green Campus website đã tải xong!');

    // Thêm hiệu ứng scroll mượt cho navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    window.scrollTo({
                        top: targetSection.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // ===== Modal đăng nhập / đăng ký =====
    const loginBtn = document.querySelector('.login-btn');       // thêm dòng này
    const registerBtn = document.querySelector('.register-btn'); // thêm dòng này
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const closeBtns = document.querySelectorAll('.close');

    // Khi bấm Đăng nhập
    loginBtn.addEventListener('click', function() {
        loginModal.style.display = 'block';
    });

    // Khi bấm Đăng ký
    registerBtn.addEventListener('click', function() {
        registerModal.style.display = 'block';
    });

    // Khi bấm nút đóng (x)
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            loginModal.style.display = 'none';
            registerModal.style.display = 'none';
        });
    });

    // Khi bấm ra ngoài modal thì đóng lại
    window.addEventListener('click', function(e) {
        if (e.target === loginModal) loginModal.style.display = 'none';
        if (e.target === registerModal) registerModal.style.display = 'none';
    });

    // Xử lý sự kiện cho các nút CTA
    const ctaButtons = document.querySelectorAll('.cta-btn, .secondary-btn, .campaign-btn, .view-all-btn, .contact-btn');
    ctaButtons.forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent;
            switch(buttonText) {
                case 'Bắt đầu hành động xanh':
                    alert('Hướng dẫn bạn bắt đầu hành động xanh ngay bây giờ!');
                    break;
                case 'Tìm hiểu thêm':
                    alert('Giới thiệu chi tiết về Green Campus');
                    break;
                case 'Tham gia ngay':
                    alert('Bạn đã tham gia chiến dịch thành công!');
                    break;
                case 'Xem tất cả chiến dịch':
                    alert('Hiển thị tất cả chiến dịch đang có');
                    break;
                case 'Liên hệ ngay':
                    alert('Kết nối với đội ngũ Green Campus');
                    break;
                default:
                    alert('Tính năng đang được phát triển!');
            }
        });
    });

    // Thêm hiệu ứng khi scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.style.background = 'var(--white)';
            navbar.style.backdropFilter = 'none';
        }

        // Cập nhật active navigation
        const sections = document.querySelectorAll('section');
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (scrollY >= (sectionTop - 100)) {
                current = section.getAttribute('id');
            }
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
});
