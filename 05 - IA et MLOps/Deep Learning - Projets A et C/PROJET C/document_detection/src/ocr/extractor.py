"""Field extraction from OCR text."""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentType:
    name: str
    keywords: List[str]
    fields: Dict[str, str]
    patterns: Dict[str, re.Pattern]


class FieldExtractor:
    """Extract structured fields from OCR text."""

    # Document type definitions with improved patterns
    DOCUMENT_TYPES = {
        "id_card": DocumentType(
            name="Carte d'identité",
            keywords=[
                "carte d'identité",
                "carte identite",
                "identity card",
                "id card",
                "cni",
                "cin",
                "national identity",
                "république française",
                "republique francaise",
                "identité nationale",
                "identite nationale",
            ],
            fields={
                "nom": "Nom",
                "prenom": "Prénom",
                "date_naissance": "Date de naissance",
                "lieu_naissance": "Lieu de naissance",
                "numero": "Numéro",
                "nationalite": "Nationalité",
                "sexe": "Sexe",
            },
            patterns={
                "nom": re.compile(
                    r"(?:Nom|Surname|NOM)[\s:]*([A-Z][A-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "prenom": re.compile(
                    r"(?:Prénom|Prenom|Given names|Pr?nom)[\s:]*([A-Z][a-zA-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "date_naissance": re.compile(
                    r"(?:Né\s+le|Née\s+le|Date\s+de\s+naissance|Birth)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "lieu_naissance": re.compile(
                    r"(?:à|Lieu\s+de\s+naissance|Place\s+of\s+birth)[\s:]*([A-Za-z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)(?:\n|$)",
                    re.IGNORECASE,
                ),
                "numero": re.compile(
                    r"(?:ID|Numéro|N°|No)[\s:]*([A-Z0-9]{5,20})", re.IGNORECASE
                ),
                "nationalite": re.compile(
                    r"(?:Nationalité|Nationality)[\s:]*([A-Za-z\s]+)", re.IGNORECASE
                ),
                "sexe": re.compile(r"(?:Sexe|Sex)[\s:]*([MF])", re.IGNORECASE),
            },
        ),
        "driver_license": DocumentType(
            name="Permis de conduire",
            keywords=[
                "permis",
                "conduire",
                "driving license",
                "driver license",
                "permis de conduire",
                "driving permit",
            ],
            fields={
                "nom": "Nom",
                "prenom": "Prénom",
                "date_naissance": "Date de naissance",
                "numero": "Numéro",
                "categorie": "Catégorie",
                "date_delivrance": "Date de délivrance",
                "date_expiration": "Date d'expiration",
            },
            patterns={
                "nom": re.compile(
                    r"(?:Nom|Surname|NOM)[\s:]*([A-Z][A-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "prenom": re.compile(
                    r"(?:Prénom|Prenom)[\s:]*([A-Z][a-zA-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "date_naissance": re.compile(
                    r"(?:Né\s+le|Date\s+de\s+naissance)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "numero": re.compile(
                    r"(?:N°|No|Numéro)[\s:]*([A-Z0-9]{5,20})", re.IGNORECASE
                ),
                "categorie": re.compile(
                    r"(?:Catégorie|Cat\.?|Category)[\s:]*([A-Z][,\sA-Z]*)",
                    re.IGNORECASE,
                ),
                "date_delivrance": re.compile(
                    r"(?:Délivré|Delivre|Issued)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "date_expiration": re.compile(
                    r"(?:Expire|Valid\s+until|Validité)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
            },
        ),
        "residence_permit": DocumentType(
            name="Titre de séjour",
            keywords=[
                "titre de séjour",
                "titre sejour",
                "residence permit",
                "permesso di soggiorno",
                "residence card",
                "carte de séjour",
            ],
            fields={
                "nom": "Nom",
                "prenom": "Prénom",
                "date_naissance": "Date de naissance",
                "nationalite": "Nationalité",
                "numero": "Numéro",
                "date_expiration": "Date d'expiration",
            },
            patterns={
                "nom": re.compile(
                    r"(?:Nom|Surname)[\s:]*([A-Z][A-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)", re.IGNORECASE
                ),
                "prenom": re.compile(
                    r"(?:Prénom|Prenom)[\s:]*([A-Z][a-zA-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "date_naissance": re.compile(
                    r"(?:Né\s+le|Date\s+de\s+naissance)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "nationalite": re.compile(
                    r"(?:Nationalité|Nationality)[\s:]*([A-Za-z\s]+)", re.IGNORECASE
                ),
                "numero": re.compile(
                    r"(?:N°|No|Numéro)[\s:]*([A-Z0-9]{5,20})", re.IGNORECASE
                ),
                "date_expiration": re.compile(
                    r"(?:Expire|Valid\s+until)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
            },
        ),
        "passport": DocumentType(
            name="Passeport",
            keywords=[
                "passeport",
                "passport",
                "travel document",
                "passeport français",
                "french passport",
            ],
            fields={
                "nom": "Nom",
                "prenom": "Prénom",
                "date_naissance": "Date de naissance",
                "nationalite": "Nationalité",
                "numero": "Numéro",
                "date_expiration": "Date d'expiration",
                "lieu_delivrance": "Lieu de délivrance",
            },
            patterns={
                "nom": re.compile(
                    r"(?:Surname|Nom)[\s:]*([A-Z][A-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)", re.IGNORECASE
                ),
                "prenom": re.compile(
                    r"(?:Given names|Prénoms|Prénom)[\s:]*([A-Z][A-Z\s\-'ÉÈÎÔÂÙËÏÜŸ]+)",
                    re.IGNORECASE,
                ),
                "date_naissance": re.compile(
                    r"(?:Date\s+of\s+birth|Date\s+de\s+naissance)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "nationalite": re.compile(
                    r"(?:Nationality|Nationalité)[\s:]*([A-Za-z\s]+)", re.IGNORECASE
                ),
                "numero": re.compile(
                    r"(?:Passport\s+No|Passeport\s+N°)[\s\.]*([A-Z0-9]{5,15})",
                    re.IGNORECASE,
                ),
                "date_expiration": re.compile(
                    r"(?:Date\s+of\s+expiry|Expire)[\s:]*(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})",
                    re.IGNORECASE,
                ),
                "lieu_delivrance": re.compile(
                    r"(?:Authority|Lieu)[\s:]*([A-Za-z\s]+)", re.IGNORECASE
                ),
            },
        ),
    }

    def __init__(self):
        self.fallback_patterns = {
            "date": re.compile(r"\b(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})\b"),
            "mrz": re.compile(r"[A-Z<]{2}[A-Z<]{3}[A-Z<]{30,}<<"),
            "numeric": re.compile(r"\b\d{5,20}\b"),
        }

    def detect_document_type(self, text: str) -> Tuple[str, float]:
        """
        Detect document type from text.

        Returns:
            Tuple of (doc_type, confidence)
        """
        if not text:
            return "unknown", 0.0

        text_lower = text.lower()
        scores = {}

        for doc_type, config in self.DOCUMENT_TYPES.items():
            score = 0
            for keyword in config.keywords:
                if keyword in text_lower:
                    score += 1
                    # Bonus for multiple word matches
                    if len(keyword.split()) > 1:
                        score += 1

            # Normalize by number of keywords
            scores[doc_type] = score / max(len(config.keywords) / 3, 1)

        if not scores:
            return "unknown", 0.0

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Threshold
        if best_score < 0.3:
            return "unknown", best_score

        return best_type, min(best_score, 1.0)

    def extract_fields(self, text: str, doc_type: str) -> Dict[str, str]:
        """
        Extract fields from text based on document type.

        Args:
            text: Raw OCR text
            doc_type: Detected document type

        Returns:
            Dictionary of extracted fields
        """
        if doc_type == "unknown" or doc_type not in self.DOCUMENT_TYPES:
            return self._extract_generic(text)

        config = self.DOCUMENT_TYPES[doc_type]
        fields = {}

        # Apply specific patterns
        for field_name, pattern in config.patterns.items():
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                # Clean up
                value = re.sub(r"\s+", " ", value)
                if value:
                    fields[field_name] = value

        # Fallback: extract any dates if not found
        if not fields.get("date_naissance"):
            dates = self._extract_dates(text)
            if dates:
                fields["date_naissance"] = dates[0]

        # Validate dates
        fields = self._validate_dates(fields)

        return fields

    def _extract_generic(self, text: str) -> Dict[str, str]:
        """Extract generic fields when document type unknown."""
        fields = {}

        # Look for key:value patterns
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()[:30]
                    value = parts[1].strip()[:50]
                    if value and len(value) > 2:
                        fields[key.lower().replace(" ", "_")] = value

        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            fields["dates_trouvees"] = ", ".join(dates[:3])

        return fields

    def _extract_dates(self, text: str) -> List[str]:
        """Extract all dates from text."""
        matches = self.fallback_patterns["date"].findall(text)
        return matches

    def _validate_dates(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Validate and normalize dates."""
        date_fields = ["date_naissance", "date_delivrance", "date_expiration"]

        for field in date_fields:
            if field in fields:
                date_str = fields[field]
                # Normalize separators
                normalized = date_str.replace("-", "/").replace(".", "/")

                try:
                    # Validate format
                    date_obj = datetime.strptime(normalized, "%d/%m/%Y")
                    fields[field] = normalized

                    # Check if date makes sense
                    now = datetime.now()
                    if field == "date_naissance":
                        # Must be in the past, reasonable age
                        if date_obj > now or (now - date_obj).days > 365 * 120:
                            del fields[field]  # Remove invalid
                    elif field == "date_expiration":
                        # Reasonable expiry (not too far in future)
                        if (date_obj - now).days > 365 * 20:
                            del fields[field]

                except ValueError:
                    pass  # Keep original if parsing fails

        return fields

    def get_document_info(self, doc_type: str) -> Optional[DocumentType]:
        """Get document type configuration."""
        return self.DOCUMENT_TYPES.get(doc_type)
