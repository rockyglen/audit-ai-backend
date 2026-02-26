# 📊 AuditAI: RAG Evaluation Report

Generated on: 2026-02-26 13:36:19

## 🏛️ Executive Summary
Below are the average scores across all evaluated metrics.

| Metric | Score | Status |
| :--- | :--- | :--- |
| **Faithfulness** | `1.0000` | ✅ Passing |
| **Answer Relevancy** | `0.7644` | ✅ Passing |
| **Context Precision** | `0.7838` | ✅ Passing |
| **Context Recall** | `0.9000` | ✅ Passing |

---

## 📝 Detailed Performance Breakdown

### Question 1
**Question:** What are the 6 functions of the NIST CSF 2.0?

**AI Answer:** According to the document **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0 (February 26, 2024)**, the six functions that organize cybersecurity outcomes at their highest level are:

1.  **GOVERN (GV):** The organization’s cybersecurity risk management strategy, expectations, and policy are established, communicated, and monitored.
2.  **IDENTIFY (ID):** The organization’s current cybersecurity risks are understood.
3.  **PROTECT (PR):** Safeguards to manage the organization’s cybersecurity risks are used.
4.  **DETECT (DE):** Possible cybersecurity attacks and compromises are found and analyzed.
5.  **RESPOND (RS):** Actions regarding a detected cybersecurity incident are taken.
6.  **RECOVER (RC):** Assets and operations affected by a cybersecurity incident are restored.

**Ground Truth:** The 6 functions of the NIST CSF 2.0 are Govern, Identify, Protect, Detect, Respond, and Recover.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7804`
- Context Precision: `0.4683`
- Context Recall: `1.0000`

---

### Question 2
**Question:** What is the purpose of the Govern function?

**AI Answer:** According to **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, the purpose of the **GOVERN (GV)** function is to ensure the organization’s cybersecurity risk management strategy, expectations, and policy are established, communicated, and monitored. 

The document details the following specific purposes and roles for the GOVERN function:

*   **Strategic Alignment:** It provides outcomes to inform what an organization may do to achieve and prioritize the outcomes of the other five Functions (Identify, Protect, Detect, Respond, and Recover) in the context of its mission and stakeholder expectations.
*   **Enterprise Integration:** It is critical for incorporating cybersecurity into an organization’s broader enterprise risk management (ERM) strategy.
*   **Executive Communication:** It supports organizational risk communication with executives, facilitating discussions on strategy, risk appetite, accountability, and resources.
*   **Scope of Oversight:** It addresses the understanding of organizational context; cybersecurity supply chain risk management; roles, responsibilities, and authorities; policy; and the oversight of cybersecurity strategy.
*   **Incident Management:** GOVERN outcomes help both in preventing and preparing for incidents, as well as discovering and managing them. 

The document further notes that GOVERN is positioned at the center of the CSF "wheel" because it informs how an organization implements all other functions.

**Ground Truth:** The Govern function establishes and monitors the organization's cybersecurity risk management strategy, expectations, and policy.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7851`
- Context Precision: `0.9478`
- Context Recall: `1.0000`

---

### Question 3
**Question:** Define the Detect function.

**AI Answer:** According to the document **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0** and the provided context, the **DETECT (DE)** function is defined as the process where "possible cybersecurity attacks and compromises are found and analyzed."

The provided context further details the function as follows:

*   **Purpose:** It enables the timely discovery and analysis of anomalies, indicators of compromise, and other potentially adverse events that may indicate cybersecurity attacks and incidents are occurring. This function is designed to support successful incident response and recovery activities.
*   **Relationship to other Functions:** According to the context describing the "CSF Functions as a wheel," investments in planning and testing within the GOVERN and IDENTIFY Functions support the timely detection of unexpected events in the DETECT Function.
*   **Categories and Outcomes:** The DETECT function is organized into two primary categories:
    *   **Continuous Monitoring (DE.CM):** Assets are monitored to find anomalies and adverse events. This includes monitoring networks and network services (DE.CM-01), the physical environment (DE.CM-02), personnel activity and technology usage (DE.CM-03), external service provider activities (DE.CM-06), and computing hardware, software, and data (DE.CM-09).
    *   **Adverse Event Analysis (DE.AE):** Anomalies and indicators are analyzed to characterize events and detect incidents. This includes analyzing events to understand activities (DE.AE-02), correlating information from multiple sources (DE.AE-03), understanding the estimated impact and scope (DE.AE-04), providing information to authorized staff and tools (DE.AE-06), integrating cyber threat intelligence (DE.AE-07), and declaring incidents when criteria are met (DE.AE-08).

**Ground Truth:** The Detect function focuses on enabling the timely discovery and analysis of anomalies, indicators of compromise, and other potentially adverse events.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7485`
- Context Precision: `0.8667`
- Context Recall: `1.0000`

---

### Question 4
**Question:** What does the Respond function entail?

**AI Answer:** According to the **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, the Respond (RS) function entails taking actions regarding a detected cybersecurity incident to contain its effects. The framework specifies that Respond outcomes cover incident management, analysis, mitigation, reporting, and communication.

The Respond function is divided into the following categories and subcategories:

*   **Incident Management (RS.MA):** Responses to detected incidents are managed. This includes:
    *   Executing the incident response plan in coordination with third parties (RS.MA-01).
    *   Triaging, validating, categorizing, and prioritizing incidents (RS.MA-02, RS.MA-03).
    *   Escalating or elevating incidents as needed (RS.MA-04).
    *   Applying criteria for initiating incident recovery (RS.MA-05).
*   **Incident Analysis (RS.AN):** Investigations are conducted to support forensics and recovery. This includes:
    *   Performing analysis to establish what took place and the root cause (RS.AN-03).
    *   Recording investigation actions and preserving the integrity and provenance of records, data, and metadata (RS.AN-06, RS.AN-07).
    *   Estimating and validating the incident's magnitude (RS.AN-08).
*   **Incident Response Reporting and Communication (RS.CO):** Activities are coordinated with stakeholders. This includes:
    *   Notifying internal and external stakeholders (RS.CO-02).
    *   Sharing information with designated stakeholders (RS.CO-03).
*   **Incident Mitigation (RS.MI):** Activities are performed to prevent the expansion of an event. This includes:
    *   Containing incidents (RS.MI-01).
    *   Eradicating incidents (RS.MI-02).

The document further notes that actions supporting the Respond function should be "ready at all times" and occur whenever cybersecurity incidents are detected.

**Ground Truth:** The Respond function includes activities to take action regarding a detected cybersecurity incident, such as incident management, analysis, mitigation, reporting, and communication.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7468`
- Context Precision: `0.8095`
- Context Recall: `1.0000`

---

### Question 5
**Question:** Explain the Recover function.

**AI Answer:** According to the provided documents, the **RECOVER (RC)** function is defined and structured as follows:

**Definition and Purpose**
According to the **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0** and several **Source: Unknown** documents, the RECOVER function ensures that assets and operations affected by a cybersecurity incident are restored. Its primary purpose is to support the timely restoration of normal operations to reduce the effects of incidents and enable appropriate communication during recovery efforts.

**Organizational Context**
The **Source: Unknown** documents describe RECOVER as one of the six CSF Functions. It is depicted as part of a wheel where all functions relate to one another; specifically, investments in the **GOVERN** and **IDENTIFY** functions support the execution of recovery actions in the **RECOVER** function.

**Categories and Subcategories**
Based on **NIST CSWP 29** and **Source: Unknown** context, the RECOVER function is divided into two primary categories:

*   **Incident Recovery Plan Execution (RC.RP):** This category focuses on restoration activities to ensure the operational availability of affected systems. Specific outcomes include:
    *   **RC.RP-01:** Executing the recovery portion of the incident response plan once initiated.
    *   **RC.RP-02:** Selecting, scoping, prioritizing, and performing recovery actions.
    *   **RC.RP-03:** Verifying the integrity of backups and restoration assets before use.
    *   **RC.RP-04:** Considering critical mission functions and cybersecurity risk management to establish post-incident operational norms.
    *   **RC.RP-05:** Verifying the integrity of restored assets and confirming normal operating status.
    *   **RC.RP-06:** Declaring the end of incident recovery based on established criteria and completing related documentation.

*   **Incident Recovery Communication (RC.CO):** This category involves coordinating restoration activities with internal and external parties. Specific outcomes include:
    *   **RC.CO-03:** Communicating recovery activities and progress to designated internal and external stakeholders.
    *   **RC.CO-04:** Sharing public updates on incident recovery using approved methods and messaging.

There are no conflicts regarding the RECOVER function across the provided documents.

**Ground Truth:** The Recover function identifies appropriate activities to maintain plans for resilience and to restore any capabilities or services that were impaired due to a cybersecurity incident.

**Scores:**
- Faithfulness: `N/A`
- Answer Relevancy: `0.8462`
- Context Precision: `0.8875`
- Context Recall: `1.0000`

---

### Question 6
**Question:** What is a Framework Profile?

**AI Answer:** According to **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, a CSF Organizational Profile is a mechanism for describing an organization’s current and/or target cybersecurity posture in terms of the CSF Core’s outcomes. These profiles are used to understand, tailor, assess, prioritize, and communicate the Core’s outcomes by considering an organization’s mission objectives, stakeholder expectations, threat landscape, and requirements.

The document specifies that every Organizational Profile includes one or both of the following:
*   **Current Profile:** Specifies the Core outcomes that an organization is currently achieving (or attempting to achieve) and characterizes the extent to which each outcome is being achieved.
*   **Target Profile:** Specifies the desired outcomes that an organization has selected and prioritized for achieving its cybersecurity risk management objectives, considering anticipated changes such as new technology, requirements, and threat trends.

Additionally, **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0** defines a **CSF Community Profile** as a baseline of CSF outcomes created and published to address shared interests and goals among a number of organizations, typically developed for a particular sector, subsector, technology, or threat type. An organization may use a Community Profile as the basis for its own Target Profile.

**Ground Truth:** A Framework Profile describes an organization's current or target cybersecurity posture in terms of the Core's outcomes, tailored to its mission, risk appetite, and resources.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7050`
- Context Precision: `0.7611`
- Context Recall: `1.0000`

---

### Question 7
**Question:** What are Framework Tiers?

**AI Answer:** According to **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, CSF Tiers are defined and characterized as follows:

**Definition and Purpose**
*   **Definition:** A Tier is a characterization of the rigor of an organization’s cybersecurity risk governance and management practices. 
*   **Function:** Tiers provide context for how an organization views cybersecurity risks and the processes in place to manage those risks. They reflect an organization’s practices for managing cybersecurity risk and describe a progression from informal, ad hoc responses to approaches that are agile, risk-informed, and continuously improving.
*   **Usage:** Tiers are used to inform an organization's Current and Target Profiles. They should complement, rather than replace, an organization’s existing cybersecurity risk management methodology. They can also be used as a benchmark for an organization-wide (enterprise) approach to managing risks.

**The Four Tiers**
The framework identifies four distinct Tiers:
1.  **Tier 1 (Partial):** Application of the cybersecurity risk strategy and prioritization are managed in an ad hoc manner. There is limited awareness of risks at the organizational level, and management occurs on an irregular, case-by-case basis.
2.  **Tier 2 (Risk Informed):** Risk assessment occurs but is not typically repeatable or reoccurring. Cybersecurity information is shared informally, and while the organization is aware of supplier risks, it does not act consistently or formally in response to them.
3.  **Tier 3 (Repeatable):** Risk management practices are formally approved and expressed as policy. Practices are regularly updated based on changes in business requirements, threats, and the technological landscape. Personnel formally act upon supplier risks through mechanisms like written agreements and monitoring.
4.  **Tier 4 (Adaptive):** There is an organization-wide approach to managing cybersecurity risks using risk-informed policies and procedures. The relationship between cybersecurity risks and organizational objectives is clearly understood and considered in decision-making.

**Progression**
According to the document, progression to higher Tiers is encouraged when risks or mandates are greater, or when a cost-benefit analysis indicates a feasible and cost-effective reduction of negative cybersecurity risks.

**Ground Truth:** Framework Tiers characterize the rigor of an organization's cybersecurity risk governance and management practices across four levels: Partial, Risk Informed, Repeatable, and Adaptive.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7459`
- Context Precision: `0.5889`
- Context Recall: `1.0000`

---

### Question 8
**Question:** What is the Identify function?

**AI Answer:** According to the **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, the IDENTIFY (ID) Function is defined as the process by which the organization’s current cybersecurity risks are understood. 

The document details the following regarding the IDENTIFY Function:

*   **Purpose:** Understanding the organization’s assets (such as data, hardware, software, systems, facilities, services, and people), suppliers, and related cybersecurity risks allows an organization to prioritize efforts consistent with its risk management strategy and mission needs identified under the GOVERN Function.
*   **Categories:** The IDENTIFY Function is divided into three primary Categories:
    *   **Asset Management (ID.AM):** Includes maintaining inventories of software, services, systems, and data; mapping network data flows; and prioritizing assets based on classification and criticality.
    *   **Risk Assessment (ID.RA):** Includes identifying and recording vulnerabilities, assessing the authenticity and integrity of hardware and software prior to acquisition, and assessing critical suppliers.
    *   **Improvement (ID.IM):** Focuses on identifying improvements to risk management processes from evaluations, security tests, and the execution of operational activities.
*   **Operational Role:** IDENTIFY outcomes help prevent and prepare for incidents. For example, an organization categorizes assets under IDENTIFY to take steps to secure them under the PROTECT Function. Additionally, investments in planning and testing within this Function support the timely detection of events and enable incident response and recovery actions.

**Ground Truth:** The Identify function involves developing an organizational understanding to manage cybersecurity risk to systems, assets, data, and capabilities.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7280`
- Context Precision: `1.0000`
- Context Recall: `1.0000`

---

### Question 9
**Question:** What is the Protect function?

**AI Answer:** According to NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0, the PROTECT (PR) function is defined as the use of safeguards to manage an organization’s cybersecurity risks. Once assets and risks are identified and prioritized, the PROTECT function supports the ability to secure those assets to prevent or lower the likelihood and impact of adverse cybersecurity events, as well as to increase the likelihood and impact of taking advantage of opportunities.

The outcomes covered by this Function include:
*   **Identity Management, Authentication, and Access Control (PR.AA):** Limiting access to physical and logical assets to authorized users, services, and hardware. Specific requirements include managing identities and credentials (PR.AA-01), proofing and binding identities to credentials (PR.AA-02), authenticating users, services, and hardware (PR.AA-03), and protecting/verifying identity assertions (PR.AA-04).
*   **Awareness and Training (PR.AT)**
*   **Data Security (PR.DS)**
*   **Platform Security (PR.PS):** Securing the hardware, software, and services of physical and virtual platforms.
*   **Technology Infrastructure Resilience (PR.IR)**

**Ground Truth:** The Protect function focuses on implementing appropriate safeguards to ensure the delivery of critical infrastructure services and to limit or contain the impact of a potential cybersecurity event.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.7343`
- Context Precision: `0.7222`
- Context Recall: `0.0000`

---

### Question 10
**Question:** Who is the intended audience for the NIST Framework?

**AI Answer:** According to **NIST CSWP 29 The NIST Cybersecurity Framework (CSF) 2.0**, the intended audience is defined as follows:

*   **Primary Audience:** Individuals responsible for developing and leading cybersecurity programs.
*   **Risk Management Professionals:** The framework can be used by others involved in managing risk, including executives, boards of directors, acquisition professionals, technology professionals, risk managers, lawyers, human resources specialists, and cybersecurity and risk management auditors.
*   **Policy Makers:** It is useful to those making and influencing policy, such as associations, professional organizations, and regulators who set and communicate priorities for cybersecurity risk management.
*   **Organizations:** The CSF is designed for organizations of all sizes and sectors, including industry, government, academia, and nonprofit organizations, regardless of their cybersecurity program's maturity level or technical sophistication.
*   **General Expertise:** The framework describes outcomes intended to be understood by a broad audience—including executives, managers, and practitioners—regardless of their specific cybersecurity expertise.

**Ground Truth:** The Framework is designed to be used by organizations of all sizes and sectors to manage cybersecurity risk, ranging from executive leadership to practitioners.

**Scores:**
- Faithfulness: `1.0000`
- Answer Relevancy: `0.8235`
- Context Precision: `0.7857`
- Context Recall: `1.0000`

---

