"""
IngestionStage: thin coordinator for the newingestion workflow.

The stage lifecycle is unchanged, but the normalized contract is now a domain
bundle with canonical JSON artifacts and derived compatibility exports.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
import uuid

from .models import IngestionDomainBundle, NewingestionArtifacts, NewingestionControls, NewingestionPaths
from .runtime_controls import resolve_newingestion_runtime_controls


@dataclass
class IngestionStage:
    root: Path
    run_config_path: Optional[Path] = None
    run_id: Optional[str] = None

    def __post_init__(self):
        if self.run_id is None:
            self.run_id = f"INGESTION-{datetime.now(UTC).isoformat().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:6].upper()}"

    def resolve_paths(self) -> NewingestionPaths:
        return NewingestionPaths.resolve(self.root)

    def resolve_runtime_controls(self) -> NewingestionControls:
        return resolve_newingestion_runtime_controls(self.run_config_path)

    def _get_adapter(self, source_type: str) -> Any:
        from .source_adapters import get_adapter

        cached = getattr(self, "_adapter", None)
        if cached is not None and getattr(cached, "source_type", None) == source_type:
            return cached

        adapter = get_adapter(source_type)
        self._adapter = adapter
        return adapter

    def preflight(self, paths: NewingestionPaths, controls: NewingestionControls) -> None:
        from .source_adapters import SourceAdapterContext

        paths.outputs_dir.mkdir(parents=True, exist_ok=True)

        try:
            adapter = self._get_adapter(controls.source_type)
        except ValueError as exc:
            raise RuntimeError(f"Invalid source type: {exc}")

        context = SourceAdapterContext(root_path=self.root, controls=controls)
        if not adapter.verify_credentials(context):
            if controls.fail_on_missing_scope:
                raise RuntimeError(f"Unable to verify credentials for {controls.source_type}")
            print(
                f"[newingestion] credential check failed for source={controls.source_type}; continuing because fail_on_missing_scope is false.",
                flush=True,
            )

    def collect(self, paths: NewingestionPaths, controls: NewingestionControls) -> dict:
        from .source_adapters import SourceAdapterContext

        adapter = self._get_adapter(controls.source_type)
        context = SourceAdapterContext(root_path=self.root, controls=controls)
        return adapter.collect(context)

    def normalize(self, raw_data: dict, controls: NewingestionControls) -> IngestionDomainBundle:
        from .normalizer import normalize_raw_data_to_bundle

        return normalize_raw_data_to_bundle(raw_data, controls, self.run_id)

    def validate(self, bundle: IngestionDomainBundle, controls: NewingestionControls) -> IngestionDomainBundle:
        from .validator import validate_bundle

        return validate_bundle(bundle, controls)

    def write_outputs(self, bundle: IngestionDomainBundle, paths: NewingestionPaths, controls: NewingestionControls) -> NewingestionArtifacts:
        from .writer import write_outputs

        return write_outputs(bundle, paths.outputs_dir, self.run_id, controls)

    def build_summary(self, artifacts: NewingestionArtifacts) -> dict:
        return {
            "run_id": artifacts.run_id,
            "source_type": artifacts.source_type,
            "counts": artifacts.counts,
            "manifest_artifact": str(artifacts.manifest_artifact_path),
            "duplicate_track_locations_artifact": str(artifacts.duplicate_track_locations_path) if artifacts.duplicate_track_locations_path else None,
            "canonical_artifacts": {name: str(path) for name, path in artifacts.artifact_paths.items()},
            "compatibility_exports": {name: str(path) for name, path in artifacts.compatibility_export_paths.items()},
            "warnings": artifacts.warnings,
        }

    def run(self) -> NewingestionArtifacts:
        paths = self.resolve_paths()
        controls = self.resolve_runtime_controls()
        self.preflight(paths, controls)
        raw_data = self.collect(paths, controls)
        bundle = self.normalize(raw_data, controls)
        bundle = self.validate(bundle, controls)
        return self.write_outputs(bundle, paths, controls)
