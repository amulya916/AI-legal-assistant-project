document.addEventListener('DOMContentLoaded', () => {
    const noticeTypeSelect = document.getElementById('noticeTypeSelect');
    const dynamicFormFields = document.getElementById('dynamicFormFields');
    const noticeForm = document.getElementById('noticeForm');
    const previewEditor = document.getElementById('previewEditor');
    const saveNoticeBtn = document.getElementById('saveNoticeBtn');
    const copyNoticeBtn = document.getElementById('copyNoticeBtn');
    const noticeIdInput = document.getElementById('noticeIdInput');
    
    // Config of fields for each Notice type
    const noticeFieldsConfig = {
        'consumer_complaint': [
            { id: 'buyer_name', label: 'Buyer / Complainant Name', type: 'text', placeholder: 'e.g. John Doe' },
            { id: 'seller_name', label: 'Seller / Company Name', type: 'text', placeholder: 'e.g. Acme Retailers Ltd.' },
            { id: 'product_details', label: 'Product or Service Details', type: 'text', placeholder: 'e.g. Model X Smartphone purchased on 12/04/2026' },
            { id: 'issue_details', label: 'Defect or Grievance Description', type: 'textarea', placeholder: 'Describe the issue (e.g. screens flickering, refused to replace)...' },
            { id: 'demand_details', label: 'Refund or Compensation Demanded', type: 'text', placeholder: 'e.g. Full refund of $500 plus $100 compensation' }
        ],
        'salary_recovery': [
            { id: 'employee_name', label: 'Employee Name', type: 'text', placeholder: 'e.g. Alice Smith' },
            { id: 'employer_name', label: 'Employer / Company Name', type: 'text', placeholder: 'e.g. TechCorp Innovations' },
            { id: 'designation', label: 'Designation / Job Title', type: 'text', placeholder: 'e.g. Senior Software Engineer' },
            { id: 'unpaid_months', label: 'Months / Period of Unpaid Salary', type: 'text', placeholder: 'e.g. March 2026 and April 2026' },
            { id: 'amount_owed', label: 'Total Amount Owed', type: 'text', placeholder: 'e.g. $8,500' },
            { id: 'compliance_days', label: 'Days for Compliance', type: 'number', placeholder: 'e.g. 15', val: 15 }
        ],
        'rti_application': [
            { id: 'applicant_name', label: 'Applicant Name', type: 'text', placeholder: 'e.g. John Doe' },
            { id: 'department_name', label: 'Public Department / Authority', type: 'text', placeholder: 'e.g. Municipal Corporation of Delhi' },
            { id: 'information_requested', label: 'Specific Details of Information Requested', type: 'textarea', placeholder: 'What documents or records do you require? Be specific...' },
            { id: 'filing_date', label: 'Filing Date', type: 'text', placeholder: 'e.g. 24th May 2026' }
        ],
        'cybercrime_complaint': [
            { id: 'victim_name', label: 'Victim Name', type: 'text', placeholder: 'e.g. Sarah Jenkins' },
            { id: 'nature_of_crime', label: 'Nature of Cybercrime', type: 'text', placeholder: 'e.g. Financial Fraud, Harassment, Identity Theft' },
            { id: 'incident_date', label: 'Incident Date & Time', type: 'text', placeholder: 'e.g. 15th May 2026 around 4:00 PM' },
            { id: 'evidence_details', label: 'Evidence Description', type: 'textarea', placeholder: 'Mention bank statements, WhatsApp screenshots, transactional SMS headers, etc.' },
            { id: 'suspect_details', label: 'Suspect Details (If any)', type: 'text', placeholder: 'e.g. Unknown numbers +91-XXXXX, email domain hackers@mail.com' }
        ],
        'property_dispute': [
            { id: 'owner_name', label: 'Owner / Sender Name', type: 'text', placeholder: 'e.g. Robert Brown' },
            { id: 'disputant_name', label: 'Disputant / Encroacher Name', type: 'text', placeholder: 'e.g. Local Builders Corporation' },
            { id: 'property_address', label: 'Property Address / Description', type: 'text', placeholder: 'e.g. Plot No. 42-A, Green Valley Estates' },
            { id: 'dispute_details', label: 'Description of Dispute', type: 'textarea', placeholder: 'Describe the trespass, encroachment, boundary conflict, etc.' },
            { id: 'demanded_action', label: 'Demanded Rectification Action', type: 'text', placeholder: 'e.g. Demolish encroaching wall, cease trespassing immediately' }
        ]
    };
    
    // Generate input forms based on dropdown
    function renderFields(noticeType) {
        dynamicFormFields.innerHTML = '';
        if (!noticeType || !noticeFieldsConfig[noticeType]) {
            dynamicFormFields.innerHTML = '<p style="color:var(--text-muted);">Please select a notice type to fill details.</p>';
            return;
        }
        
        const fields = noticeFieldsConfig[noticeType];
        fields.forEach(f => {
            const group = document.createElement('div');
            group.className = 'form-group';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.setAttribute('for', f.id);
            label.textContent = f.label;
            
            let input;
            if (f.type === 'textarea') {
                input = document.createElement('textarea');
                input.rows = 4;
            } else {
                input = document.createElement('input');
                input.type = f.type;
                if (f.val) input.value = f.val;
            }
            
            input.id = f.id;
            input.name = f.id;
            input.className = 'form-control';
            input.placeholder = f.placeholder;
            input.required = true;
            
            group.appendChild(label);
            group.appendChild(input);
            dynamicFormFields.appendChild(group);
        });
        
        // Show submission button
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-primary mt-2';
        submitBtn.style.width = '100%';
        submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Notice Draft';
        dynamicFormFields.appendChild(submitBtn);
    }

    // Trigger on load and change
    if (noticeTypeSelect) {
        renderFields(noticeTypeSelect.value);
        noticeTypeSelect.addEventListener('change', () => {
            renderFields(noticeTypeSelect.value);
        });
    }

    // Handle AJAX Save Change request
    if (saveNoticeBtn && previewEditor) {
        saveNoticeBtn.addEventListener('click', async () => {
            const noticeId = noticeIdInput ? noticeIdInput.value : null;
            const updatedText = previewEditor.value;
            
            if (!noticeId) {
                alert('No active notice draft found to save.');
                return;
            }
            
            saveNoticeBtn.disabled = true;
            saveNoticeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            
            try {
                const response = await fetch('/notice/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ notice_id: noticeId, generated_text: updatedText })
                });
                
                const data = await response.json();
                saveNoticeBtn.disabled = false;
                saveNoticeBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save Edits';
                
                if (data.success) {
                    alert('Draft edits saved successfully.');
                } else {
                    alert(`Error saving edits: ${data.error}`);
                }
            } catch (err) {
                saveNoticeBtn.disabled = false;
                saveNoticeBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save Edits';
                alert('Connection failure. Could not connect to server.');
            }
        });
    }

    // Handle Clipboard Copy
    if (copyNoticeBtn && previewEditor) {
        copyNoticeBtn.addEventListener('click', () => {
            previewEditor.select();
            document.execCommand('copy');
            
            const originalHTML = copyNoticeBtn.innerHTML;
            copyNoticeBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            copyNoticeBtn.className = 'btn btn-outline btn-sm';
            
            setTimeout(() => {
                copyNoticeBtn.innerHTML = originalHTML;
            }, 2000);
        });
    }
});
