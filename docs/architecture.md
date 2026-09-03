# WARAVUTAI Technical Architecture Documentation

## 1. Purpose

WARAVUTAI is an evidence-first software architecture designed to distinguish between the existence of source code and verified runtime behavior.

The fundamental principle is:

> CODE EXISTS ≠ RUNTIME WORKS

The system separates:

1. Specification
2. Implementation
3. Execution
4. Raw Evidence
5. Validation
6. Derived State
7. Claim Boundary
8. Production Verification

A component is not considered verified merely because source code exists, a build succeeds, or an application can be launched.

---

## 2. Architecture Overview

```text
                         WARAVUTAI
                             │
              ┌──────────────┴──────────────┐
              │                             │
        PRODUCT LAYER                 EVIDENCE LAYER
              │                             │
           PANDA                    G23 Verification
              │                             │
       Device / Creator              Evidence Gates
              │                             │
        Backend APIs                Validation Engine
              │                             │
        AI Core / Services          Derived State
              │                             │
              └──────────────┬──────────────┘
                             │
                       Claim Boundary
                             │
                  Production Verification

---

## 3. Core Architecture Layers

### 3.1 Product Layer

The Product Layer contains user-facing functionality:

- PANDA APK
- Creator functionality
- Device Services
- Backend services
- PandaZenUniverse portal
- AI Core

The Product Layer answers:

> What does the system attempt to do?

It does not independently answer:

> Has the claimed behavior been verified?

### 3.2 Runtime Layer

The Runtime Layer is responsible for actual execution.

Examples:

- Android application execution
- Backend execution
- command execution
- ADB interaction
- process state
- runtime output
- exit codes

Runtime evidence must be collected from actual execution rather than inferred from source code.

### 3.3 Evidence Layer

The Evidence Layer records observable facts produced during execution.

Typical evidence includes:

- stdout
- stderr
- exit code
- process state
- package state
- ADB transport state
- generated artifacts
- timestamps
- SHA-256 hashes
- test results
- manifests
- audit records

Evidence is treated as data.

Claims are treated separately.

---

## 4. G23 Verification Architecture

G23 is the protection and verification boundary of WARAVUTAI.

Its responsibility is to prevent unsupported evidence from being promoted into stronger claims.

```text
RAW OBSERVATION
      |
      v
EVIDENCE RECORD
      |
      v
VALIDATION
      |
      v
DERIVED STATE
      |
      v
CLAIM BOUNDARY
      |
      v
PRODUCTION VERIFICATION

---

## 5. Evidence Does Not Equal Truth

WARAVUTAI separates evidence from claims.

Evidence can demonstrate that an observable event occurred.

Evidence does not automatically prove the full semantic meaning of that event.

The following principles are enforced:

```text
CODE EXISTS              != RUNTIME WORKS
RUNTIME OUTPUT           != CLAIM TRUTH
EXIT CODE 0              != ALL CLAIMS TRUE
SHA-256 MATCH            != SEMANTIC TRUTH
CLIENT ASSERTION         != AUTHORITATIVE EVIDENCE
LOCAL TEST               != PRODUCTION VERIFICATION
```

A stronger claim requires stronger and independently relevant evidence.

G23 must therefore prevent evidence from being promoted beyond its actual scope.

---

## 6. Runtime Evidence Model

Runtime evidence describes what was observable during an execution or inspection event.

A runtime record may contain:

```text
timestamp
command
environment
target
stdout
stderr
exit_code
process_state
package_state
transport_state
artifact_reference
sha256
test_result
```

Runtime state is classified separately from claim state.

Example:

```text
EXECUTED
   |
   +-- FAILED
   |
   +-- SUCCEEDED
   |
   +-- UNKNOWN
```

A successful command means that the command completed according to its execution contract.

It does not automatically establish that every expected system property is true.

---

## 7. Exit Code Semantics

Exit codes are execution evidence.

The general interpretation is:

```text
exit_code = 0
    |
    +-- command completed successfully
```

and:

```text
exit_code != 0
    |
    +-- command reported failure
```

However:

```text
exit_code = 0
        !=
system claim = VERIFIED
```

For example, a script can successfully execute a check while the check itself determines that the requested capability is unavailable.

Therefore the verifier must preserve both:

```text
EXECUTION RESULT
```

and:

```text
VERIFICATION RESULT
```

as separate fields.

---

## 8. SHA-256 Integrity Model

SHA-256 is used to establish byte-level artifact integrity.

Example:

```text
artifact
   |
   v
SHA-256
   |
   v
digest
```

If the calculated digest matches the expected digest, the bytes represented by the artifact are consistent with that digest.

This establishes integrity of the observed bytes.

It does not establish:

```text
correctness
security
trustworthiness
production readiness
semantic truth
```

Therefore:

```text
SHA-256 MATCH
    |
    +-- integrity evidence
    |
    +-- NOT claim truth
```

---

## 9. Tamper-Evident Principle

WARAVUTAI uses controlled tampering tests to demonstrate whether integrity mechanisms detect modification.

A typical test model is:

```text
CLEAN ARTIFACT
      |
      v
VERIFY
      |
      +----> PASS

TAMPERED ARTIFACT
      |
      v
VERIFY
      |
      +----> FAIL
```

A successful tamper test demonstrates that the tested verification mechanism detected the tested modification.

It does not prove that every possible attack or modification is detectable.

Claims must remain bounded by the exact test scope.

---

## 10. UNKNOWN as a First-Class State

UNKNOWN is a valid final state.

It is not automatically equivalent to:

```text
FAIL
```

and it must never be silently converted into:

```text
PASS
```

or:

```text
VERIFIED
```

The rule is:

```text
MISSING EVIDENCE
      |
      v
UNKNOWN
      |
      v
STOP CLAIM ESCALATION
```

Examples include:

- missing runtime evidence
- unavailable inspection capability
- interrupted ADB transport
- incomplete evidence stream
- ambiguous process state
- unavailable production environment
- unverifiable external dependency

When evidence is insufficient, the system must preserve the uncertainty.

---

## 11. ADB Transport Boundary

ADB is treated as a transport and observation boundary.

The authoritative transport observation begins with:

```bash
adb devices -l
```

The expected verified transport state is:

```text
device
```

Other states must be handled conservatively:

```text
unauthorized -> FAIL / STOP
offline      -> FAIL / STOP
missing      -> UNKNOWN / STOP
unexpected   -> UNKNOWN / STOP
```

ADB transport status does not itself prove application correctness.

It only establishes whether the inspection channel is available at the time of observation.

Wireless debugging ports must not be assumed to be permanently fixed.

A dynamic port must be treated as runtime configuration unless independently verified.

---

## 12. Evidence Stream Continuity

Evidence transmitted through a transport is complete only when continuity can be established.

A typical evidence sequence may be represented as:

```text
START
  |
  +-- Evidence A
  |
  +-- Evidence B
  |
  +-- TRANSPORT GAP
  |
  +-- Evidence C
```

The missing interval must not be reconstructed from assumptions.

A transport gap creates an evidence boundary.

If continuity cannot be established, the affected claim scope must be reduced accordingly.
Disconnected ADB sessions, missing output, truncated logs, or unavailable observations must remain explicitly missing.

The system must never fabricate bytes, events, process states, or runtime observations that were not actually captured.

Evidence continuity is therefore a prerequisite for claims that depend on an uninterrupted observation window.

---

## 13. Process Lifetime

Process existence is a runtime fact that must be observed directly.

Android runtime inspection may use commands such as:

```bash
pidof <package>
ps -A
dumpsys activity services
dumpsys activity activities
```

Each command provides a different observation surface.

APK installation does not prove that a process is running.

A running process does not prove that the intended feature is working.

A process-state claim therefore requires relevant runtime evidence from the actual observation window.

---

## 14. Claim Boundary

G23 separates observation, evidence, validation, derived state, and final claims.

The conceptual chain is:

```text
OBSERVATION
     |
     v
EVIDENCE
     |
     v
VALIDATION
     |
     v
DERIVED STATE
     |
     v
CLAIM
```

Claim strength is bounded by the evidence that directly supports the claim.

For example:

```text
APK EXISTS
    -> may support ARTIFACT EXISTS
    -> does NOT establish APPLICATION WORKS

ADB DEVICE CONNECTED
    -> may support TRANSPORT AVAILABLE
    -> does NOT establish PRODUCTION RUNTIME VERIFIED
```

A stronger claim requires evidence that is both relevant to the claim and sufficiently independent from the assertion being evaluated.

---

## 15. Production Verification

Production verification is a separate state from local, sandbox, device, or staging execution.

A successful test in one environment does not automatically establish correctness in another environment.

Production verification requires evidence tied to the actual production environment and the applicable production contract.

The following must not be sufficient by themselves to derive PRODUCTION_VERIFIED = TRUE:

```text
client metadata
submitted assertions
local test output
artifact hashes
sandbox evidence
development configuration
```

Production status must therefore be derived from independently relevant production evidence rather than from declarations made by the client or from evidence belonging to another environment.

---

## 16. Defense-in-Depth

G23 uses multiple independent verification boundaries rather than relying on a single successful observation.

The conceptual protection layers are:

```text
SYSTEM
  |
  v
RUNTIME / ARTIFACT
  |
  v
EVIDENCE / INTEGRITY
  |
  v
G23 / VALIDATION
  |
  v
CLAIM BOUNDARY
  |
  v
PRODUCTION GATE
```

Each layer answers a different question.

One layer being successful must not hide a failure, absence, uncertainty, or evidence gap in another layer.

Defense-in-depth therefore prevents a weak or indirect signal from being promoted into a stronger system claim.

---

## 17. Security and Verification Philosophy

The verification philosophy is evidence-first and claim-bounded.

The system should:

- record what actually happened
- verify what can be independently verified
- link claims to relevant evidence
- preserve UNKNOWN when evidence is insufficient
- stop when the available evidence is exhausted

The following escalations are prohibited:

```text
APK EXISTS
    -> PRODUCTION READY

TEST PASSED
    -> SECURE

ADB CONNECTED
    -> RUNTIME STABLE

HASH MATCHED
    -> BEHAVIOR CORRECT
```

These transformations exceed the evidentiary scope of their inputs.

---

## 18. Current Verification Status

The current system status is bounded by available implementation and runtime evidence.

The following high-level states are maintained:

```text
Architecture        = DEFINED
Device Services     = PARTIAL
PANDA APK           = IMPLEMENTED / LIMITED
AI Core             = DEFINED
Backend             = PARTIAL
PandaZenUniverse    = PORTAL
G23 Evidence        = VERIFIED
G23 Validation      = VERIFIED
Production Proof    = NOT VERIFIED
```

These states are not permanent declarations.

A status may be changed only when the corresponding implementation, execution, evidence, and validation conditions provide sufficient support for the new state.

Production verification remains explicitly separate from development, sandbox, and device-level evidence.

---

## 19. Documentation Structure

The documentation should remain modular so that architecture, evidence, verification, runtime behavior, and production boundaries can evolve without collapsing into a single undifferentiated record.

The recommended structure is:

```text
docs/
├── README.md
├── architecture/
│   ├── overview.md
│   ├── system-boundaries.md
│   ├── runtime-model.md
│   └── data-flow.md
├── evidence/
│   ├── evidence-model.md
│   ├── runtime-evidence.md
│   ├── sha256-integrity.md
│   ├── tamper-evidence.md
│   └── evidence-gaps.md
├── g23/
│   ├── overview.md
│   ├── evidence-gates.md
│   ├── claim-boundary.md
│   └── unknown-state.md
├── adb/
│   ├── transport-model.md
│   ├── wireless-debugging.md
│   ├── reconnect-model.md
│   └── continuity.md
├── panda/
│   ├── architecture.md
│   ├── android-runtime.md
│   └── creator-boundary.md
├── backend/
│   ├── architecture.md
│   └── authentication.md
├── testing/
│   ├── test-strategy.md
│   ├── runtime-tests.md
│   └── adversarial-tests.md
└── status/
    ├── verification-status.md
    └── production-boundary.md
```

This structure is a documentation target and does not imply that every listed file already exists.

---

## 20. Documentation Rule

Documentation must distinguish between specification, implementation, execution, evidence, validation, derived state, claim, and production verification.

These states must not be collapsed into a single status label.

The documentation records the verification model and the evidence-supported state of the system.

Documentation itself does not constitute proof of runtime behavior, security, correctness, or production deployment.

When evidence is changed, removed, invalidated, or becomes stale, the affected verification status and claim scope must be reviewed.

---

## 21. Final Principle

The complete verification chain is:

```text
CODE EXISTS
     -> IMPLEMENTATION
     -> EXECUTION
     -> RAW EVIDENCE
     -> VALIDATION
     -> DERIVED STATE
     -> CLAIM SCOPE
     -> PRODUCTION VERIFICATION
```

No evidence boundary may be skipped.

The governing principles are:

```text
EVIDENCE DIRECTLY BOUNDS CLAIM.
NO SIGNAL = UNVERIFIED
NO SOURCE MAP = SYSTEM LOGIC RECORD
UNKNOWN = VALID FINAL STATE
EVIDENCE EXHAUSTED = STOP
CLIENT ASSERTION != AUTHORITATIVE TRUTH
```

The objective of this architecture is traceability from system behavior to observable evidence, rather than the appearance of verification.
