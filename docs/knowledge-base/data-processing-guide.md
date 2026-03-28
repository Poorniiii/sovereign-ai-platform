# Data Processing Compliance Guide — Plain English

This guide translates key GDPR obligations into practical compliance requirements.
Use it to assess whether a contract, privacy policy, or system design meets GDPR standards.

---

## 1. Lawful Basis — You MUST have one before collecting data

Before collecting any personal data you must identify your lawful basis (Article 6). The most
common bases for commercial platforms are:

| Basis | When it applies | Example |
|---|---|---|
| Consent | User actively opts in | Newsletter sign-up, analytics tracking |
| Contract | Data needed to deliver the service | Email address to create an account |
| Legal obligation | Law requires you to collect it | Tax records, fraud reporting |
| Legitimate interests | Your interest outweighs user's | Fraud detection, network security |

**Red flags (non-compliant)**:
- Vague statements like "we may use your data to improve our services" without a specific lawful basis
- Claiming legitimate interests for marketing without a balancing test
- Processing data before obtaining consent when consent is the only valid basis
- Using consent as a lawful basis but not providing a way to withdraw it

**Compliant wording example**:
"We process your email address on the legal basis of contract performance (Article 6(1)(b)) as it
is necessary to send you the service you have requested. We will not use your email for marketing
without your separate consent."

---

## 2. Retention Periods — Data must not be kept indefinitely

Article 5(1)(e) (storage limitation) requires that personal data is not kept longer than necessary.

**Non-compliant examples**:
- "We retain user data indefinitely."
- "Data is deleted when you close your account" — but account closure process is unclear
- No stated retention period at all

**Compliant examples**:
- "We retain account data for 3 years after your last login, then delete it securely."
- "Transaction records are retained for 7 years to comply with tax law, then deleted."
- "Log files containing IP addresses are deleted after 90 days."

**Assessment rule**: Any contract or policy that does not specify a retention period, or uses
the word "indefinitely", fails Article 5(1)(e).

---

## 3. IP Addresses and Online Identifiers

Per Recital 30 and Article 4(1), IP addresses are personal data when the controller can
reasonably combine them with other data to identify a person (e.g. account records, timestamps).

**Common violations**:
- Logging all user IP addresses in analytics or application logs without a retention policy
- Storing IP addresses "for analytics" without a lawful basis
- Sharing IP address logs with third parties without informing users
- Retaining IP address logs indefinitely

**Compliant approach**:
- State the lawful basis for collecting IPs (e.g. legitimate interests for security/fraud prevention)
- Define a retention period (typically 30-90 days for security logs)
- Include IP addresses in the privacy notice
- Use anonymisation (e.g. zeroing the last octet) if identification is not required

---

## 4. Consent Requirements

Consent (Article 4(11), Article 7) must be:

**Freely given**: The user must be able to refuse without suffering consequences. Bundling consent
with terms of service ("by using this service you consent to all data processing") is not valid.

**Specific**: Consent must be obtained separately for each purpose. One checkbox for "I agree to
all data processing" is not specific enough.

**Informed**: The user must know what they are consenting to, who processes the data, and for
how long before giving consent.

**Unambiguous**: Pre-ticked checkboxes are not valid consent. Silence is not consent.
Consent must be a clear affirmative action.

**Withdrawable**: The user must be able to withdraw consent as easily as they gave it.

**Red flags**:
- "By continuing to use our service, you agree to our data processing."
- Pre-ticked consent boxes
- No mechanism to withdraw consent
- Consent bundled with acceptance of terms

---

## 5. Data Minimisation

Article 5(1)(c) requires that you collect only the data that is necessary for the stated purpose.

**Violations**:
- Collecting date of birth when only age verification is needed
- Requiring a phone number to sign up for a text-only service
- Storing full credit card numbers when a payment processor handles payments
- Logging detailed user behaviour for all users when only aggregate stats are needed

**Assessment rule**: For each data field collected, ask "is this strictly necessary for the
stated purpose?" If the answer is no or maybe, it likely violates data minimisation.

---

## 6. Security Requirements (Article 32)

Technical and organisational measures must be appropriate to the risk. At minimum:

- Personal data must be encrypted in transit (TLS) and at rest
- Access to personal data must be access-controlled (only those who need it)
- Regular security testing must take place
- A data breach response plan must exist

**Red flags**:
- Storing passwords in plaintext
- Transmitting personal data over HTTP (unencrypted)
- No access controls on personal data stores
- No stated security measures in a data processing agreement

---

## 7. Right to Erasure — Contracts Must Address It

Any contract governing data processing must acknowledge the right to erasure (Article 17).

**Compliant contract language**:
"Upon written request from the data subject, we will erase all personal data relating to that
individual within 30 days, except where retention is required by applicable law."

**Non-compliant**:
- No mention of erasure rights
- 'We will delete your data when you close your account' without specifying a timeline
- Claiming all data is retained for 'legal purposes' without specifying which law requires it

---

## 8. Children's Data (Article 8)

Where services are directed at children (under 16 in most EU member states), parental consent
is required. General consent mechanisms designed for adults are not sufficient.

Signs of non-compliance:
- A platform targeted at minors with no age verification
- Using the same consent mechanism for adults and children
- No mention of how children's data is handled in the privacy policy

---

## 9. International Data Transfers

Transferring personal data outside the EU/EEA requires one of:
- An adequacy decision (the destination country has equivalent protection)
- Standard Contractual Clauses (SCCs) approved by the European Commission
- Binding Corporate Rules (BCRs) for intragroup transfers
- The user's explicit consent for the specific transfer

**Red flags**:
- "We may transfer your data to our US servers" with no SCCs or adequacy basis mentioned
- No mention of international transfers in the privacy policy when the service uses US-based cloud providers

---

## 10. Quick Compliance Checklist

For any privacy policy or data processing contract, verify:

- [ ] Lawful basis for each type of processing is stated
- [ ] Retention periods are defined for all data categories
- [ ] Purpose of processing is specific and cannot be repurposed without new consent
- [ ] Consent is freely given, specific, informed, and withdrawable
- [ ] Data subjects are informed of their rights (access, rectification, erasure, portability)
- [ ] Security measures are described
- [ ] International transfers are addressed with appropriate safeguards
- [ ] Contact details for the DPA (Data Protection Authority) are provided
- [ ] Children's data handling is addressed if applicable
