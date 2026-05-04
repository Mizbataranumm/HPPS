document.addEventListener('DOMContentLoaded', () => {
    
    const startBtn = document.getElementById('start-btn');
    const landingPage = document.getElementById('landing-page');
    const dashboardPage = document.getElementById('dashboard-page');
    const inputSection = document.getElementById('input-section');
    const resultsSection = document.getElementById('results-section');
    const predictForm = document.getElementById('prediction-form');
    const cityPreset = document.getElementById('city-preset');
    const loadingOverlay = document.getElementById('loading-overlay');
    const recalculateBtn = document.getElementById('recalculate-btn');

    // Chart instances
    let modelChartInstance = null;
    let featureChartInstance = null;

    // Navigation
    startBtn.addEventListener('click', () => {
        const username = document.getElementById('username-input').value.trim();
        if (username) {
            document.querySelector('.user-greeting').innerText = `Welcome, ${username}`;
            document.querySelector('.avatar').innerText = username.charAt(0).toUpperCase();
        }
        
        landingPage.classList.remove('active');
        dashboardPage.classList.add('active');
    });

    recalculateBtn.addEventListener('click', () => {
        resultsSection.style.display = 'none';
        inputSection.style.display = 'block';
        window.scrollTo(0, 0);
    });

    // City Preset Logic
    cityPreset.addEventListener('change', (e) => {
        const selected = e.target.options[e.target.selectedIndex];
        if (selected.value !== "") {
            const tier = selected.getAttribute('data-tier');
            const loc = selected.getAttribute('data-loc');
            
            document.getElementById('city_tier').value = tier;
            document.getElementById('location_score').value = loc;
            document.getElementById('loc-val').innerText = loc;
        }
    });

    // Prediction Logic
    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show Loading
        loadingOverlay.style.display = 'flex';

        // Gather Data
        const payload = {
            area: document.getElementById('area').value,
            bhk: document.getElementById('bhk').value,
            bathrooms: document.getElementById('bathrooms').value,
            age: document.getElementById('age').value,
            location_score: document.getElementById('location_score').value,
            quality_score: document.getElementById('quality_score').value,
            city_tier: document.getElementById('city_tier').value,
            garage: document.getElementById('garage').checked ? 1 : 0
        };

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                // Populate Results
                // Animate Final Price Count Up
                animateValue('final-price', 0, data.predicted_lakhs, 1500, data.formatted_price);

                document.getElementById('confidence-range').innerText = data.confidence_range;
                document.getElementById('calc-explanation').innerHTML = data.explanation;
                document.getElementById('market-comparison').innerText = data.market_comparison;
                document.getElementById('best-model-name').innerText = data.best_model;
                document.getElementById('best-model-r2').innerText = 'R²: ' + data.best_model_r2;

                // Render Charts
                renderModelChart(data.all_models);
                renderFeatureChart(data.feature_importances);

                // Switch View
                inputSection.style.display = 'none';
                resultsSection.style.display = 'block';
                window.scrollTo(0, 0);
            } else {
                alert("Error: " + data.error);
            }
        } catch (err) {
            console.error(err);
            alert("Failed to connect to the server.");
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    // Chart Rendering Functions
    function renderModelChart(modelsData) {
        const ctx = document.getElementById('modelChart').getContext('2d');
        
        if (modelChartInstance) {
            modelChartInstance.destroy();
        }

        const labels = Object.keys(modelsData);
        const r2Scores = labels.map(k => (modelsData[k].r2 * 100).toFixed(1));

        modelChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'R² Score (%)',
                    data: r2Scores,
                    backgroundColor: [
                        'rgba(0, 212, 170, 0.6)',
                        'rgba(138, 43, 226, 0.6)',
                        'rgba(255, 215, 0, 0.6)'
                    ],
                    borderColor: [
                        'rgba(0, 212, 170, 1)',
                        'rgba(138, 43, 226, 1)',
                        'rgba(255, 215, 0, 1)'
                    ],
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#a0aec0' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    x: {
                        ticks: { color: '#a0aec0' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function renderFeatureChart(importances) {
        const ctx = document.getElementById('featureChart').getContext('2d');
        
        if (featureChartInstance) {
            featureChartInstance.destroy();
        }

        // Sort by importance
        const sortedArray = Object.entries(importances).sort((a, b) => b[1] - a[1]);
        const labels = sortedArray.map(item => item[0].replace('_', ' ').toUpperCase());
        const data = sortedArray.map(item => (item[1] * 100).toFixed(1));

        featureChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Contribution (%)',
                    data: data,
                    backgroundColor: 'rgba(0, 212, 170, 0.5)',
                    borderColor: 'rgba(0, 212, 170, 1)',
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y', // horizontal bar chart
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { color: '#a0aec0' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Helper: Number Count Up Animation
    function animateValue(id, start, end, duration, finalString) {
        const obj = document.getElementById(id);
        let startTimestamp = null;
        
        // Determine suffix if needed based on finalString (e.g. ' Cr' or ' L')
        const suffix = finalString.includes('Cr') ? ' Cr' : ' L';
        const prefix = '₹ ';
        
        // If final string has Cr, the target end value for the animation should be scaled down by 100
        const targetValue = finalString.includes('Cr') ? end / 100 : end;

        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            // easeOutQuart
            const easeProgress = 1 - Math.pow(1 - progress, 4);
            const currentVal = (easeProgress * (targetValue - start) + start).toFixed(2);
            
            obj.innerText = prefix + currentVal + suffix;
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerText = finalString; // Ensure exact final string matches API format
            }
        };
        window.requestAnimationFrame(step);
    }
});
