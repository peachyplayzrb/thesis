# Contribution Statement

This project contributes a playlist generation pipeline that is designed to be transparent, controllable, and reproducible. It shows how recommendation behaviour can be inspected, adjusted, and evaluated when user listening data and candidate tracks come from different sources. Each stage of the pipeline produces outputs that can be checked, and the effects of changing settings can be tested and measured.

Chapter 2 establishes the evidence gap that motivates this contribution: optimisation-centric and accountability-centric studies are typically evaluated separately, leaving weak joint evidence about how preference uncertainty, candidate exclusion logic, explanation fidelity, and reproducibility interact within one pipeline. This project addresses that gap by engineering a deterministic playlist generation pipeline where these interactions are explicit and testable.

The contribution is intentionally bounded to engineering evidence under single-user deterministic scope. It does not claim model-family superiority or benchmark state-of-the-art performance.
