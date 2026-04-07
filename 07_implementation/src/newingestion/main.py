"""
Main entry point for the newingestion stage.

Follows the thin wrapper pattern used by other stages:
- Parse command-line arguments
- Instantiate IngestionStage
- Call run()
- Print deterministic summary
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional, List

from .stage import IngestionStage


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone newingestion stage: extract, normalize, and emit ingestion data."
    )

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory for the newingestion package (contains outputs/)"
    )

    parser.add_argument(
        "--run-config",
        type=Path,
        required=False,
        default=None,
        help="Optional path to run-config JSON or YAML with control settings"
    )

    parser.add_argument(
        "--run-id",
        type=str,
        required=False,
        default=None,
        help="Optional explicit run ID (auto-generated if omitted)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--enable-interactive-oauth",
        action="store_true",
        help="Enable interactive OAuth redirect-URI flow if credentials missing"
    )

    parser.add_argument(
        "--oauth-client-id",
        type=str,
        default=None,
        help="Spotify OAuth client ID (for interactive flow)"
    )

    parser.add_argument(
        "--oauth-client-secret",
        type=str,
        default=None,
        help="Spotify OAuth client secret (for interactive flow)"
    )

    parser.add_argument(
        "--oauth-redirect-uri",
        type=str,
        default="http://127.0.0.1:8888/callback",
        help="Redirect URI for OAuth callback (default: http://127.0.0.1:8888/callback)"
    )

    parser.add_argument(
        "--oauth-timeout-seconds",
        type=int,
        default=600,
        help="Seconds to wait for user OAuth (default: 600)"
    )

    parser.add_argument(
        "--oauth-no-browser",
        action="store_true",
        help="Skip auto-opening browser for OAuth (print URL instead)"
    )

    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    """
    Execute the newingestion stage.

    Args:
        argv: Optional command-line arguments (uses sys.argv if omitted)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args(argv)

    try:
        # Build stage config from CLI args to pass OAuth settings through precedence chain
        stage_config = {"newingestion": {}}

        # Add OAuth settings if provided
        if args.enable_interactive_oauth:
            stage_config["newingestion"]["enable_interactive_oauth"] = True
        if args.oauth_client_id:
            stage_config["newingestion"]["oauth_client_id"] = args.oauth_client_id
        if args.oauth_client_secret:
            stage_config["newingestion"]["oauth_client_secret"] = args.oauth_client_secret
        if args.oauth_redirect_uri != "http://127.0.0.1:8888/callback":
            stage_config["newingestion"]["oauth_redirect_uri"] = args.oauth_redirect_uri
        if args.oauth_timeout_seconds != 600:
            stage_config["newingestion"]["oauth_timeout_seconds"] = args.oauth_timeout_seconds
        if args.oauth_no_browser:
            stage_config["newingestion"]["oauth_no_browser"] = True

        # Set as env var so it's picked up by control resolution (highest precedence)
        if stage_config["newingestion"]:
            os.environ["BL_STAGE_CONFIG_JSON"] = json.dumps(stage_config)

        # Instantiate and run stage
        stage = IngestionStage(
            root=args.root,
            run_config_path=args.run_config,
            run_id=args.run_id,
        )

        artifacts = stage.run()
        summary = stage.build_summary(artifacts)

        # Print deterministic summary
        print(json.dumps(summary, indent=2, default=str))

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
