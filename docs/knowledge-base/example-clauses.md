# Example Contract Clauses — Compliant and Non-Compliant

This document provides example contract and privacy policy clauses with assessments.
These examples are typical of real-world SaaS agreements, data processing addendums,
and privacy notices. Use this as a reference corpus for compliance analysis.

---

## Category 1: Data Retention

### NON-COMPLIANT — Indefinite Retention

**Clause**: "We retain all user data for as long as necessary to provide our services."

**Assessment**: NON-COMPLIANT. "As long as necessary" is not a defined period. Article 5(1)(e)
(storage limitation) requires that personal data is kept in a form that permits identification
no longer than necessary for the purposes for which it is processed. This vague clause does not
satisfy that requirement.

**Specific violation**: Article 5(1)(e) — Storage Limitation.

---

### NON-COMPLIANT — Explicit Indefinite Retention

**Clause**: "User data including names, email addresses, IP addresses, and usage logs are
retained indefinitely in our systems."

**Assessment**: NON-COMPLIANT. "Indefinitely" is an explicit statement of non-compliance with
Article 5(1)(e). There is no purpose that justifies keeping personal data forever.

**Specific violation**: Article 5(1)(e) — Storage Limitation.

---

### COMPLIANT — Defined Retention Periods

**Clause**: "We retain your account information for 3 years from the date of your last login.
Usage logs, including IP addresses, are automatically deleted after 90 days. Payment records
are retained for 7 years to comply with our statutory tax obligations under applicable law and
are deleted thereafter."

**Assessment**: COMPLIANT. Specific retention periods are stated for each data category.
Different data has different periods based on the legitimate purpose. Third-party legal
obligations are cited where applicable.

---

## Category 2: Lawful Basis

### NON-COMPLIANT — No Lawful Basis Stated

**Clause**: "We collect and process your personal data to improve our services."

**Assessment**: NON-COMPLIANT. "To improve our services" is a purpose, not a lawful basis.
Article 6 requires one of six specific lawful bases (consent, contract, legal obligation,
vital interests, public task, legitimate interests). None is identified here.

**Specific violation**: Article 6(1) — no lawful basis identified.

---

### NON-COMPLIANT — Legitimate Interests Without Balancing

**Clause**: "We process your personal data based on our legitimate interests in operating
and improving our platform."

**Assessment**: NON-COMPLIANT. While legitimate interests (Article 6(1)(f)) is a valid basis,
it requires a documented balancing test showing the controller's interests outweigh the
data subject's rights. Merely citing it without any balancing assessment is insufficient.
Also, "improving our platform" is typically not a sufficiently pressing legitimate interest
to override the data subject's right to privacy.

---

### COMPLIANT — Specific Lawful Bases

**Clause**: "We process your personal data on the following lawful bases:
(a) Email address and name: Article 6(1)(b) (contract) — necessary to create and manage your account.
(b) Payment information: Article 6(1)(c) (legal obligation) — required by applicable VAT and
anti-money laundering regulations.
(c) Usage analytics: Article 6(1)(a) (consent) — only if you have opted into analytics tracking.
You may withdraw this consent at any time in your account settings."

**Assessment**: COMPLIANT. Each data type has a clearly stated, specific lawful basis.
Different bases are used for different purposes. Consent-based processing includes a withdrawal mechanism.

---

## Category 3: Consent

### NON-COMPLIANT — Bundled Consent

**Clause**: "By creating an account and accepting these Terms of Service, you consent to the
collection and processing of all personal data described in our Privacy Policy."

**Assessment**: NON-COMPLIANT. Bundling consent with acceptance of terms of service is explicitly
addressed in Article 7(2): requests for consent must be clearly distinguishable from other matters.
Forced consent (no account without consent) violates the "freely given" requirement of Article 4(11).

**Specific violation**: Article 4(11), Article 7(2) — consent not freely given or distinguishable.

---

### NON-COMPLIANT — No Withdrawal Mechanism

**Clause**: "You consent to us using your email address for marketing communications."

**Assessment**: NON-COMPLIANT. While consent is stated, Article 7(3) requires that the data
subject can withdraw consent at any time and that withdrawal must be as easy as giving consent.
This clause provides no mechanism for withdrawal.

---

### COMPLIANT — Valid Consent

**Clause**: "We would like to send you product updates and special offers by email.
[ ] Yes, I'd like to receive marketing emails. (optional — not required to use the service)

You can withdraw this consent at any time by clicking 'Unsubscribe' in any email or by
visiting your account preferences at Settings > Notifications > Unsubscribe."

**Assessment**: COMPLIANT. Consent is explicitly optional (not bundled with service access),
given by an affirmative action (checkbox, not pre-ticked), specific to marketing emails,
and a clear, easy withdrawal mechanism is provided.

---

## Category 4: IP Address Collection

### NON-COMPLIANT — Undisclosed Collection

**Clause**: "We collect your name, email address, and device type when you register."
[System simultaneously logs all user IP addresses to an analytics database with no retention policy]

**Assessment**: NON-COMPLIANT. IP addresses are personal data (Recital 30, Article 4(1)).
Collecting them without disclosing it in the privacy notice violates Article 5(1)(a)
(transparency) and Articles 13/14 (information obligations).

---

### NON-COMPLIANT — Unspecified Purpose

**Clause**: "We log your IP address."

**Assessment**: NON-COMPLIANT. No purpose is given (violates Article 5(1)(b)), no lawful basis
is stated (violates Article 6), and no retention period is provided (violates Article 5(1)(e)).

---

### COMPLIANT — Full Disclosure

**Clause**: "We record your IP address when you access our service. We do this on the lawful
basis of legitimate interests (Article 6(1)(f)) for the purposes of detecting and preventing
fraud, abuse, and security attacks. IP address logs are retained for 60 days and then
automatically deleted. IP addresses are not shared with third parties except where required
by law or to report detected attacks to our hosting provider's security team."

**Assessment**: COMPLIANT. Purpose is specific, lawful basis is identified, retention period is
defined, recipients are named, and the legitimate interests basis includes an implicit proportionality
assessment (fraud/security is a well-established legitimate interest).

---

## Category 5: Security and Encryption

### NON-COMPLIANT — No Security Measures

**Clause**: "We take reasonable steps to protect your personal data."

**Assessment**: NON-COMPLIANT. Article 32 requires specific, appropriate technical and
organisational measures to be in place. "Reasonable steps" with no specifics is insufficient
for a data processing agreement.

---

### COMPLIANT — Specific Security Measures

**Clause**: "We implement the following security measures for personal data:
(a) All data in transit is encrypted using TLS 1.2 or higher.
(b) Personal data at rest is encrypted using AES-256.
(c) Access to personal data is limited to authorised personnel only and is logged.
(d) We conduct annual penetration testing and quarterly access reviews.
(e) We maintain a documented incident response plan and will notify affected users and
    the relevant supervisory authority within 72 hours of becoming aware of a data breach."

**Assessment**: COMPLIANT. Specific, verifiable technical measures are listed. The 72-hour
breach notification commitment satisfies Article 33.

---

## Category 6: Data Subject Rights

### NON-COMPLIANT — Rights Not Acknowledged

**Clause**: "Once we collect your data, it is non-refundable and cannot be deleted."

**Assessment**: NON-COMPLIANT. This directly contradicts the right to erasure (Article 17),
the right to rectification (Article 16), and the right of access (Article 15). No contract
can waive statutory rights granted by GDPR.

---

### COMPLIANT — Rights Statement

**Clause**: "You have the following rights regarding your personal data:
Right of access (Article 15): You may request a copy of the personal data we hold about you.
Right to rectification (Article 16): You may request correction of inaccurate data.
Right to erasure (Article 17): You may request deletion of your data where it is no longer needed.
Right to restriction (Article 18): You may request we limit processing of your data.
Right to data portability (Article 20): You may request your data in a machine-readable format.
Right to object (Article 21): You may object to processing based on legitimate interests.

To exercise any of these rights, contact our Data Protection Officer at dpo@example.com.
We will respond within 30 days. You may also lodge a complaint with your national supervisory authority."

**Assessment**: COMPLIANT. All required rights are listed, a contact method is provided, a
response timeframe (within the Article 12 one-month requirement) is stated, and the right to
complain to a supervisory authority is acknowledged.
