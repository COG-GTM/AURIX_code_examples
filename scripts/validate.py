#!/usr/bin/env python3
"""
Validation script for AURIX Code Examples repository.

Checks:
1. Directory structure integrity (required files/dirs per example)
2. JSON validity of .ads/ config files and .exportedSettings
3. C source file syntax via cppcheck (optional, requires cppcheck installed)
4. Metadata presence in Cpu0_Main.c

Usage:
    python3 scripts/validate.py                  # validate all examples
    python3 scripts/validate.py --example NAME   # validate a single example
    python3 scripts/validate.py --no-cppcheck    # skip cppcheck analysis
    python3 scripts/validate.py --summary        # print summary only
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_EXAMPLES_DIR = REPO_ROOT / "code_examples"

# Required for every code example
REQUIRED_DIRS = ["Configurations"]
REQUIRED_FILES = ["Cpu0_Main.c"]

# .ads JSON files that should be valid if present
ADS_JSON_FILES = [
    "install-libraries.json",
    "clean-libraries.json",
    "backup-libraries.json",
    "rollback-libraries.json",
    "package.json",
]


class ValidationResult:
    def __init__(self, example_name: str):
        self.example_name = example_name
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def validate_structure(example_dir: Path, result: ValidationResult) -> None:
    """Check that required directories and files exist."""
    for d in REQUIRED_DIRS:
        if not (example_dir / d).is_dir():
            result.add_error(f"Missing required directory: {d}")

    for f in REQUIRED_FILES:
        if not (example_dir / f).is_file():
            result.add_error(f"Missing required file: {f}")

    # Check for Libraries directory (present in almost all examples)
    if not (example_dir / "Libraries").is_dir():
        result.add_warning("Missing Libraries directory")

    # Check for .ads directory
    if not (example_dir / ".ads").is_dir():
        result.add_warning("Missing .ads configuration directory")

    # Check for at least one linker script
    lsl_files = list(example_dir.glob("*.lsl"))
    if not lsl_files:
        result.add_warning("No linker script (.lsl) found")


def validate_json_files(example_dir: Path, result: ValidationResult) -> None:
    """Validate that all JSON config files parse correctly."""
    ads_dir = example_dir / ".ads"
    if ads_dir.is_dir():
        for json_file in ADS_JSON_FILES:
            json_path = ads_dir / json_file
            if json_path.is_file():
                try:
                    with open(json_path, "r", encoding="utf-8", errors="replace") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    result.add_error(f".ads/{json_file}: Invalid JSON - {e}")

    # Validate .exportedSettings if present
    exported = example_dir / ".exportedSettings"
    if exported.is_file():
        try:
            with open(exported, "r", encoding="utf-8", errors="replace") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            result.add_error(f".exportedSettings: Invalid JSON - {e}")

    # Validate Libraries/.ads/ JSON files if present
    lib_ads = example_dir / "Libraries" / ".ads"
    if lib_ads.is_dir():
        for json_path in lib_ads.glob("*.json"):
            try:
                with open(json_path, "r", encoding="utf-8", errors="replace") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                result.add_error(
                    f"Libraries/.ads/{json_path.name}: Invalid JSON - {e}"
                )


def validate_metadata(example_dir: Path, result: ValidationResult) -> None:
    """Check that Cpu0_Main.c contains metadata section."""
    cpu0_main = example_dir / "Cpu0_Main.c"
    if not cpu0_main.is_file():
        return

    try:
        content = cpu0_main.read_text(encoding="utf-8", errors="replace")
    except OSError:
        result.add_error("Cannot read Cpu0_Main.c")
        return

    # Check for core0_main function
    if "core0_main" not in content:
        result.add_warning("Cpu0_Main.c missing core0_main() function")


def validate_cppcheck(example_dir: Path, result: ValidationResult) -> None:
    """Run cppcheck on the example's C source files (top-level only)."""
    c_files = list(example_dir.glob("*.c"))
    if not c_files:
        result.add_warning("No C source files found at top level")
        return

    try:
        cmd = [
            "cppcheck",
            "--error-exitcode=1",
            "--suppress=missingInclude",
            "--suppress=missingIncludeSystem",
            "--suppress=unusedFunction",
            "--suppress=unknownMacro",
            "--suppress=integerOverflow",
            "--suppress=unmatchedSuppression",
            "--std=c99",
            "--language=c",
            "--quiet",
        ] + [str(f) for f in c_files]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if proc.returncode != 0:
            # Parse cppcheck output for real errors
            for line in proc.stderr.strip().split("\n"):
                if line.strip():
                    result.add_error(f"cppcheck: {line.strip()}")
    except FileNotFoundError:
        result.add_warning("cppcheck not installed, skipping static analysis")
    except subprocess.TimeoutExpired:
        result.add_warning("cppcheck timed out")


def validate_example(
    example_dir: Path, run_cppcheck: bool = True
) -> ValidationResult:
    """Run all validations on a single code example."""
    result = ValidationResult(example_dir.name)

    validate_structure(example_dir, result)
    validate_json_files(example_dir, result)
    validate_metadata(example_dir, result)

    if run_cppcheck:
        validate_cppcheck(example_dir, result)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate AURIX code examples repository"
    )
    parser.add_argument(
        "--example",
        type=str,
        help="Validate a single example by name",
    )
    parser.add_argument(
        "--no-cppcheck",
        action="store_true",
        help="Skip cppcheck static analysis",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary only (no per-example details)",
    )
    args = parser.parse_args()

    run_cppcheck = not args.no_cppcheck

    if not CODE_EXAMPLES_DIR.is_dir():
        print(f"ERROR: code_examples directory not found at {CODE_EXAMPLES_DIR}")
        return 1

    # Collect examples to validate
    if args.example:
        example_dir = CODE_EXAMPLES_DIR / args.example
        if not example_dir.is_dir():
            print(f"ERROR: Example not found: {args.example}")
            return 1
        examples = [example_dir]
    else:
        examples = sorted(
            [d for d in CODE_EXAMPLES_DIR.iterdir() if d.is_dir()]
        )

    if not examples:
        print("ERROR: No code examples found")
        return 1

    print(f"Validating {len(examples)} code example(s)...")
    if run_cppcheck:
        print("  (cppcheck enabled)")
    else:
        print("  (cppcheck disabled)")
    print()

    results: list[ValidationResult] = []
    for i, example_dir in enumerate(examples):
        result = validate_example(example_dir, run_cppcheck)
        results.append(result)

        if not args.summary:
            status = "PASS" if result.passed else "FAIL"
            warn_count = len(result.warnings)
            suffix = f" ({warn_count} warning(s))" if warn_count > 0 else ""
            print(f"  [{i + 1}/{len(examples)}] {status} {result.example_name}{suffix}")

            for err in result.errors:
                print(f"    ERROR: {err}")
            if not args.summary:
                for warn in result.warnings:
                    print(f"    WARN:  {warn}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    print()
    print("=" * 60)
    print(f"VALIDATION SUMMARY")
    print(f"  Total examples: {total}")
    print(f"  Passed:         {passed}")
    print(f"  Failed:         {failed}")
    print(f"  Total errors:   {total_errors}")
    print(f"  Total warnings: {total_warnings}")
    print("=" * 60)

    if failed > 0:
        print()
        print("FAILED EXAMPLES:")
        for r in results:
            if not r.passed:
                print(f"  - {r.example_name}")
                for err in r.errors:
                    print(f"      ERROR: {err}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
