#!/bin/bash

# Guyue Digital Twin - Comprehensive Test Suite
# Runs all health probes, CI validators, and internal audits.

set -e

echo "=========================================="
echo "🚀 Starting Guyue Universal Test Suite..."
echo "=========================================="

echo "[0/6] Running Zero-Leakage Security Scanner..."
python3 scripts/security_scanner.py

echo ""
echo "[1/6] Running Environmental Doctor Probe..."
python3 scripts/doctor.py

echo ""
echo "[2/6] Running CI Validators..."
python3 scripts/ci_validate_skills.py

echo ""
echo "[3/6] Running Test Prompt Evaluator..."
python3 scripts/run_eval.py

echo ""
echo "[4/6] Running Birth Certificate Check..."
python3 scripts/check_birth_certificate.py

echo ""
echo "[5/6] System Health Check Completed."
echo "✅ Guyue local validation passed."
echo "=========================================="
