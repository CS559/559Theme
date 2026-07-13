'use strict';

/*
 * menu.js — mobile navigation toggle for 559Theme.
 *
 * Sole job: wire the hamburger button (.menu__btn) to show/hide the nav list
 * (.menu__list) on small screens.
 *
 * Expected markup (rendered by layouts/_partials/header.html + menu.html):
 *   <button class="menu__btn" aria-expanded="false"> … </button>
 *   <ul class="menu__list"> … <li><a> … </a></li> … </ul>
 *
 * On button click it toggles, on the elements above:
 *   .menu__list--active      show/hide the list (CSS owns the actual display)
 *   .menu__list--transition  enable the slide animation; removed again on
 *                            transitionend so it only animates during a toggle
 *   .menu__btn--active       hamburger <-> close-icon state
 *   aria-expanded            flipped "true" <-> "false" on the button
 *
 * History: this file also carried a submenu handler (no theme layout renders
 * submenus) and a full dark/light theme system keyed on a `.theme-toggle`
 * element and `localStorage`/`matchMedia` (no theme layout renders a toggle,
 * and no CSS keys off the `data-theme` it set). Both were dead code and were
 * removed in the theme-unification cleanup (Phase 5). If you later add a theme
 * toggle or submenus, add the markup AND the matching script — this file
 * deliberately does neither.
 */
(function iifeMenu(document) {
	var menuBtn = document.querySelector('.menu__btn');
	var menu = document.querySelector('.menu__list');

	function toggleMenu() {
		menu.classList.toggle('menu__list--active');
		menu.classList.toggle('menu__list--transition');
		this.classList.toggle('menu__btn--active');
		this.setAttribute(
			'aria-expanded',
			this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
		);
	}

	function removeMenuTransition() {
		this.classList.remove('menu__list--transition');
	}

	if (menuBtn && menu) {
		menuBtn.addEventListener('click', toggleMenu, false);
		menu.addEventListener('transitionend', removeMenuTransition, false);
	}
}(document));
