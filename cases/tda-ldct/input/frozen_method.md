Frozen Method Version: v1.0
Freeze Date: 2026-10-15

Primary Method:
Breach-Gated Topological Trust Regularization

Development Patient:
L310 - CLOSED FOR METHOD TUNING

Exploratory Patient:
L333 - NOT USED FOR FINAL METHOD DEVELOPMENT

Independent Final-Test Patient:
L506 - UNOPENED AT METHOD FREEZE

Primary checkpoints:
- last_control.pt
- last_selective_ph_v1.pt
- last_selective_ph_gated_trust.pt

Frozen key settings:
- H1 topology
- reliable QD Top-30 candidates
- minimum stable views = 2/3
- noise sigma = 0.002
- blur sigma = 0.45
- breach correction scope = reliable original-QD Top5 H1
- safe trust scope = all reliable H1
- safe weight = 1.0
- safe deadband = 0
- breach-gated trust = enabled
- topology every 12 optimizer steps
- target topology gradient ratio = 0.10
- epochs = 3
- samples per epoch = 1024
- batch size = 4
- patch size = 256
- learning rate = 3e-5
- checkpoint rule = LAST checkpoint

L310 frozen conclusion:
GATED_TRUST_SUPPORTED_COLLATERAL_REDUCED

Important:
L310 may be used only for code audit / reproducibility checks.
It must no longer be used for method or hyperparameter selection.

L506 must remain unopened until:
1. source-code audit is completed;
2. final-test protocol is written and frozen.
