const API_BASE_URL = '/api';
        let isLoading = false;

        // Helper function to display results with styling
        function displayResult(elementId, data, type = 'info') {
            const element = document.getElementById(elementId);
            element.textContent = JSON.stringify(data, null, 2);
            element.className = type;
        }

        // Helper function to display errors
        function displayError(elementId, error) {
            const element = document.getElementById(elementId);
            element.textContent = `Error: ${error.message || error}`;
            element.className = 'error';
        }

        // Helper function to show loading state
        function setLoading(buttonElement, isLoading) {
            if (isLoading) {
                buttonElement.disabled = true;
                buttonElement.innerHTML += '<span class="loading"></span>';
            } else {
                buttonElement.disabled = false;
                const loading = buttonElement.querySelector('.loading');
                if (loading) loading.remove();
            }
        }

        // Check browser status
        async function checkStatus() {
            const resultElementId = 'status-result';
            const button = event.target;
            
            try {
                setLoading(button, true);
                const response = await fetch(`${API_BASE_URL}/status`);
                const data = await response.json();
                
                if (!response.ok) {
                    displayError(resultElementId, data);
                    return;
                }
                
                const type = data.browser_active ? 'success' : 'warning';
                displayResult(resultElementId, data, type);
            } catch (error) {
                displayError(resultElementId, error);
            } finally {
                setLoading(button, false);
            }
        }

        // Open NotebookLM
        async function openNotebookLM() {
            const resultElementId = 'open-result';
            const button = event.target;
            const url = document.getElementById('notebooklm-url').value;
            
            if (!url) {
                displayError(resultElementId, 'NotebookLM URL is required');
                return;
            }
            
            try {
                setLoading(button, true);
                const response = await fetch(`${API_BASE_URL}/open_notebooklm`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ notebooklm_url: url })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    if (response.status === 401) {
                        displayResult(resultElementId, data, 'warning');
                    } else {
                        displayError(resultElementId, data);
                    }
                    return;
                }
                
                displayResult(resultElementId, data, 'success');
            } catch (error) {
                displayError(resultElementId, error);
            } finally {
                setLoading(button, false);
            }
        }

        // Query NotebookLM
        async function queryNotebookLM() {
            const resultElementId = 'query-result';
            const button = event.target;
            const query = document.getElementById('query-text').value;
            
            if (!query) {
                displayError(resultElementId, 'Query text is required');
                return;
            }
            
            try {
                setLoading(button, true);
                
                // Show initial message
                document.getElementById(resultElementId).textContent = 'Submitting query and waiting for response... This may take 30-60 seconds.';
                document.getElementById(resultElementId).className = 'warning';
                
                const response = await fetch(`${API_BASE_URL}/query_notebooklm`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    displayError(resultElementId, data);
                    return;
                }
                
                displayResult(resultElementId, data, 'success');
            } catch (error) {
                displayError(resultElementId, error);
            } finally {
                setLoading(button, false);
            }
        }

        // Close browser
        async function closeBrowser() {
            const resultElementId = 'close-result';
            const button = event.target;
            
            try {
                setLoading(button, true);
                const response = await fetch(`${API_BASE_URL}/close_browser`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    displayError(resultElementId, data);
                    return;
                }
                
                displayResult(resultElementId, data, 'success');
            } catch (error) {
                displayError(resultElementId, error);
            } finally {
                setLoading(button, false);
            }
        }

        // Auto-check status on page load
        window.addEventListener('load', function() {
            setTimeout(checkStatus, 1000);
        });