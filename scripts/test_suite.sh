#!/bin/bash

# Guyue Digital Twin - Comprehensive Test Suite
# Runs all health probes, CI validators, and internal audits.

set -e

echo "=========================================="
echo "🚀 Starting Guyue Universal Test Suite..."
echo "=========================================="

echo "[0/10] Running Zero-Leakage Security Scanner..."
python3 scripts/security_scanner.py

echo ""
echo "[1/10] Running Long Goal Control-Pack Checker..."
python3 scripts/check_long_goal_pack.py --self-test

echo ""
echo "[2/10] Running Full Install Payload Checker..."
python3 scripts/check_full_install.py --self-test

echo ""
echo "[3/10] Running Claude Marketplace Validation..."
if command -v claude >/dev/null 2>&1; then
  claude plugin validate --strict .
else
  echo "Claude CLI not found; internal marketplace schema checks remain active in CI validation."
fi

echo ""
echo "[4/10] Running MCP Memory Safety Tests..."
python3 scripts/test_mcp_server.py

echo ""
echo "[5/10] Running Environmental Doctor Probe..."
python3 scripts/doctor.py

echo ""
echo "[6/10] Running CI Validators..."
python3 scripts/ci_validate_skills.py

echo ""
echo "[7/10] Running Test Prompt Evaluator..."
python3 scripts/run_eval.py

echo ""
echo "[8/10] Running Birth Certificate Check..."
python3 scripts/check_birth_certificate.py

echo ""
echo "[9/10] System Health Check Completed."
echo "✅ Guyue local validation passed."
echo "=========================================="
