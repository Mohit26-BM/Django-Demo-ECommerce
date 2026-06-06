/* ============================================================
   MyShop — main.js
   ============================================================ */

/* ── Qty controls ─────────────────────────────────────────── */
function adjustQty(btn, delta) {
  const input = btn.closest('.qty-controls').querySelector('.qty-input');
  input.value = Math.max(1, Math.min(99, parseInt(input.value || 1) + delta));
  input.classList.add('qty-bump');
  setTimeout(() => input.classList.remove('qty-bump'), 200);
}

/* ── Page fade-in ─────────────────────────────────────────── */
document.documentElement.style.opacity = '0';
window.addEventListener('load', () => {
  document.documentElement.style.transition = 'opacity 320ms ease';
  document.documentElement.style.opacity   = '1';
});

document.addEventListener('DOMContentLoaded', () => {

  /* ── Auto-dismiss alerts ──────────────────────────────── */
  document.querySelectorAll('.alert-dismissible').forEach(el => {
    setTimeout(() => bootstrap.Alert.getOrCreateInstance(el).close(), 4000);
  });

  /* ── Navbar: add shadow on scroll ────────────────────── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => {
      if (window.scrollY > 10) {
        navbar.style.boxShadow = '0 2px 16px rgba(0,0,0,.35)';
      } else {
        navbar.style.boxShadow = '';
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Back-to-top button ───────────────────────────────── */
  const btt = document.createElement('button');
  btt.className = 'back-to-top';
  btt.setAttribute('aria-label', 'Back to top');
  btt.innerHTML = '<i class="bi bi-chevron-up"></i>';
  document.body.appendChild(btt);

  window.addEventListener('scroll', () => {
    btt.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  /* ── Scroll-reveal for cards / sections ──────────────── */
  const revealOpts = { threshold: 0.08, rootMargin: '0px 0px -40px 0px' };
  const revealIO = new IntersectionObserver((entries, io) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        io.unobserve(entry.target);
      }
    });
  }, revealOpts);

  document.querySelectorAll(
    '.product-card, .order-card, .card, .trust-item, .payment-chip, section'
  ).forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${Math.min(i % 6, 5) * 55}ms`;
    revealIO.observe(el);
  });

  /* ── Add-to-cart button: loading state ───────────────── */
  document.querySelectorAll('form[action*="add_to_cart"]').forEach(form => {
    form.addEventListener('submit', function () {
      const btn = this.querySelector('button[type="submit"]');
      if (!btn || btn.disabled) return;
      const original = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
      setTimeout(() => {
        btn.innerHTML = '<i class="bi bi-check2"></i>';
        btn.style.background = 'var(--color-success)';
      }, 400);
      setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = original;
        btn.style.background = '';
      }, 1500);
    });
  });

  /* ── Ripple effect on .btn-primary / .btn-success ────── */
  document.querySelectorAll('.btn-primary, .btn-success, .btn-accent').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const r = document.createElement('span');
      r.className = 'btn-ripple';
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size / 2}px;top:${e.clientY - rect.top - size / 2}px`;
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(r);
      setTimeout(() => r.remove(), 600);
    });
  });

  /* ── Smooth image fade-in when loaded ────────────────── */
  document.querySelectorAll('.product-img-wrap img, .product-detail-img').forEach(img => {
    if (img.complete) {
      img.classList.add('img-loaded');
    } else {
      img.addEventListener('load', () => img.classList.add('img-loaded'));
    }
  });

  /* ── Category strip: hide scrollbar arrow hint on mobile */
  const strip = document.querySelector('.category-strip');
  if (strip && strip.scrollWidth > strip.clientWidth) {
    strip.classList.add('has-overflow');
  }

  /* ── Checkout payment option — restore selection style ── */
  document.querySelectorAll('.payment-option input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function () {
      document.querySelectorAll('.payment-option').forEach(el => {
        el.style.borderColor = '';
        el.style.background  = '';
      });
      if (this.checked) {
        const opt = this.closest('.payment-option');
        opt.style.borderColor = 'var(--color-primary)';
        opt.style.background  = 'var(--color-primary-light)';
      }
    });
  });
  document.querySelector('.payment-option input:checked')
    ?.dispatchEvent(new Event('change'));

  /* ── Password show/hide toggle ───────────────────────── */
  document.querySelectorAll('.pwd-toggle').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.closest('.auth-input-wrap').querySelector('input');
      const show  = input.type === 'password';
      input.type  = show ? 'text' : 'password';
      this.querySelector('i').className = show ? 'bi bi-eye-slash' : 'bi bi-eye';
      this.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });

  /* ── Cart badge micro-bounce on page load ─────────────── */
  const badge = document.querySelector('.cart-badge');
  if (badge && parseInt(badge.textContent) > 0) {
    badge.classList.add('badge-bounce');
    setTimeout(() => badge.classList.remove('badge-bounce'), 600);
  }

  /* ── Stagger product-scroller cards ──────────────────── */
  document.querySelectorAll('.product-scroller').forEach(scroller => {
    scroller.querySelectorAll('.product-card').forEach((card, i) => {
      card.style.animationDelay = `${i * 60}ms`;
    });
  });

});
