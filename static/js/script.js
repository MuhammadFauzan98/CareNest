// Smart Health Assistant - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
});

function initializeApplication() {
    setupFormValidations();
    setupInteractiveElements();
    setupHealthGuidelines();
}

function setupFormValidations() {
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(strength);
        });
    }

    // Age validation
    const ageInput = document.getElementById('age');
    if (ageInput) {
        ageInput.addEventListener('change', function() {
            const age = parseInt(this.value);
            if (age < 60 || age > 120) {
                this.setCustomValidity('Age must be between 60 and 120 years for elderly care monitoring.');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Health parameter validation
    const healthInputs = ['systolic_bp', 'diastolic_bp', 'heart_rate', 'blood_sugar', 'cholesterol'];
    healthInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('change', validateHealthParameter);
        }
    });
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    return Math.min(strength, 4);
}

function updatePasswordStrengthIndicator(strength) {
    const indicator = document.getElementById('password-strength');
    if (!indicator) return;

    const strengths = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['danger', 'danger', 'warning', 'info', 'success'];
    
    indicator.textContent = strengths[strength];
    indicator.className = `badge bg-${colors[strength]}`;
}

function validateHealthParameter(event) {
    const input = event.target;
    const value = parseFloat(input.value);
    let isValid = true;
    let message = '';

    switch(input.id) {
        case 'systolic_bp':
            if (value < 70 || value > 250) {
                isValid = false;
                message = 'Systolic BP should be between 70 and 250 mmHg';
            }
            break;
        case 'diastolic_bp':
            if (value < 40 || value > 150) {
                isValid = false;
                message = 'Diastolic BP should be between 40 and 150 mmHg';
            }
            break;
        case 'heart_rate':
            if (value < 30 || value > 200) {
                isValid = false;
                message = 'Heart rate should be between 30 and 200 BPM';
            }
            break;
        case 'blood_sugar':
            if (value < 50 || value > 500) {
                isValid = false;
                message = 'Blood sugar should be between 50 and 500 mg/dL';
            }
            break;
        case 'cholesterol':
            if (value < 100 || value > 400) {
                isValid = false;
                message = 'Cholesterol should be between 100 and 400 mg/dL';
            }
            break;
    }

    if (!isValid) {
        input.setCustomValidity(message);
        showInputWarning(input, message);
    } else {
        input.setCustomValidity('');
        hideInputWarning(input);
    }
}

function showInputWarning(input, message) {
    let warning = input.parentNode.querySelector('.input-warning');
    if (!warning) {
        warning = document.createElement('div');
        warning.className = 'input-warning text-danger small mt-1';
        input.parentNode.appendChild(warning);
    }
    warning.textContent = message;
    input.classList.add('is-invalid');
}

function hideInputWarning(input) {
    const warning = input.parentNode.querySelector('.input-warning');
    if (warning) {
        warning.remove();
    }
    input.classList.remove('is-invalid');
}

function setupInteractiveElements() {
    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupHealthGuidelines() {
    // Add guideline popovers to health input fields
    const guidelines = {
        'systolic_bp': 'Normal: <120 mmHg\nElevated: 120-129 mmHg\nHigh: ≥130 mmHg',
        'diastolic_bp': 'Normal: <80 mmHg\nElevated: <80 mmHg\nHigh: ≥80 mmHg',
        'heart_rate': 'Normal resting: 60-100 BPM\nToo slow: <60 BPM\nToo fast: >100 BPM',
        'blood_sugar': 'Normal fasting: 70-99 mg/dL\nPrediabetes: 100-125 mg/dL\nDiabetes: ≥126 mg/dL',
        'cholesterol': 'Desirable: <200 mg/dL\nBorderline: 200-239 mg/dL\nHigh: ≥240 mg/dL',
        'sleep_hours': 'Recommended: 7-9 hours\nInsufficient: <7 hours\nPoor health: <6 hours'
    };

    Object.keys(guidelines).forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.setAttribute('data-bs-toggle', 'popover');
            field.setAttribute('data-bs-trigger', 'hover focus');
            field.setAttribute('data-bs-placement', 'top');
            field.setAttribute('data-bs-content', guidelines[fieldId]);
            field.setAttribute('data-bs-title', 'Health Guidelines');
        }
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Utility functions
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function calculateBMI(weight, height) {
    // height in cm to meters
    const heightInMeters = height / 100;
    return (weight / (heightInMeters * heightInMeters)).toFixed(1);
}

function getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

// API functions
async function fetchHealthTrends() {
    try {
        const response = await fetch('/api/health-trends');
        return await response.json();
    } catch (error) {
        console.error('Error fetching health trends:', error);
        return null;
    }
}

// Export functions for global access
window.HealthAssistant = {
    formatDate,
    calculateBMI,
    getBMICategory,
    fetchHealthTrends
};

// Service Worker Registration (for future PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed: ', error);
            });
    });
}
// Add this to the existing script.js file

// Enhanced interactive elements
function setupEnhancedInteractions() {
    // Parallax effect for hero section
    setupParallax();
    
    // Animate elements on scroll
    setupScrollAnimations();
    
    // Enhanced form interactions
    setupEnhancedForms();
    
    // Real-time health calculations
    setupHealthCalculators();
}

function setupParallax() {
    const hero = document.querySelector('.hero-section');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }
}

function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards and feature items
    document.querySelectorAll('.card, .feature-item, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

function setupEnhancedForms() {
    // Floating labels
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        const label = input.previousElementSibling;
        if (label && label.classList.contains('form-label')) {
            // Add floating label effect
            input.addEventListener('focus', () => {
                label.style.transform = 'translateY(-25px) scale(0.85)';
                label.style.color = 'var(--primary-color)';
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    label.style.transform = 'none';
                    label.style.color = '';
                }
            });
        }
        
        // Real-time validation with visual feedback
        input.addEventListener('input', function() {
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
}

function setupHealthCalculators() {
    // BMI Calculator
    const weightInput = document.getElementById('weight');
    const heightInput = document.getElementById('height');
    
    if (weightInput && heightInput) {
        const calculateBMI = () => {
            const weight = parseFloat(weightInput.value);
            const height = parseFloat(heightInput.value) / 100; // cm to m
            
            if (weight && height) {
                const bmi = weight / (height * height);
                showBMICalculator(bmi);
            }
        };
        
        weightInput.addEventListener('input', calculateBMI);
        heightInput.addEventListener('input', calculateBMI);
    }
}

function showBMICalculator(bmi) {
    let bmiDisplay = document.getElementById('bmi-display');
    if (!bmiDisplay) {
        bmiDisplay = document.createElement('div');
        bmiDisplay.id = 'bmi-display';
        bmiDisplay.className = 'alert alert-info mt-3';
        const form = document.querySelector('form');
        form.appendChild(bmiDisplay);
    }
    
    const category = getBMICategory(bmi);
    const color = category === 'Normal weight' ? 'success' : 
                  category === 'Overweight' ? 'warning' : 'danger';
    
    bmiDisplay.innerHTML = `
        <strong>BMI: ${bmi.toFixed(1)}</strong> - ${category}
        <span class="badge bg-${color} float-end">${category}</span>
    `;
    bmiDisplay.className = `alert alert-${color} mt-3`;
}

function getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

// Enhanced health risk visualization
function createHealthRadarChart(healthData) {
    const ctx = document.getElementById('healthRadarChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Blood Pressure', 'Heart Rate', 'Blood Sugar', 'Cholesterol', 'Sleep Quality'],
            datasets: [{
                label: 'Your Health',
                data: [
                    normalizeBP(healthData.systolic_bp, healthData.diastolic_bp),
                    normalizeHeartRate(healthData.heart_rate),
                    normalizeBloodSugar(healthData.blood_sugar),
                    normalizeCholesterol(healthData.cholesterol),
                    normalizeSleep(healthData.sleep_hours)
                ],
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(37, 99, 235, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 14,
                            family: "'Inter', sans-serif"
                        }
                    }
                }
            }
        }
    });
}

// Normalization functions for radar chart
function normalizeBP(systolic, diastolic) {
    const avg = (systolic + diastolic) / 2;
    return Math.max(0, 100 - Math.abs(100 - avg));
}

function normalizeHeartRate(rate) {
    return Math.max(0, 100 - Math.abs(72 - rate));
}

function normalizeBloodSugar(sugar) {
    return Math.max(0, 100 - Math.abs(100 - sugar) / 2);
}

function normalizeCholesterol(cholesterol) {
    return Math.max(0, 100 - Math.abs(200 - cholesterol) / 2);
}

function normalizeSleep(hours) {
    return Math.min(100, hours * 12.5); // 8 hours = 100%
}

// Initialize enhanced features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
    setupEnhancedInteractions();
    
    // Add any health data for visualization if available
    if (typeof healthData !== 'undefined') {
        createHealthRadarChart(healthData);
    }
});

// Export enhanced functions
window.HealthAssistant = {
    ...window.HealthAssistant,
    createHealthRadarChart,
    setupEnhancedInteractions
};