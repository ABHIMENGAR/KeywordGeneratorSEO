document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('keywordForm');
    const keywordInput = document.getElementById('keywordInput');
    const generateBtn = document.getElementById('generateBtn');
    const resultsSection = document.getElementById('resultsSection');
    const keywordsList = document.getElementById('keywordsList');
    const errorMessage = document.getElementById('errorMessage');
    const keywordCount = document.getElementById('keywordCount');
    const downloadCsv = document.getElementById('downloadCsv');
    const downloadJson = document.getElementById('downloadJson');
    const copyBtn = document.getElementById('copyBtn');
    const filterInput = document.getElementById('filterInput');

    let currentKeyword = '';
    let currentKeywords = [];

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const keyword = keywordInput.value.trim();

        if (!keyword) {
            showError('Please enter a keyword');
            return;
        }

        currentKeyword = keyword;
        setLoading(true);
        resultsSection.classList.add('hidden');
        errorMessage.classList.add('hidden');
        filterInput.value = ''; // Reset filter

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ keyword: keyword })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                currentKeywords = data.keywords;
                displayResults(data.keywords);
            } else {
                showError(data.error || 'An error occurred while generating keywords');
                currentKeywords = [];
            }
        } catch (error) {
            showError('Network error: ' + error.message);
            currentKeywords = [];
        } finally {
            setLoading(false);
        }
    });

    // Display Results
    function displayResults(keywords) {
        keywordCount.textContent = keywords.length;
        keywordsList.innerHTML = '';

        if (keywords.length === 0) {
            keywordsList.innerHTML = '<p class="no-results">No keywords found. Try a different topic.</p>';
        } else {
            // Using a DocumentFragment for better performance
            const fragment = document.createDocumentFragment();
            keywords.forEach(keyword => {
                const keywordCard = document.createElement('div');
                keywordCard.className = 'keyword-card';
                keywordCard.textContent = keyword;

                // Add click-to-copy functionality for individual cards
                keywordCard.addEventListener('click', () => {
                    copyTextToClipboard(keyword);
                    showToast(`Copied: ${keyword}`);
                });

                fragment.appendChild(keywordCard);
            });
            keywordsList.appendChild(fragment);
        }

        resultsSection.classList.remove('hidden');
    }

    // Filter Logic
    filterInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = currentKeywords.filter(k => k.toLowerCase().includes(query));
        displayResults(filtered);
    });

    // Loading State
    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        if (isLoading) {
            generateBtn.querySelector('.btn-text').style.display = 'none';
            generateBtn.querySelector('.btn-loader').style.display = 'flex';
        } else {
            generateBtn.querySelector('.btn-text').style.display = 'inline';
            generateBtn.querySelector('.btn-loader').style.display = 'none';
        }
    }

    // Error Handling
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    // Download Handlers
    downloadCsv.addEventListener('click', async () => new DownloadHandler('csv').download());
    downloadJson.addEventListener('click', async () => new DownloadHandler('json').download());

    class DownloadHandler {
        constructor(type) {
            this.type = type;
        }

        async download() {
            if (!currentKeyword || currentKeywords.length === 0) return;

            const btn = this.type === 'csv' ? downloadCsv : downloadJson;
            const originalText = btn.textContent;
            btn.textContent = 'Preparing...';
            btn.disabled = true;

            try {
                const response = await fetch(`/api/download/${this.type}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        keyword: currentKeyword,
                        keywords: currentKeywords
                    })
                });

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${currentKeyword}-keywords.${this.type}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                showError(`Error downloading ${this.type.toUpperCase()}: ${error.message}`);
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }
    }

    // Copy All Handler
    copyBtn.addEventListener('click', () => {
        if (currentKeywords.length === 0) return;
        const text = currentKeywords.join('\n');
        copyTextToClipboard(text);
        showToast(`Copied ${currentKeywords.length} keywords!`);
    });

    // Utilities
    async function copyTextToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            console.error('Failed to copy: ', err);
            // Fallback
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("Copy");
            textArea.remove();
        }
    }

    function showToast(message) {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293b;
            color: white;
            padding: 10px 20px;
            border-radius: 50px;
            z-index: 1000;
            font-size: 0.9rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: fadeIn 0.3s ease-out;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        // Remove after 2 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    // Add CSS for toast animation
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, 20px); }
            to { opacity: 1; transform: translate(-50%, 0); }
        }
    `;
    document.head.appendChild(style);
});
