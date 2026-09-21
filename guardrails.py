import re
from typing import NamedTuple, List, Dict

class GuardrailResult(NamedTuple):
    is_safe: bool
    sanitized_prompt: str
    injection_detected: bool
    pii_redacted_count: int
    violations: List[str]
    vault: Dict[str, str]

class GuardrailService:
    """
    GuardrailService handles AI Application Security & Privacy:
    1. Prompt Injection Detection (OWASP LLM01)
    2. Context-Preserving PII Pseudonymization & Re-Identification Vault (OWASP LLM06)
    3. Policy & Content Safeguards
    """

    # Patterns commonly used in Prompt Injections / Jailbreaks
    INJECTION_PATTERNS = [
        r"ignore\s+.*?(instructions|rules|prompts|system)",
        r"disregard\s+.*?(instructions|rules|prompts|system)",
        r"forget\s+.*?(instructions|rules|prompts|system)",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"override\s+.*?(rules|settings|safety|security)",
        r"system\s+prompt",
        r"jailbreak",
        r"dan\s+mode",
    ]

    # Regex patterns for identifying sensitive user PII
    PII_PATTERNS = {
        "EMAIL": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "PHONE": r"(?:\+?\b|\+)\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    }

    def process_prompt(self, prompt: str) -> GuardrailResult:
        """
        Inspects prompt for injections and pseudonymizes PII using indexed placeholders.
        Returns GuardrailResult with a vault map for post-processing rehydration.
        """
        violations = []
        is_injection = False
        pii_count = 0
        cleaned_text = prompt
        vault: Dict[str, str] = {}

        # 1. Check for Prompt Injections
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                is_injection = True
                violations.append(f"Prompt Injection pattern matched: '{pattern}'")
                break

        if is_injection:
            return GuardrailResult(
                is_safe=False,
                sanitized_prompt=prompt,
                injection_detected=True,
                pii_redacted_count=0,
                violations=violations,
                vault={}
            )

        # 2. Pseudonymize PII with indexed placeholders (e.g. [EMAIL_1], [PHONE_1])
        for pii_type, pattern in self.PII_PATTERNS.items():
            counter = 1
            matches = list(re.finditer(pattern, cleaned_text))

            processed_values = set()
            for match in matches:
                original_value = match.group(0)
                if original_value in processed_values:
                    continue

                processed_values.add(original_value)
                placeholder = f"[{pii_type}_{counter}]"

                vault[placeholder] = original_value
                cleaned_text = cleaned_text.replace(original_value, placeholder)
                pii_count += 1
                counter += 1

        return GuardrailResult(
            is_safe=True,
            sanitized_prompt=cleaned_text,
            injection_detected=False,
            pii_redacted_count=pii_count,
            violations=[],
            vault=vault
        )

    def rehydrate(self, llm_response: str, vault: Dict[str, str]) -> str:
        """
        Re-identifies the LLM's response by replacing pseudonym placeholders
        with their original values stored in the privacy vault.
        Uses flexible regex matching to handle LLM formatting quirks (e.g., [EMAIL 1] vs [EMAIL_1]).
        """
        rehydrated_text = llm_response
        for placeholder, original_value in vault.items():
            # Parse placeholder into type and index (e.g. "[EMAIL_1]" -> "EMAIL", "1")
            match = re.match(r"\[([A-Z_]+)_(\d+)\]", placeholder)
            if match:
                pii_type, index = match.groups()
                # Flexible pattern matching variations like [EMAIL_1], [EMAIL 1], [EMAIL-1], [email 1]
                flexible_pattern = rf"\[\s*{re.escape(pii_type)}[\s_:-]*{index}\s*\]"
                rehydrated_text = re.sub(flexible_pattern, original_value, rehydrated_text, flags=re.IGNORECASE)
            else:
                # Fallback to exact string replacement
                rehydrated_text = rehydrated_text.replace(placeholder, original_value)

        return rehydrated_text
