/**
 * Verdant Heritage Organic Farm - Client Application Controller
 * Handles Cart Drawer, Multi-Step Checkout, Auth Modal, CSA Subscriptions,
 * Farm Visits, Live Filters, Toast Notifications, and LocalStorage State.
 */

// --- STATE MANAGEMENT ---
const FarmApp = {
  cart: [],
  currentUser: null,
  productsCache: [],

  init() {
    this.loadCart();
    this.loadCurrentUser();
    this.bindEvents();
    this.updateCartBadge();
    this.renderCartDrawer();
    this.initBackToTop();
  },

  // --- LOCAL STORAGE & USER SYNC ---
  loadCart() {
    try {
      const stored = localStorage.getItem('verdant_cart');
      this.cart = stored ? JSON.parse(stored) : [];
    } catch (e) {
      this.cart = [];
    }
  },

  saveCart() {
    try {
      localStorage.setItem('verdant_cart', JSON.stringify(this.cart));
      this.updateCartBadge();
      this.renderCartDrawer();
      if (window.location.pathname.includes('/checkout')) {
        this.renderCheckoutSummary();
      }
    } catch (e) {
      console.error('Failed to save cart to localStorage', e);
    }
  },

  async loadCurrentUser() {
    try {
      const res = await fetch('/api/auth/me');
      const data = await res.json();
      if (data.success && data.user) {
        this.currentUser = data.user;
        this.updateAuthUI(data.user);
      } else {
        // Check localStorage fallback demo
        const storedUser = localStorage.getItem('verdant_user');
        if (storedUser) {
          this.currentUser = JSON.parse(storedUser);
          this.updateAuthUI(this.currentUser);
        }
      }
    } catch (e) {
      console.warn('Auth check error, offline fallback enabled');
    }
  },

  updateAuthUI(user) {
    const accountBtn = document.getElementById('accountBtn');
    if (accountBtn) {
      if (user) {
        accountBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          <span>${user.name.split(' ')[0]}</span>
        `;
        accountBtn.classList.add('logged-in');
        accountBtn.setAttribute('href', '/account');
      } else {
        accountBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          <span>Account</span>
        `;
        accountBtn.classList.remove('logged-in');
        accountBtn.removeAttribute('href');
      }
    }
  },

  // --- CART OPERATIONS ---
  addToCart(product, quantity = 1) {
    const qty = parseInt(quantity) || 1;
    const existingIndex = this.cart.findIndex(item => item.id === product.id);

    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += qty;
    } else {
      this.cart.push({
        id: product.id,
        name: product.name,
        price: parseFloat(product.price),
        image: product.image,
        unit: product.unit,
        quantity: qty
      });
    }

    this.saveCart();
    this.showToast(`Added ${qty}x ${product.name} to your farm cart!`, 'success');
    this.openCartDrawer();
  },

  removeFromCart(productId) {
    const item = this.cart.find(i => i.id === productId);
    this.cart = this.cart.filter(i => i.id !== productId);
    this.saveCart();
    if (item) {
      this.showToast(`Removed ${item.name} from cart`, 'info');
    }
  },

  updateQuantity(productId, delta) {
    const item = this.cart.find(i => i.id === productId);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      this.removeFromCart(productId);
    } else {
      this.saveCart();
    }
  },

  getCartSubtotal() {
    return this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  },

  getCartCount() {
    return this.cart.reduce((sum, item) => sum + item.quantity, 0);
  },

  updateCartBadge() {
    const count = this.getCartCount();
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(b => {
      b.textContent = count;
      b.style.display = count > 0 ? 'flex' : 'none';
    });
  },

  renderCartDrawer() {
    const container = document.getElementById('cartDrawerItems');
    if (!container) return;

    const subtotal = this.getCartSubtotal();
    const freeDeliveryThreshold = 35.00;
    const deliveryFee = subtotal >= freeDeliveryThreshold || subtotal === 0 ? 0.00 : 5.00;
    const total = subtotal + deliveryFee;

    // Update free delivery progress bar
    const progressFill = document.getElementById('shippingProgressFill');
    const shippingMsg = document.getElementById('shippingProgressText');
    if (progressFill && shippingMsg) {
      if (subtotal >= freeDeliveryThreshold) {
        progressFill.style.width = '100%';
        shippingMsg.innerHTML = '🎉 You unlocked <strong>FREE Farm Delivery!</strong>';
      } else {
        const remaining = (freeDeliveryThreshold - subtotal).toFixed(2);
        const percent = Math.min(100, Math.round((subtotal / freeDeliveryThreshold) * 100));
        progressFill.style.width = `${percent}%`;
        shippingMsg.innerHTML = `Add <strong>$${remaining}</strong> more for Free Delivery`;
      }
    }

    // Render items
    if (this.cart.length === 0) {
      container.innerHTML = `
        <div class="cart-empty-state">
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
          <h4>Your farm basket is empty</h4>
          <p>Explore our fresh morning harvest and seasonal organic specialties.</p>
          <a href="/shop" class="btn btn-primary btn-sm" style="margin-top: 1rem;" onclick="FarmApp.closeCartDrawer()">Shop Fresh Produce</a>
        </div>
      `;
    } else {
      container.innerHTML = this.cart.map(item => `
        <div class="cart-item-row" data-id="${item.id}">
          <img src="${item.image}" alt="${item.name}" class="cart-item-thumb">
          <div class="cart-item-info">
            <h4>${item.name}</h4>
            <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)} <span style="font-size:0.75rem; color:#8d9890;">($${item.price.toFixed(2)} ${item.unit})</span></div>
            <div class="cart-item-controls">
              <div class="qty-stepper">
                <button class="qty-btn" onclick="FarmApp.updateQuantity(${item.id}, -1)">-</button>
                <span class="qty-input">${item.quantity}</span>
                <button class="qty-btn" onclick="FarmApp.updateQuantity(${item.id}, 1)">+</button>
              </div>
              <button class="btn-remove-item" onclick="FarmApp.removeFromCart(${item.id})">Remove</button>
            </div>
          </div>
        </div>
      `).join('');
    }

    // Summary numbers
    const subtotalEl = document.getElementById('cartSubtotalDisplay');
    const deliveryEl = document.getElementById('cartDeliveryDisplay');
    const totalEl = document.getElementById('cartTotalDisplay');
    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (deliveryEl) deliveryEl.textContent = deliveryFee === 0 ? 'FREE' : `$${deliveryFee.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;

    const checkoutBtn = document.getElementById('btnDrawerCheckout');
    if (checkoutBtn) {
      checkoutBtn.disabled = this.cart.length === 0;
      checkoutBtn.style.opacity = this.cart.length === 0 ? '0.5' : '1';
    }
  },

  openCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer && overlay) {
      drawer.classList.add('active');
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },

  closeCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer && overlay) {
      drawer.classList.remove('active');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  // --- AUTH MODAL ---
  openAuthModal(initialTab = 'login') {
    if (this.currentUser) {
      window.location.href = '/account';
      return;
    }
    const modal = document.getElementById('authModal');
    if (modal) {
      modal.classList.add('active');
      this.switchAuthTab(initialTab);
      document.body.style.overflow = 'hidden';
    }
  },

  closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  switchAuthTab(tabName) {
    const tabs = document.querySelectorAll('.auth-tab-btn');
    const views = document.querySelectorAll('.auth-view');

    tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    views.forEach(v => v.style.display = v.id === `${tabName}View` ? 'block' : 'none');
  },

  // --- EVENT BINDINGS ---
  bindEvents() {
    // Header cart toggle
    const cartTrigger = document.getElementById('cartTrigger');
    if (cartTrigger) {
      cartTrigger.addEventListener('click', () => this.openCartDrawer());
    }

    const closeDrawerBtn = document.getElementById('closeCartDrawer');
    if (closeDrawerBtn) {
      closeDrawerBtn.addEventListener('click', () => this.closeCartDrawer());
    }

    const cartOverlay = document.getElementById('cartOverlay');
    if (cartOverlay) {
      cartOverlay.addEventListener('click', () => this.closeCartDrawer());
    }

    // Account Trigger
    const accountBtn = document.getElementById('accountBtn');
    if (accountBtn) {
      accountBtn.addEventListener('click', (e) => {
        if (!this.currentUser) {
          e.preventDefault();
          this.openAuthModal('login');
        }
      });
    }

    // Auth modal controls
    const closeAuthBtn = document.getElementById('closeAuthModal');
    if (closeAuthBtn) {
      closeAuthBtn.addEventListener('click', () => this.closeAuthModal());
    }

    const authOverlay = document.getElementById('authModal');
    if (authOverlay) {
      authOverlay.addEventListener('click', (e) => {
        if (e.target === authOverlay) this.closeAuthModal();
      });
    }

    // Auth tabs
    document.querySelectorAll('.auth-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchAuthTab(btn.dataset.tab));
    });

    // Mobile Hamburger Toggle
    const mobileToggle = document.getElementById('mobileNavToggle');
    const mobileDrawer = document.getElementById('mobileNavDrawer');
    if (mobileToggle && mobileDrawer) {
      mobileToggle.addEventListener('click', () => {
        mobileDrawer.classList.toggle('active');
      });
    }

    // Sticky Nav scroll detection
    const header = document.querySelector('.site-header');
    if (header) {
      window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      });
    }

    // FAQ Accordion
    document.querySelectorAll('.faq-trigger').forEach(trigger => {
      trigger.addEventListener('click', () => {
        const item = trigger.closest('.faq-item');
        const isActive = item.classList.contains('active');
        document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
        if (!isActive) {
          item.classList.add('active');
        }
      });
    });

    // Handle Forms
    this.bindAuthForms();
    this.bindNewsletterForms();
    this.bindContactForm();
    this.bindBookingForm();
  },

  // --- FORM HANDLERS ---
  bindAuthForms() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';

        const email = loginForm.email.value;
        const password = loginForm.password.value;

        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });
          const data = await res.json();
          if (data.success) {
            this.currentUser = data.user;
            localStorage.setItem('verdant_user', JSON.stringify(data.user));
            this.updateAuthUI(data.user);
            this.closeAuthModal();
            this.showToast(data.message, 'success');
            if (window.location.pathname.includes('/checkout')) {
              window.location.reload();
            }
          } else {
            this.showToast(data.error || 'Login failed', 'error');
          }
        } catch (err) {
          this.showToast('Unable to connect to login service', 'error');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Log In';
        }
      });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating Account...';

        const name = registerForm.name.value;
        const email = registerForm.email.value;
        const phone = registerForm.phone.value;
        const password = registerForm.password.value;
        const confirm = registerForm.confirm_password.value;
        const address = registerForm.address ? registerForm.address.value : '';

        if (password !== confirm) {
          this.showToast('Passwords do not match.', 'error');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Create Account';
          return;
        }

        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password, address })
          });
          const data = await res.json();
          if (data.success) {
            this.currentUser = data.user;
            localStorage.setItem('verdant_user', JSON.stringify(data.user));
            this.updateAuthUI(data.user);
            this.closeAuthModal();
            this.showToast(data.message, 'success');
          } else {
            this.showToast(data.error || 'Registration failed', 'error');
          }
        } catch (err) {
          this.showToast('Error registering account', 'error');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Create Account';
        }
      });
    }

    const forgotForm = document.getElementById('forgotPasswordForm');
    if (forgotForm) {
      forgotForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = forgotForm.email.value;
        const res = await fetch('/api/auth/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (data.success) {
          document.getElementById('forgotSuccessMsg').style.display = 'block';
          document.getElementById('forgotSuccessText').textContent = data.message;
          forgotForm.style.display = 'none';
        }
      });
    }
  },

  bindNewsletterForms() {
    document.querySelectorAll('.newsletter-form').forEach(form => {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = form.querySelector('input[type="email"]');
        const btn = form.querySelector('button[type="submit"]');
        if (!input || !input.value) return;

        btn.disabled = true;
        btn.textContent = 'Subscribing...';

        try {
          const res = await fetch('/api/newsletter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: input.value })
          });
          const data = await res.json();
          if (data.success) {
            this.showToast(data.message, 'success');
            input.value = '';
          } else {
            this.showToast(data.error, 'error');
          }
        } catch (err) {
          this.showToast('Subscription failed, try again.', 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'Subscribe';
        }
      });
    });
  },

  bindContactForm() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
      contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = contactForm.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Sending Message...';

        const payload = {
          name: contactForm.name.value,
          email: contactForm.email.value,
          subject: contactForm.subject.value,
          message: contactForm.message.value
        };

        try {
          const res = await fetch('/api/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            this.showToast(data.message, 'success');
            contactForm.reset();
          } else {
            this.showToast(data.error || 'Message failed', 'error');
          }
        } catch (err) {
          this.showToast('Could not send message, please call our farmstand.', 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'Send Message';
        }
      });
    }
  },

  bindBookingForm() {
    const bookingForm = document.getElementById('farmTourBookingForm');
    if (bookingForm) {
      bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = bookingForm.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Booking Tour...';

        const payload = {
          tour_id: bookingForm.tour_id.value,
          name: bookingForm.name.value,
          email: bookingForm.email.value,
          phone: bookingForm.phone.value,
          visitors: parseInt(bookingForm.visitors.value) || 1,
          date: bookingForm.date.value,
          time_slot: bookingForm.time_slot.value
        };

        try {
          const res = await fetch('/api/visits/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            this.showToast(data.message, 'success');
            bookingForm.reset();
            const successBox = document.getElementById('bookingSuccessAlert');
            if (successBox) {
              successBox.style.display = 'block';
              successBox.scrollIntoView({ behavior: 'smooth' });
            }
          } else {
            this.showToast(data.error || 'Booking error', 'error');
          }
        } catch (err) {
          this.showToast('Failed to connect to tour booking system', 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'Confirm Farm Visit';
        }
      });
    }
  },

  // --- CSA ACTIONS ---
  async subscribeCSA(planId) {
    if (!this.currentUser) {
      this.showToast('Please log in or register to join our CSA family', 'info');
      this.openAuthModal('register');
      return;
    }

    try {
      const res = await fetch('/api/csa/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, 'success');
        setTimeout(() => {
          window.location.href = '/account#csa';
        }, 1200);
      }
    } catch (err) {
      this.showToast('Could not complete CSA subscription', 'error');
    }
  },

  async cancelCSA() {
    if (!confirm('Are you sure you want to pause/cancel your CSA subscription?')) return;

    try {
      const res = await fetch('/api/csa/cancel', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, 'info');
        window.location.reload();
      }
    } catch (err) {
      this.showToast('Failed to cancel subscription', 'error');
    }
  },

  // --- QUICK VIEW MODAL ---
  async openQuickView(productId) {
    try {
      const res = await fetch(`/api/products/${productId}`);
      const data = await res.json();
      if (data.success && data.product) {
        const p = data.product;
        const modal = document.getElementById('quickViewModal');
        const content = document.getElementById('quickViewContent');
        if (!modal || !content) return;

        content.innerHTML = `
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div style="border-radius: var(--radius-lg); overflow: hidden; height: 320px;">
              <img src="${p.image}" alt="${p.name}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div>
              <span class="badge-tag badge-organic" style="margin-bottom: 0.5rem;">${p.category}</span>
              <h3 style="font-size: 1.6rem; margin-bottom: 0.4rem;">${p.name}</h3>
              <div style="font-size: 1.4rem; font-weight: 800; color: var(--color-forest); margin-bottom: 0.8rem;">
                $${p.price.toFixed(2)} <span style="font-size: 0.85rem; color: #777;">${p.unit}</span>
              </div>
              <p style="font-size: 0.92rem; color: var(--color-text-muted); margin-bottom: 1rem;">${p.description}</p>
              <div style="font-size: 0.82rem; background: var(--color-beige); padding: 0.8rem; border-radius: var(--radius-sm); margin-bottom: 1.2rem;">
                <strong>Harvested:</strong> ${p.harvest_date}<br>
                <strong>Farm Origin:</strong> ${p.origin}
              </div>
              <div style="display: flex; gap: 0.8rem;">
                <div class="qty-stepper">
                  <button class="qty-btn" onclick="const input = document.getElementById('qvQty'); if(input.value > 1) input.value--;">-</button>
                  <input type="text" id="qvQty" class="qty-input" value="1" readonly>
                  <button class="qty-btn" onclick="const input = document.getElementById('qvQty'); input.value++;">+</button>
                </div>
                <button class="btn btn-primary" onclick="FarmApp.addToCart(${JSON.stringify(p).replace(/"/g, '&quot;')}, document.getElementById('qvQty').value); FarmApp.closeQuickView();">
                  Add to Farm Basket
                </button>
              </div>
            </div>
          </div>
        `;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    } catch (e) {
      console.error(e);
    }
  },

  closeQuickView() {
    const modal = document.getElementById('quickViewModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  // --- TOAST NOTIFICATIONS ---
  showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'error' ? '⚠️' : type === 'info' ? 'ℹ️' : '🌱';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(60px)';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  },

  // --- BACK TO TOP ---
  initBackToTop() {
    const btn = document.getElementById('backToTopBtn');
    if (!btn) return;

    window.addEventListener('scroll', () => {
      if (window.scrollY > 350) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    });

    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  FarmApp.init();
});
