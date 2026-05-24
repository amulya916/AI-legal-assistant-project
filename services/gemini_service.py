import google.generativeai as genai
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def _get_model():
    """Configure and retrieve the Gemini generative model. Fallback to mock if API key is not set."""
    api_key = current_app.config['GEMINI_API_KEY']
    # If key is missing, empty, or a dummy placeholder, use Simulator Mode
    if not api_key or not api_key.strip() or "your_gemini" in api_key.lower() or "placeholder" in api_key.lower():
        logger.warning("GEMINI_API_KEY is not configured or is a placeholder. Using simulator mode.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Use gemini-2.0-flash as the primary default model
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        return None

def generate_chat_response(message, chat_history=None):
    """
    Generate conversational chatbot response using Gemini API.
    Accommodates past conversation history.
    """
    model = _get_model()
    
    if not model:
        return _get_mock_chat_response(message)
    
    # Structure system instructions and history
    system_instruction = (
        "You are 'AdvoBot', an advanced AI Legal Assistant. "
        "Your role is to help users understand legal concepts, consumer rights, labor laws, "
        "women's rights, property disputes, senior citizen privileges, government schemes, and general legal procedures. "
        "Provide detailed, structured responses with markdown formatting (bullet points, bold text). "
        "Keep your tone professional, empathetic, and informative. "
        "CRITICAL: Always append a standard disclaimer stating: "
        "'Disclaimer: This information is for educational and informational purposes only. "
        "It does not constitute professional legal advice. Please consult a qualified attorney for specific legal matters.'"
    )
    
    prompt = f"{system_instruction}\n\n"
    if chat_history:
        prompt += "Conversation history:\n"
        for chat in chat_history[-6:]:  # include up to last 6 messages
            prompt += f"User: {chat['message']}\nAssistant: {chat['response']}\n"
    
    prompt += f"\nUser's new message: {message}\nAssistant:"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        err_msg = str(e)
        warning_type = "Quota exceeded or network issue"
        if "quota" in err_msg.lower() or "429" in err_msg:
            warning_type = "Gemini API Quota Exceeded (429)"
        elif "api key" in err_msg.lower() or "key not found" in err_msg.lower() or "400" in err_msg:
            warning_type = "Invalid API Key or project setup"
            
        mock_response = _get_mock_chat_response(message)
        warning_note = f"\n\n*(Note: Local simulator fallback active. Live Gemini API returned an error: {warning_type}. See [docs](https://ai.google.dev/gemini-api/docs/rate-limits) to resolve.)*"
        return mock_response + warning_note

def analyze_legal_situation(situation):
    """
    Analyze a detailed situation submitted by the user.
    Breaks it down into relevant Rights, Next Steps, and Applicable Laws.
    """
    model = _get_model()
    
    if not model:
        return _get_mock_rights_analysis(situation)
    
    prompt = (
        f"You are a Senior Legal Analyst. Analyze the following legal situation described by a user:\n"
        f"\"{situation}\"\n\n"
        f"Provide a structured legal evaluation covering the following parts:\n"
        f"1. **Overview & Analysis**: Explain what the issue is and what core disputes are involved.\n"
        f"2. **Legal Rights Involved**: Detail the specific rights the user has under the law (e.g. Labor law, Consumer law, etc.).\n"
        f"3. **Recommended Actions**: Provide a step-by-step list of concrete actions the user should take (e.g. sending a notice, filing a complaint, gathering evidence).\n"
        f"4. **Key Laws & Regulations**: List relevant acts, laws, or legal precedents that apply to this situation.\n\n"
        f"Ensure the formatting is clean markdown. Include a disclaimer at the end."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini Rights Finder API request failed: {e}")
        mock_response = _get_mock_rights_analysis(situation)
        warning_note = f"\n\n*(Note: Local simulator fallback active. Live Gemini API error: {str(e)})*"
        return mock_response + warning_note

def generate_legal_notice(notice_type, form_data):
    """
    Generate formal legal notices based on specific forms.
    Returns standard legal notice format.
    """
    model = _get_model()
    
    # Format details into readable context
    details_str = ""
    for key, val in form_data.items():
        details_str += f"- {key.replace('_', ' ').title()}: {val}\n"
        
    if not model:
        return _get_mock_legal_notice(notice_type, form_data)
        
    prompt = (
        f"You are a legal document generator. Draft a formal, professional Legal Notice of type: '{notice_type}'.\n"
        f"Use the following parameters provided by the user:\n"
        f"{details_str}\n"
        f"Requirements:\n"
        f"- Format it strictly as a legal document. It should include typical sections: Date, Sender/Recipient headers, "
        f"Subject line, Detailed representation of facts, Specific demands/remedies, timeline for compliance (e.g. 15 days), "
        f"and warning of legal action if not complied with.\n"
        f"- Write the content clearly and formally. Do not use placeholders (like [insert date here]); generate reasonable content "
        f"based on the form data, and if any standard field is missing, draft a professional placeholder or compute it logically.\n"
        f"Provide the raw text of the notice that can be printed or edited."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini Notice Generator API request failed: {e}")
        mock_response = _get_mock_legal_notice(notice_type, form_data)
        warning_note = f"\n\n*(Generated in Local Simulator Mode because Gemini API request failed: {str(e)})*"
        return mock_response + warning_note

def analyze_document(text):
    """
    Analyze the raw text extracted from a PDF/DOCX.
    Generates summary, important points, key clauses, and simplified explanation.
    """
    model = _get_model()
    
    if not model:
        return _get_mock_document_analysis(text)
        
    prompt = (
        f"You are an Expert Document Auditor. Carefully review the following text extracted from a legal document:\n\n"
        f"\"\"\"\n{text[:8000]}\n\"\"\"\n\n" # Limiting text length for prompt limits
        f"Analyze this document and output a structured markdown summary with these sections:\n"
        f"1. **Executive Summary**: A brief, 3-4 sentence overview of what this document is and its main purpose.\n"
        f"2. **Key Clauses & Important Points**: Bullets detailing critical responsibilities, deadlines, amounts, or terms.\n"
        f"3. **Obligations & Penalties**: Specific duties of each party and consequences of breach or termination.\n"
        f"4. **Simplified Explanations**: Translate the most complex legalese found in the text into simple, layperson terms.\n\n"
        f"Make sure to keep the explanations very clear, readable, and well-structured."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini Document Analyzer API request failed: {e}")
        mock_response = _get_mock_document_analysis(text)
        warning_note = f"\n\n*(Note: Local simulator fallback active. Live Gemini API error: {str(e)})*"
        return mock_response + warning_note

# --- MOCK SIMULATOR FALLBACKS (If API key is missing) ---

def _get_mock_chat_response(message):
    msg_lower = message.lower()
    disclaimer = ("\n\n*Disclaimer: This simulated information is for educational purposes only. "
                  "It does not constitute professional legal advice.*")
    
    # Detect if they are asking for additional details or specific procedures
    is_asking_details = any(w in msg_lower for w in ["detail", "more", "explain", "describe", "elaborate", "specify", "what else", "tell me about"])
    is_asking_how = any(w in msg_lower for w in ["how to", "steps", "procedure", "process", "action", "file", "report"])
    
    # 1. Cybercrime & Cyber harassment
    if any(w in msg_lower for w in ["cyber", "fraud", "online", "phishing", "hack", "scam", "internet", "harass", "crime", "bully"]):
        response = "### Cybercrime Protection & Legal Redressal\n\n"
        
        # Check subcategories
        if any(w in msg_lower for w in ["money", "bank", "card", "transaction", "otp", "financial", "rupee", "payment", "fund"]):
            response += (
                "Regarding your query on **online financial fraud or unauthorized transactions**:\n\n"
                "1. **The Golden Hour Rule**: Contact your bank or payment wallet company immediately (ideally within 2 hours) to report the fraud. Request that the transaction be recalled/frozen.\n"
                "2. **National Helpline**: Call the National Cyber Financial Fraud Helpline at **1930** immediately. Authorities have the capability to freeze funds in transit across bank networks if reported promptly.\n"
                "3. **Portal Complaint**: File a complaint at `cybercrime.gov.in` with proof of transactions, bank statements, and relevant messages."
            )
        elif any(w in msg_lower for w in ["harass", "stalk", "bully", "abuse", "threat", "photo", "profile", "social", "instagram", "facebook"]):
            response += (
                "Regarding your query on **cyber harassment, online bullying, or social media profile issues**:\n\n"
                "1. **Preserve Digital Evidence**: Take high-resolution screenshots of the threats, comments, or fake profiles, including URLs and timestamps. Do not delete the communication logs.\n"
                "2. **Platform Reporting**: Use the platform's reporting forms to get the offending content taken down immediately.\n"
                "3. **Cyber Cell Action**: File an online complaint at `cybercrime.gov.in` under the 'Women/Child Cybercrime' or 'Report other cybercrime' sections. You can request anonymity if needed."
            )
        elif any(w in msg_lower for w in ["hack", "password", "email", "account", "login", "malware", "virus"]):
            response += (
                "Regarding your query on **hacking, password security, or account compromise**:\n\n"
                "1. **Credential Reset**: Try resetting your passwords using the recovery email/phone. Change credentials on all services using identical passwords.\n"
                "2. **Active Sessions**: Terminate all unrecognized sessions in the account security panel.\n"
                "3. **Enable 2-Factor Authentication (2FA)**: Activate multi-factor verification on all critical email, banking, and social accounts immediately.\n"
                "4. **Security Scan**: Run an anti-malware tool to check for keyloggers or spyware on your local device."
            )
        else:
            response += (
                "If you are dealing with a cybercrime incident, follow these baseline steps:\n\n"
                "- **Report Fast**: File a report on the official Cybercrime Portal (`cybercrime.gov.in`) or contact the local Police Cyber Cell.\n"
                "- **Notify Institutions**: If financial details or cards are exposed, block them immediately via your bank.\n"
                "- **Save Records**: Keep screenshots of chats, transactional alerts, and email records as primary evidence.\n\n"
                "To get tailored advice, you can ask me about *financial fraud*, *harassment*, or *account hacking* specifically."
            )
            
        if is_asking_details:
            response += (
                "\n\n**Key Legal Sections (under the Information Technology Act):**\n"
                "- **Section 66C**: Punishes identity theft (stealing passwords, biometric data, digital signatures) with up to 3 years imprisonment.\n"
                "- **Section 66D**: Punishes cheating by impersonation using a computer resource.\n"
                "- **Section 67**: Punishes publishing or transmitting obscene materials in electronic form."
            )
        return response + disclaimer

    # 2. Consumer Rights
    elif any(w in msg_lower for w in ["consumer", "defect", "refund", "retailer", "product", "seller", "warranty", "shop", "buy", "purchase"]):
        response = "### Consumer Rights & Grievance Actions\n\n"
        
        if any(w in msg_lower for w in ["refund", "return", "charge", "exchange", "money"]):
            response += (
                "Regarding your query on **refunds or returns for products**:\n\n"
                "1. **Defective Goods**: Under consumer protection rules, a buyer has a right to a full refund, repair, or replacement if the item is defective or doesn't match descriptions.\n"
                "2. **Unfair Terms**: Store policies claiming 'Strictly No Refunds/Exchanges' are legally void if they sell a damaged or incorrect product.\n"
                "3. **Demand Notice**: Send a written letter/notice to the shop or manufacturer requesting a refund or replacement within 7 to 14 days."
            )
        elif any(w in msg_lower for w in ["warranty", "guarantee", "repair", "service"]):
            response += (
                "Regarding your query on **warranties or service deficiencies**:\n\n"
                "1. **Warranty Compliance**: The manufacturer must repair or replace the product for free during the warranty period, provided there is no external damage or misuse.\n"
                "2. **Service Failure**: If a service center delays repairs indefinitely (e.g. over 30 days), this constitutes a deficiency of service, and you can demand a replacement unit."
            )
        else:
            response += (
                "Under the Consumer Protection Act, 2019, you have the following rights:\n\n"
                "- **Right to be Informed**: Right to know product specs, quantity, price, and standards.\n"
                "- **Right to Redressal**: Right to seek legal remedies against unfair trade practices or defective goods.\n"
                "- **Action Plan**: First, register a complaint on the National Consumer Helpline (NCH). If it remains unresolved, file a formal complaint in the District Consumer Disputes Redressal Commission."
            )
            
        if is_asking_details:
            response += (
                "\n\n**Financial Jurisdiction (for filing cases):**\n"
                "- **District Commission**: Handles claims up to ₹50 Lakhs.\n"
                "- **State Commission**: Handles claims between ₹50 Lakhs and ₹2 Crores.\n"
                "- **National Commission**: Handles claims exceeding ₹2 Crores."
            )
        return response + disclaimer

    # 3. Labor & Employment Rights
    elif any(w in msg_lower for w in ["labor", "salary", "pay", "employer", "boss", "job", "terminate", "fired", "work"]):
        response = "### Labor & Employment Rights\n\n"
        
        if any(w in msg_lower for w in ["terminate", "fired", "resign", "notice", "severance", "dismiss"]):
            response += (
                "Regarding your query on **termination or notice periods**:\n\n"
                "1. **Notice Clause**: Employers must give the notice specified in your contract (usually 30-90 days) or pay wages in lieu of that period.\n"
                "2. **Wrongful Dismissal**: Retaliatory termination (e.g. for complaining about wages) is illegal. You can appeal to the labor office under state Shop & Establishment rules.\n"
                "3. **Severance & Gratuity**: If you have worked continuously for 5+ years, you are legally entitled to gratuity payment upon exit."
            )
        elif any(w in msg_lower for w in ["salary", "pay", "unpaid", "delay", "dues", "wage"]):
            response += (
                "Regarding your query on **recovering unpaid or delayed salary**:\n\n"
                "1. **Wages Timeline**: Salaries should be paid by the 7th or 10th day of the following month depending on company size.\n"
                "2. **Send Legal Notice**: Serve the employer a formal demand letter giving them 15 days to clear the outstanding salary. You can use our **Notice Builder** in the dashboard to generate this.\n"
                "3. **Labor Commissioner**: File a complaint with the regional Labor Conciliation Officer. They will summon the employer for mediation."
            )
        else:
            response += (
                "Employees are protected against unpaid wages and arbitrary contract violations:\n\n"
                "- **Timely Wages**: Right to receive salary in full without arbitrary deductions.\n"
                "- **Overtime Rights**: Work hours exceeding 8-9 hours daily must be compensated with double the standard wage rate.\n\n"
                "**Action Plan**: Keep all pay slips, employment contract, attendance logs, and emails confirming work done."
            )
            
        if is_asking_details:
            response += (
                "\n\n**Applicable Statutes:**\n"
                "- **Payment of Wages Act, 1936**: Safeguards timely wages payment.\n"
                "- **Industrial Disputes Act, 1947**: Protects rights of workers regarding layoffs and unfair retrenchments."
            )
        return response + disclaimer

    # 4. RTI
    elif any(w in msg_lower for w in ["rti", "information", "right to info", "public officer", "pio"]):
        response = "### Right to Information (RTI) Filing Guide\n\n"
        
        if is_asking_how or "file" in msg_lower or "apply" in msg_lower:
            response += (
                "**How to File an RTI Application:**\n\n"
                "1. **Draft Specific Questions**: Write direct questions asking for records, logs, circulars, or documents. Avoid asking for opinions or reasons (e.g. ask 'Provide a copy of the road repairs budget' rather than 'Why is the road not repaired?').\n"
                "2. **Find the Public Authority**: Determine which government department holds the records.\n"
                "3. **Submit application**: Apply online via `rtionline.gov.in` (for central departments) or submit via registered Speed Post to the Public Information Officer (PIO) with the application fee."
            )
        else:
            response += (
                "The RTI Act is a powerful transparency tool:\n\n"
                "- **Response Timeframe**: The PIO has to respond within **30 days** of receipt.\n"
                "- **First Appeal**: If the response is delayed, incomplete, or rejected, file a First Appeal to the First Appellate Authority (FAA) within 30 days."
            )
        return response + disclaimer

    # 5. Property Disputes
    elif any(w in msg_lower for w in ["property", "dispute", "tenant", "land", "house", "rent", "evict"]):
        response = "### Property & Tenancy Rights\n\n"
        
        if any(w in msg_lower for w in ["tenant", "rent", "evict", "landlord", "deposit"]):
            response += (
                "Regarding your query on **landlord-tenant rent or eviction disputes**:\n\n"
                "1. **Eviction Procedure**: Forceful eviction is illegal. Landlords must follow the legal eviction route via the Rent Control Authority.\n"
                "2. **Utilities Interruption**: Cutting off electricity, water, or internet to pressure a tenant to leave is a punishable offense under state Rent Control Acts.\n"
                "3. **Security Deposit Recovery**: If your deposit is withheld arbitrarily, send a legal notice demanding refund with interest. If ignored, approach the Rent Tribunal."
            )
        else:
            response += (
                "Property disputes are civil in nature:\n\n"
                "- **Contracts**: Always ensure a registered Lease Agreement or Sale Deed is signed.\n"
                "- **Encroachments**: Encroachment disputes require filing a civil suit for injunction and possession, backed by municipal survey documents."
            )
        return response + disclaimer

    # 6. Default Fallback
    else:
        words = [w for w in msg_lower.split() if len(w) > 4]
        keyword_echo = f" \"{words[0]}\"" if words else ""
        
        # Check if API key is configured
        api_key = current_app.config.get('GEMINI_API_KEY', '')
        has_key = api_key and api_key.strip() and "your_gemini" not in api_key.lower() and "placeholder" not in api_key.lower()
        
        if has_key:
            reason = "Because the live Gemini API returned an error (such as a Quota Exceeded block), I am running in local simulator mode."
            setup_instructions = ""
        else:
            reason = "Because **GEMINI_API_KEY is currently blank** in the backend `.env` file, I am running in local simulator mode."
            setup_instructions = (
                f"**To Enable Real AI responses:**\n"
                f"To get fully dynamic, adaptive, and detailed answers that perfectly address your questions (including details on cybercrimes or complex scenarios), "
                f"please open the file [`.env`](file:///c:/Users/bhaga/ailegalproject/.env) and enter a valid Google Gemini API Key on line 9:\n"
                f"```env\n"
                f"GEMINI_API_KEY=AIzaSy...\n"
                f"```\n\n"
            )
        
        return (
            f"### AI Assistant Response\n\n"
            f"Thank you for your question about{keyword_echo}: \"{message}\"\n\n"
            f"I see you are asking for details outside our basic simulation templates. "
            f"{reason}\n\n"
            f"In simulator mode, I can provide general templates and guides for:\n"
            f"- **Consumer Rights** (refunds, defects, warranties)\n"
            f"- **Cybercrime & Fraud** (online financial fraud, harassment, hacking)\n"
            f"- **Labor & Employment** (unpaid salary, notice periods, termination)\n"
            f"- **RTI Filings & Property Rules**\n\n"
            f"{setup_instructions}"
            + disclaimer
        )

def _get_mock_rights_analysis(situation):
    return (
        "## Legal Situation Analysis (Simulated)\n\n"
        "### 1. Overview & Analysis\n"
        f"You submitted the following situation: *\"{situation}\"*\n"
        "Based on a general analysis, this situation involves a potential civil or statutory violation. "
        "It suggests a breach of agreed-upon terms, statutory obligations, or standard legal protocols.\n\n"
        "### 2. Legal Rights Involved\n"
        "- **Right to Fair Treatment / Performance**: You are entitled to receive services/wages/goods as mutually agreed upon.\n"
        "- **Right to Protection from Breach**: The default or failure of the counterparty gives you the right to seek damages, specific performance, or statutory fines.\n"
        "- **Right to Redressal**: Access to appropriate administrative or judicial boards (e.g., Labor Commissioner, Consumer Forum, Civil Courts).\n\n"
        "### 3. Recommended Actions\n"
        "1. **Send a Demand Letter (Legal Notice)**: Formally write to the defaulting party specifying the breach and demanding rectification within 10 to 15 days.\n"
        "2. **Collect Evidence**: Compile all emails, text messages, receipts, service logs, contracts, or bank statements.\n"
        "3. **Initiate Mediation / File a Complaint**: If they refuse to comply, approach the relevant government regulator, labor officer, or consumer portal.\n\n"
        "### 4. Key Laws & Regulations\n"
        "- **Indian Contract Act, 1872** (or local civil code equivalent) regarding breach of contract.\n"
        "- **Payment of Wages Act / Labor Laws** (if labor related).\n"
        "- **Consumer Protection Act, 2019** (if service or goods related).\n\n"
        "*(Note: Gemini API key is missing. This analysis was generated by the local simulator module.)*\n\n"
        "**Disclaimer: This simulated analysis is for educational purposes. Consult a licensed lawyer to seek formal counsel.**"
    )

def _get_mock_legal_notice(notice_type, form_data):
    details_str = ""
    for k, v in form_data.items():
        details_str += f"**{k.upper()}**: {v}\n"
        
    notice_title = notice_type.replace('_', ' ').upper()
    
    return (
        f"============================================================\n"
        f"                 FORMAL LEGAL DEMAND NOTICE                 \n"
        f"============================================================\n\n"
        f"Date: 24th May 2026\n\n"
        f"TO,\n"
        f"Recipient Party / Defaulting Organization\n"
        f"Details: {form_data.get('employer_name', form_data.get('seller_name', form_data.get('recipient_details', 'Opposing Party')))}\n\n"
        f"FROM,\n"
        f"Sender Party / Aggrieved Client\n"
        f"Details: {form_data.get('employee_name', form_data.get('buyer_name', form_data.get('applicant_name', 'Claimant Name')))}\n\n"
        f"SUBJECT: LEGAL NOTICE FOR NOTICE TYPE: {notice_title}\n\n"
        f"Dear Sir/Madam,\n\n"
        f"Under instructions from my client, I hereby serve you with the following Legal Notice:\n\n"
        f"1. That you entered into a transaction/employment contract with my client. The relevant details provided are:\n"
        f"{details_str}\n"
        f"2. That you have defaulted on your legal/contractual obligations, resulting in severe mental harassment, financial losses, and breach of trust to my client.\n\n"
        f"3. In the light of the facts stated above, my client hereby demands that you satisfy the outstanding grievances (including payments, delivery of goods, or information requested) within fifteen (15) days of receipt of this notice.\n\n"
        f"4. If you fail to comply with the terms of this notice, my client will be constrained to initiate appropriate legal proceedings against you in a court of law, holding you fully liable for all legal costs, interest, and damages.\n\n"
        f"Sincerely,\n\n"
        f"[Signature / Legal Counsel]\n\n"
        f"------------------------------------------------------------\n"
        f"*(Generated in Simulator Mode because GEMINI_API_KEY is not configured.)*"
    )

def _get_mock_document_analysis(text):
    text_snippet = text[:150]
    return (
        "## Uploaded Document Analysis (Simulated)\n\n"
        "### 1. Executive Summary\n"
        f"This document appears to be a formal legal agreement or letter. The document starts with: *\"{text_snippet}...\"* "
        "The analysis indicates that it is a standard business or legal filing, binding the signatories to the clauses outlined inside.\n\n"
        "### 2. Key Clauses & Important Points\n"
        "- **Identities**: Contains definitions of the parties involved.\n"
        "- **Subject Matter**: Outlines the core transaction, terms, or services being rendered.\n"
        "- **Effective Date**: Represents the start date for the legal obligations.\n\n"
        "### 3. Obligations & Penalties\n"
        "- **Performance**: Parties must complete duties outlined in the document text.\n"
        "- **Termination**: Clauses describing how the agreement can be dissolved, and standard notification windows (typically 30 days).\n\n"
        "### 4. Simplified Explanations\n"
        "- *Legalese*: \"Indemnification and hold harmless...\"\n"
        "  - *Simplified*: One party agrees to pay for any lawsuit costs or losses the other party experiences due to their actions.\n"
        "- *Legalese*: \"Force Majeure...\"\n"
        "  - *Simplified*: Neither party is blamed if a major, uncontrollable event (like a flood or war) stops them from doing their job.\n\n"
        "*(Note: Gemini API is in Simulator mode. For deep contextual extraction, configure a valid GEMINI_API_KEY.)*"
    )
