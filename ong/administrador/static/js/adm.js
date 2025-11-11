// static/js/adm.js
(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburgerBtn');
    const mobileNav = document.getElementById('mobileNav');
    const mobileBackdrop = document.getElementById('mobileBackdrop');
    const userToggle = document.getElementById('userToggle');
    const userDropdown = document.getElementById('userDropdown');

    console.log('[adm.js] init', {
      hamburger: !!hamburger,
      mobileNav: !!mobileNav,
      mobileBackdrop: !!mobileBackdrop,
      userToggle: !!userToggle,
      userDropdown: !!userDropdown
    });

    /* ---------------------------
       util
    --------------------------- */
    function setBodyScrollDisabled(disabled) {
      if (disabled) {
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
      } else {
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
      }
    }

    /* ---------------------------
       MOBILE NAV
    --------------------------- */
    function openMobileNav() {
      if (!hamburger) return;
      hamburger.classList.add('open');
      hamburger.setAttribute('aria-expanded', 'true');

      if (mobileNav) {
        mobileNav.classList.add('open');
        mobileNav.setAttribute('aria-hidden', 'false');
      }
      if (mobileBackdrop) mobileBackdrop.classList.add('visible');
      setBodyScrollDisabled(true);
      closeUserDropdown();
    }

    function closeMobileNav() {
      if (!hamburger) return;
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');

      if (mobileNav) {
        mobileNav.classList.remove('open');
        mobileNav.setAttribute('aria-hidden', 'true');
      }
      if (mobileBackdrop) mobileBackdrop.classList.remove('visible');
      setBodyScrollDisabled(false);
    }

    function toggleMobileNav(e) {
      e && e.stopPropagation();
      if (hamburger && hamburger.classList.contains('open')) closeMobileNav();
      else openMobileNav();
    }

    if (hamburger) {
      hamburger.addEventListener('click', toggleMobileNav);
      hamburger.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleMobileNav(e); }
        else if (e.key === 'Escape') closeMobileNav();
      });
    }

    // Quando clicar em um link dentro do mobileNav, permitir a navegação e fechar o menu em atraso
    if (mobileNav) {
      mobileNav.addEventListener('click', function(e) {
        const a = e.target.closest('a');
        if (!a) return;

        // Log para debugar — remova se quiser
        try {
          console.log('[adm.js] mobileNav link click:', a.getAttribute('href'));
        } catch (err) { /* ignore */ }

        // Se for âncora interna (começa com '#') ou link normal, não previne.
        // Fecha com pequeno atraso para não cancelar navegação.
        setTimeout(() => {
          try { closeMobileNav(); } catch (err) { /* silencioso */ }
        }, 150);
      });

      // Evitar que cliques internos em elementos não-links fechem o menu
      mobileNav.addEventListener('touchstart', function(e){
        // deixa o evento seguir normalmente
      }, { passive: true });
    }

    if (mobileBackdrop) {
      mobileBackdrop.addEventListener('click', function(e){
        // click no backdrop deve fechar o menu
        closeMobileNav();
      });
      mobileBackdrop.addEventListener('touchstart', function(e){
        closeMobileNav();
      }, { passive: true });
    }

    /* ---------------------------
       USER DROPDOWN
    --------------------------- */
    let userAnimating = false;

    function openUserDropdown() {
      if (!userToggle || !userDropdown) return;
      userDropdown.classList.add('open');
      userToggle.setAttribute('aria-expanded', 'true');
      userDropdown.setAttribute('aria-hidden', 'false');
      closeMobileNav();
    }

    function closeUserDropdown() {
      if (!userToggle || !userDropdown) return;
      userDropdown.classList.remove('open');
      userToggle.setAttribute('aria-expanded', 'false');
      userDropdown.setAttribute('aria-hidden', 'true');
    }

    function toggleUserDropdown(e) {
      if (!userToggle || !userDropdown) return;
      e && e.preventDefault(); e && e.stopPropagation();
      if (userAnimating) return;
      userAnimating = true;
      const willOpen = !userDropdown.classList.contains('open');
      if (willOpen) openUserDropdown(); else closeUserDropdown();
      setTimeout(()=> userAnimating = false, 220);
    }

    if (userToggle) {
      userToggle.addEventListener('click', toggleUserDropdown);
      userToggle.addEventListener('keydown', function(e){
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleUserDropdown(e); }
        else if (e.key === 'Escape') closeUserDropdown();
      });
    }

    if (userDropdown) {
      userDropdown.addEventListener('click', function(e) {
        const a = e.target.closest('a');
        if (a) {
          try {
            console.log('[adm.js] userDropdown link click:', a.getAttribute('href'));
          } catch (err) {}
          // fechar com atraso para não interromper navegação
          setTimeout(() => { closeUserDropdown(); }, 150);
        }
      });

      userDropdown.addEventListener('focusout', function(ev) {
        const newTarget = ev.relatedTarget;
        if (!userDropdown.contains(newTarget) && !(userToggle && userToggle.contains(newTarget))) {
          closeUserDropdown();
        }
      });
    }

    /* ---------------------------
       CLIQUE FORA / TOUCH GLOBAL
    --------------------------- */
    document.addEventListener('click', function(e) {
      const clickedInsideUser = userDropdown && (userDropdown.contains(e.target) || (userToggle && userToggle.contains(e.target)));
      const clickedInsideMobile = mobileNav && (mobileNav.contains(e.target) || (hamburger && hamburger.contains(e.target)));
      if (!clickedInsideUser) closeUserDropdown();
      if (!clickedInsideMobile) closeMobileNav();
    });

    document.addEventListener('touchstart', function(e) {
      const touchedInsideUser = userDropdown && (userDropdown.contains(e.target) || (userToggle && userToggle.contains(e.target)));
      const touchedInsideMobile = mobileNav && (mobileNav.contains(e.target) || (hamburger && hamburger.contains(e.target)));
      if (!touchedInsideUser) closeUserDropdown();
      if (!touchedInsideMobile) closeMobileNav();
    }, { passive: true });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') { closeUserDropdown(); closeMobileNav(); }
    });

    /* ---------------------------
       RESIZE (evita estados estranhos)
    --------------------------- */
    window.addEventListener('resize', function() {
      closeMobileNav();
      closeUserDropdown();
    });

    console.log('[adm.js] listeners registrados');

    // Expor helpers para debug manual no console
    window.__adm_debug = {
      openMobileNav,
      closeMobileNav,
      toggleMobileNav,
      openUserDropdown,
      closeUserDropdown,
      toggleUserDropdown
    };
  });
})();

document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const mobileNav = document.getElementById('mobileNav');
    const mobileBackdrop = document.getElementById('mobileBackdrop');

    // Função para alternar o menu móvel
    function toggleMobileMenu() {
        const isExpanded = hamburgerBtn.getAttribute('aria-expanded') === 'true' || false;
        hamburgerBtn.setAttribute('aria-expanded', !isExpanded);
        mobileNav.setAttribute('aria-hidden', isExpanded);
        mobileBackdrop.setAttribute('aria-hidden', isExpanded);
        document.body.classList.toggle('menu-open', !isExpanded);
    }

    // Event listener para o botão hambúrguer
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleMobileMenu);
    }

    // Event listener para o backdrop (fechar menu ao clicar fora)
    if (mobileBackdrop) {
        mobileBackdrop.addEventListener('click', toggleMobileMenu);
    }
});
