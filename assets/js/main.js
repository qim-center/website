import './shared/toggler'

const fadeInElementsOnPageLoad = () => {
	const elements = document.querySelectorAll('[data-fade-on-load]')

	elements.forEach((element) => {
		requestAnimationFrame(() => {
			element.classList.remove('opacity-0')
		})
	})
}

if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', fadeInElementsOnPageLoad)
} else {
	fadeInElementsOnPageLoad()
}
