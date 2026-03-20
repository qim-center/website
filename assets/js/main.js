import './shared/toggler'

const fadeInElementsOnPageLoad = () => {
	const elements = document.querySelectorAll('[data-fade-on-load]')

	elements.forEach((element) => {
		requestAnimationFrame(() => {
			element.classList.remove('opacity-0')
		})
	})
}

// Handle image downloads on identity page
const setupImageDownloads = () => {
	const downloadableElements = document.querySelectorAll('.downloadable-image')

	downloadableElements.forEach((element) => {
		element.addEventListener('click', async function (e) {
			e.preventDefault()
			const img = this.querySelector('img')
			if (!img) return

			const src = img.src
			const altText = img.alt || 'image'
			const downloadName = this.dataset.download || altText
			const fileName = `${downloadName.replace(/\s+/g, '-').toLowerCase()}.png`

			try {
				// Fetch the image
				const response = await fetch(src)
				if (!response.ok) throw new Error('Failed to fetch image')

				// Create blob and download
				const blob = await response.blob()
				const url = window.URL.createObjectURL(blob)
				const a = document.createElement('a')
				a.href = url
				a.download = fileName
				document.body.appendChild(a)
				a.click()
				window.URL.revokeObjectURL(url)
				document.body.removeChild(a)
			} catch (error) {
				console.error('Download failed:', error)
				// Fallback to simple link download
				const link = document.createElement('a')
				link.href = src
				link.download = fileName
				document.body.appendChild(link)
				link.click()
				document.body.removeChild(link)
			}
		})
	})
}

// Handle hex code copy buttons
const setupHexCopyButtons = () => {
	const copyButtons = document.querySelectorAll('.copy-hex-btn')

	copyButtons.forEach((button) => {
		button.addEventListener('click', async function (e) {
			e.stopPropagation()
			const hexCode = this.dataset.hex
			const svg = this.querySelector('svg')
			const originalSvg = svg.outerHTML

			try {
				await navigator.clipboard.writeText(hexCode)
				// Show feedback
				svg.innerHTML = '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" class="text-green-500"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" class="text-green-500" stroke="currentColor"></path>'
				setTimeout(() => {
					svg.outerHTML = originalSvg
				}, 2000)
			} catch (error) {
				console.error('Copy failed:', error)
			}
		})
	})
}


if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', () => {
		fadeInElementsOnPageLoad()
		setupImageDownloads()
		setupHexCopyButtons()
	})
} else {
	fadeInElementsOnPageLoad()
	setupImageDownloads()
	setupHexCopyButtons()
}
