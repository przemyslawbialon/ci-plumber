#!/usr/bin/env python3


class CIStatus:
    LINTER_FAILED = "linter_failed"
    CHROMATIC_FAILED = "chromatic_failed"

    LINTER_KEYWORDS = ["lint", "eslint"]
    CHROMATIC_KEYWORDS = ["chromatic"]

    @staticmethod
    def is_linter_check(name):
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in CIStatus.LINTER_KEYWORDS)

    @staticmethod
    def is_chromatic_check(name):
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in CIStatus.CHROMATIC_KEYWORDS)
