document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const uploadText = document.getElementById('uploadText');
    const analysisResultsSection = document.getElementById('analysisResultsSection');
    
    if (uploadZone && fileInput) {
        // Highlight drag and drop zone
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            }, false);
        });
        
        // Handle dropped files
        uploadZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                updateFilenameLabel(files[0].name);
            }
        });
        
        // Handle clicked select
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                updateFilenameLabel(fileInput.files[0].name);
            }
        });
    }
    
    function updateFilenameLabel(name) {
        // Basic local validation
        const ext = name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'docx') {
            alert('Invalid file format. Please upload only PDF or DOCX files.');
            fileInput.value = '';
            uploadText.innerHTML = '<i class="fa-solid fa-cloud-arrow-up upload-icon"></i><br>Choose a file or drag it here';
            return;
        }
        
        uploadText.innerHTML = `
            <i class="fa-solid fa-file-circle-check upload-icon" style="color:var(--success)"></i><br>
            <strong style="color:var(--success)">Selected:</strong> ${name}
        `;
    }
    
    // Display Loader when form is submitting
    if (uploadForm) {
        uploadForm.addEventListener('submit', () => {
            if (!fileInput.files.length) return;
            
            // Show processing screen overlay or button loading states
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Reading & Analyzing Document...';
            }
            
            // Add custom inline loaders into the results container if existing
            if (analysisResultsSection) {
                analysisResultsSection.innerHTML = `
                    <div class="analysis-result-card text-center" style="padding: 60px;">
                        <i class="fa-solid fa-spinner fa-spin" style="font-size:3rem;color:var(--primary);margin-bottom:20px;"></i>
                        <h3>Analyzing document structure...</h3>
                        <p style="color:var(--text-secondary);margin-top:10px;">
                            We are parsing your document text, checking for legal terms, and running Gemini context summary. This may take up to 20-30 seconds depending on document length.
                        </p>
                    </div>
                `;
            }
        });
    }
});
