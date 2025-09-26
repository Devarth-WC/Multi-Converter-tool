// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize theme handling
    initializeTheme();
    
    // Initialize file upload enhancements
    initializeFileUpload();
    
    // Initialize form validations
    initializeFormValidation();
    
    // Initialize animations
    initializeAnimations();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Theme handling (future enhancement)
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
}

// Enhanced file upload functionality
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Add file size validation
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (50MB limit)
                const maxSize = 50 * 1024 * 1024; // 50MB in bytes
                if (file.size > maxSize) {
                    showAlert('File size too large. Maximum allowed size is 50MB.', 'error');
                    input.value = '';
                    return false;
                }
                
                // Check file type
                if (!isValidFileType(file.name)) {
                    showAlert('Unsupported file type. Please select a valid file.', 'error');
                    input.value = '';
                    return false;
                }
            }
        });
    });
}

// Validate file types
function isValidFileType(filename) {
    const allowedExtensions = [
        'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 
        'mp3', 'wav', 'ogg', 'flac', 'm4a'
    ];
    
    const extension = filename.split('.').pop().toLowerCase();
    return allowedExtensions.includes(extension);
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showAlert('Please fill in all required fields correctly.', 'error');
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Initialize animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    
    alertContainer.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find or create alert container
    let container = document.querySelector('.alert-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'alert-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    container.appendChild(alertContainer);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Get appropriate icon for alert type
function getAlertIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'exclamation-triangle',
        'danger': 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

// File size formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Copy text to clipboard
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    if (navigator.clipboard && window.isSecureContext) {
        // Use modern clipboard API
        navigator.clipboard.writeText(text).then(() => {
            showAlert(successMessage, 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(text, successMessage);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(text, successMessage);
    }
}

// Fallback copy method
function fallbackCopyTextToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert(successMessage, 'success');
    } catch (err) {
        showAlert('Failed to copy text', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Enhanced drag and drop functionality
function initializeDragDrop() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(dropZone => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        dropZone.addEventListener('drop', handleDrop, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        e.currentTarget.classList.add('dragover');
    }
    
    function unhighlight(e) {
        e.currentTarget.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = e.currentTarget.querySelector('input[type="file"]') || 
                         document.querySelector('input[type="file"]');
        
        if (fileInput && files.length > 0) {
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
}

// Progress bar animation
function animateProgress(progressBar, targetPercent, duration = 2000) {
    const startTime = Date.now();
    const startPercent = parseFloat(progressBar.style.width) || 0;
    
    function updateProgress() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentPercent = startPercent + (targetPercent - startPercent) * progress;
        
        progressBar.style.width = currentPercent + '%';
        progressBar.setAttribute('aria-valuenow', currentPercent);
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

// Smooth scroll to element
function smoothScrollTo(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// Form submission with loading state
function handleFormSubmission(form, submitButton) {
    const originalText = submitButton.innerHTML;
    const loadingText = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    // Set loading state
    submitButton.innerHTML = loadingText;
    submitButton.disabled = true;
    
    // Show progress if progress bar exists
    const progressBar = form.querySelector('.progress');
    if (progressBar) {
        progressBar.style.display = 'block';
        const progressBarFill = progressBar.querySelector('.progress-bar');
        if (progressBarFill) {
            animateProgress(progressBarFill, 90, 3000);
        }
    }
    
    // Reset function (call this when form submission completes or fails)
    return function resetForm() {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
        if (progressBar) {
            progressBar.style.display = 'none';
        }
    };
}

// Enhanced file preview
function createFilePreview(file) {
    const previewContainer = document.createElement('div');
    previewContainer.className = 'file-preview mt-3';
    
    const fileType = getFileType(file.name);
    let previewContent = '';
    
    // Create preview based on file type
    if (fileType === 'image' && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewContent = `
                <div class="text-center">
                    <img src="${e.target.result}" alt="Preview" 
                         class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                </div>
            `;
            previewContainer.innerHTML = previewContent;
        };
        reader.readAsDataURL(file);
    } else {
        // Generic file preview
        const icon = getFileIcon(fileType);
        previewContent = `
            <div class="text-center">
                <i class="fas ${icon} fa-4x text-primary mb-2"></i>
                <p class="mb-0 fw-bold">${file.name}</p>
                <small class="text-muted">${formatFileSize(file.size)}</small>
            </div>
        `;
        previewContainer.innerHTML = previewContent;
    }
    
    return previewContainer;
}

// Get file type category
function getFileType(filename) {
    const ext = filename.toLowerCase().split('.').pop();
    if (ext === 'pdf') return 'pdf';
    if (['docx', 'txt'].includes(ext)) return 'document';
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return 'image';
    if (['mp3', 'wav', 'ogg', 'flac', 'm4a'].includes(ext)) return 'audio';
    return 'unknown';
}

// Get appropriate icon for file type
function getFileIcon(fileType) {
    const icons = {
        'pdf': 'fa-file-pdf',
        'document': 'fa-file-alt',
        'image': 'fa-file-image',
        'audio': 'fa-file-audio',
        'unknown': 'fa-file'
    };
    return icons[fileType] || 'fa-file';
}

// Initialize all functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDragDrop();
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                smoothScrollTo(target, 80);
            }
        });
    });
    
    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                handleFormSubmission(form, submitButton);
            }
        });
    });
    
    // Initialize file preview functionality
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Remove existing preview
                const existingPreview = this.parentNode.querySelector('.file-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                // Add new preview
                const preview = createFilePreview(file);
                this.parentNode.appendChild(preview);
            }
        });
    });
});

// Global utilities
window.FileConverter = {
    copyToClipboard,
    formatFileSize,
    showAlert,
    getFileType,
    animateProgress,
    smoothScrollTo
};

// Service Worker registration (for future PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js').then(function(registration) {
            console.log('ServiceWorker registration successful');
        }, function(err) {
            console.log('ServiceWorker registration failed');
        });
    });
}