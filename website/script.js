// JavaScript for AriTyper Website

// Analytics configuration
const ANALYTICS_API = 'https://arityper-api.onrender.com/api';
const SESSION_ID = generateSessionId();

document.addEventListener('DOMContentLoaded', function() {
    // Track page visit
    trackPageVisit();
    
    // Initialize Bootstrap components
    initializeBootstrap();
    
    // Setup smooth scrolling
    setupSmoothScrolling();
    
    // Setup navbar scroll effect
    setupNavbarScroll();
    
    // Setup download functionality
    setupDownloadButtons();
    
    // Setup animations
    setupAnimations();
});

function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

function trackPageVisit() {
    try {
        fetch(`${ANALYTICS_API}/track_visit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page: window.location.pathname,
                referrer: document.referrer || '',
                session_id: SESSION_ID
            })
        }).catch(error => {
            console.log('Analytics tracking failed:', error);
        });
    } catch (error) {
        console.log('Analytics tracking error:', error);
    }
}

function trackDownload(fileName, fileSize) {
    try {
        fetch(`${ANALYTICS_API}/track_download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_name: fileName,
                file_size: fileSize,
                source: 'website',
                session_id: SESSION_ID
            })
        }).catch(error => {
            console.log('Download tracking failed:', error);
        });
    } catch (error) {
        console.log('Download tracking error:', error);
    }
}

function initializeBootstrap() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function setupSmoothScrolling() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 80; // Account for fixed navbar
                const targetPosition = target.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const navbarToggler = document.querySelector('.navbar-toggler');
                    navbarToggler.click();
                }
            }
        });
    });
}

function setupNavbarScroll() {
    // Add shadow to navbar on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

function setupDownloadButtons() {
    const downloadBtn = document.getElementById('downloadBtn');
    const modalDownloadBtn = document.getElementById('modalDownloadBtn');
    const downloadModal = new bootstrap.Modal(document.getElementById('downloadModal'));
    
    // Main download button
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            downloadModal.show();
        });
    }
    
    // Modal download button (for testing)
    if (modalDownloadBtn) {
        modalDownloadBtn.addEventListener('click', function() {
            startDownload();
            downloadModal.hide();
        });
    }
}

function startDownload() {
    // Show download progress
    showToast('Download started!', 'info');
    
    // Create download progress element
    const progressContainer = document.createElement('div');
    progressContainer.className = 'download-progress mt-3';
    progressContainer.innerHTML = `
        <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" style="width: 0%">
                <span class="sr-only">Downloading...</span>
            </div>
        </div>
        <small class="text-muted mt-2 d-block">Preparing download...</small>
    `;
    
    // Add progress to download card
    const downloadCard = document.querySelector('.download-card .card-body');
    if (downloadCard) {
        downloadCard.appendChild(progressContainer);
    }
    
    // Simulate download progress
    simulateDownloadProgress(progressContainer);
}

function simulateDownloadProgress(progressContainer) {
    const progressBar = progressContainer.querySelector('.progress-bar');
    const statusText = progressContainer.querySelector('small');
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;
        
        progressBar.style.width = progress + '%';
        
        if (progress < 30) {
            statusText.textContent = 'Connecting to download server...';
        } else if (progress < 60) {
            statusText.textContent = 'Downloading AriTyper.exe...';
        } else if (progress < 90) {
            statusText.textContent = 'Finalizing download...';
        } else if (progress >= 100) {
            statusText.textContent = 'Download complete! Check your downloads folder.';
            clearInterval(interval);
            
            // Show success message
            showToast('Download completed successfully!', 'success');
            
            // Enable the actual download after a delay
            setTimeout(() => {
                triggerActualDownload();
            }, 1000);
        }
    }, 200);
}

function triggerActualDownload() {
    // Track the download
    trackDownload('AriTyper-Setup.exe', 25000000); // ~25MB estimated size
    
    // Create a temporary link for download
    const link = document.createElement('a');
    link.href = '#'; // In production, this would be the actual file URL
    link.download = 'AriTyper-Setup.exe';
    link.style.display = 'none';
    
    // For demo purposes, we'll just show a message
    showToast('In production, this would download the actual AriTyper installer', 'info');
    
    // Remove progress after completion
    setTimeout(() => {
        const progressContainer = document.querySelector('.download-progress');
        if (progressContainer) {
            progressContainer.remove();
        }
    }, 3000);
}

function setupAnimations() {
    // Add fade-in animation to elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all feature cards and sections
    document.querySelectorAll('.feature-card, .pricing-card, .payment-method-card').forEach(el => {
        observer.observe(el);
    });
    
    // Add hover effect to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
    
    // Remove toast element after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Form validation (for contact forms, etc.)
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Phone number validation (for Uganda numbers)
function isValidUgandaPhone(phone) {
    const phoneRegex = /^(\+256|0)[7]\d{8}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Copy to clipboard functionality
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = buttonElement.textContent;
        buttonElement.textContent = 'Copied!';
        buttonElement.classList.add('btn-success');
        buttonElement.classList.remove('btn-outline-primary');
        
        setTimeout(() => {
            buttonElement.textContent = originalText;
            buttonElement.classList.remove('btn-success');
            buttonElement.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Initialize page loading animation
window.addEventListener('load', function() {
    // Hide loading spinner if exists
    const loadingSpinner = document.querySelector('.loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
    
    // Show page content with animation
    document.body.classList.add('fade-in');
});

// Handle keyboard navigation
document.addEventListener('keydown', function(e) {
    // Escape key closes modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Performance optimization: Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll events
window.addEventListener('scroll', debounce(function() {
    // Add any scroll-based animations here
}, 100));

// Analytics tracking (placeholder)
function trackEvent(eventName, properties) {
    // In production, this would send data to analytics service
    console.log('Event tracked:', eventName, properties);
}

// Track download attempts
document.getElementById('downloadBtn')?.addEventListener('click', function() {
    trackEvent('download_attempted', {
        source: 'main_button',
        timestamp: new Date().toISOString()
    });
});

// Track page views
trackEvent('page_view', {
    page: window.location.pathname,
    timestamp: new Date().toISOString()
});
