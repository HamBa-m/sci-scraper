// Handle form submission and SSE updates
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progress-text');
    const papersList = document.getElementById('papers-list');
    const resultsContainer = document.getElementById('results-container');
    
    let eventSource = null;

    function formatStatistics(stats) {
        // Convert plain text statistics to HTML
        return stats.split('\n').map(line => {
            if (line.startsWith('Overall Summary:') || 
                line.startsWith('Breakdown by Source:') || 
                line.startsWith('Unique Sources in')) {
                return `<h3 class="text-white text-xl font-semibold mt-4 mb-2">${line}</h3>`;
            } else if (line.startsWith('-')) {
                return `<div class="ml-4 text-white">${line}</div>`;
            } else if (line.trim() === '') {
                return '<br>';
            } else if (line.includes('|')) {
                // Handle table-like data
                const cells = line.split('|').map(cell => cell.trim());
                return `<div class="grid grid-cols-4 gap-4 text-white">${
                    cells.map(cell => `<div>${cell}</div>`).join('')
                }</div>`;
            } else {
                return `<div class="text-white">${line}</div>`;
            }
        }).join('');
    }

    function startEventSource() {
        // Close any existing connection
        if (eventSource) {
            eventSource.close();
        }

        // Create new SSE connection
        eventSource = new EventSource('/progress');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Update progress
            const progress = data.progress;
            progressBar.style.width = `${progress}%`;
            progressText.textContent = `${progress}%`;
            
            // Add new papers to the list
            if (data.papers && data.papers.length > 0) {
                data.papers.forEach(paper => {
                    const paperElement = document.createElement('div');
                    paperElement.className = 'paper-item';
                    
                    // Create title element
                    const titleElement = document.createElement('div');
                    titleElement.className = 'font-medium';
                    titleElement.textContent = paper.title || 'Untitled Paper';
                    paperElement.appendChild(titleElement);
                    
                    // Create source element
                    if (paper.source) {
                        const sourceElement = document.createElement('div');
                        sourceElement.className = 'text-sm opacity-75';
                        sourceElement.textContent = `Source: ${paper.source}`;
                        paperElement.appendChild(sourceElement);
                    }
                    
                    // Add paper to list with animation
                    papersList.appendChild(paperElement);
                    papersList.scrollTop = papersList.scrollHeight;
                });
            }
        };
        
        eventSource.onerror = function(error) {
            console.error('SSE Error:', error);
            eventSource.close();
            showError('Lost connection to server. Please refresh the page and try again.');
        };
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-500 bg-opacity-25 text-white p-4 rounded-lg mt-4 fade-in';
        errorDiv.textContent = message;
        form.insertAdjacentElement('afterend', errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset UI
        progressContainer.classList.add('hidden');
        papersList.innerHTML = '';
        resultsContainer.classList.add('hidden');
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        
        const formData = new FormData(this);
        
        // Validate form data
        const query = formData.get('query').trim();
        const numPages = formData.get('num_pages');
        
        if (!query) {
            showError('Please enter a search query');
            return;
        }
        
        if (!numPages || isNaN(numPages) || numPages < 1) {
            showError('Please enter a valid number of pages');
            return;
        }
        
        try {
            // Show progress container immediately
            progressContainer.classList.remove('hidden');
            progressContainer.classList.add('fade-in');
            
            // Start SSE connection before submitting form
            startEventSource();
            
            // Submit form
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Server error');
            }
            
            // Get the response HTML
            const html = await response.text();
            
            // Parse the response to get statistics
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Find statistics in the parsed document
            // Assuming statistics are in a <pre> tag or data attribute
            const statsElement = doc.querySelector('pre');
            if (statsElement) {
                const stats = statsElement.textContent;
                resultsContainer.classList.remove('hidden');
                resultsContainer.innerHTML = `
                    <h2 class="text-white text-2xl font-bold mb-4">Scraping Summary</h2>
                    <div class="stats-container">
                        ${formatStatistics(stats)}
                    </div>
                    <p class="text-white mt-4">Results saved to <span class="font-bold">scholar_results.xlsx</span></p>
                `;
                resultsContainer.classList.add('fade-in');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred while processing your request');
        }
    });
});


function downloadResults() {
    fetch('/download')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'scholar_results.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => console.error('Error downloading results:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResults);
    }
});

// Show download button when scraping is complete
function updateProgress(data) {
    // progress update code
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progress-text');
    progressBar.style.width = `${data.progress}%`;
    progressText.textContent = `${data.progress}%`;
    
    if (data.progress === 100) {
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.classList.remove('hidden');
        }
    }
}