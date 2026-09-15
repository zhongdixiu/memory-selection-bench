from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .cases import load_cases, load_principals, validate_suite
from .config import PROJECT_ROOT, load_bench_config, load_dotenv
from .contracts import Track
from .providers import environment_checks, live_provider_checks
from .reporting import generate_reports
from .runner import run_benchmark


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-bench")
    sub = parser.add_subparsers(dest="command", required=True)
    def command(name: str) -> argparse.ArgumentParser:
        child = sub.add_parser(name)
        child.add_argument("--config", help="benchmark YAML path")
        return child

    command("validate-cases")
    doctor = command("doctor")
    doctor.add_argument("--live", action="store_true", help="call all configured model endpoints")
    smoke = command("smoke")
    smoke.add_argument("--candidate", choices=("mem0", "everos", "all"), default="all")
    run = command("run")
    run.add_argument("--candidate", choices=("mem0", "everos", "all"), required=True)
    run.add_argument("--track", choices=("r0", "r1"), required=True)
    run.add_argument("--suite", choices=("decision", "full"), default="decision")
    probe = command("probe")
    probe.add_argument("--candidate", choices=("mem0", "everos", "all"), default="all")
    command("report")
    integration = command("integrate")
    integration.add_argument("--candidate", choices=("mem0", "everos", "all"), default="all")
    integration.add_argument("--track", choices=("r0", "r1"), default="r0")
    return parser


async def _run_candidates(config, candidate: str, track: Track, suite: str) -> int:
    candidates = ("mem0", "everos") if candidate == "all" else (candidate,)
    exit_code = 0
    for item in candidates:
        run_id, manifest = await run_benchmark(config=config, candidate=item, track=track, suite=suite)
        print(json.dumps({"run_id": run_id, "candidate": item, "status": manifest["status"], "error": manifest.get("error")}, ensure_ascii=False))
        if manifest["status"] in {"FAIL", "BLOCKED", "TIMEOUT"}:
            exit_code = 1
    return exit_code


async def _main_async(args: argparse.Namespace) -> int:
    config = load_bench_config(args.config)
    if args.command == "validate-cases":
        cases = load_cases(PROJECT_ROOT / "data/cases.yaml")
        principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
        errors = validate_suite(cases, principals)
        print(json.dumps({"ok": not errors, "case_count": len(cases), "errors": errors}, ensure_ascii=False, indent=2))
        return int(bool(errors))
    if args.command == "doctor":
        checks = environment_checks(config)
        if args.live and all(item["ok"] for item in checks if item["kind"] == "secret"):
            checks.extend(await live_provider_checks(config))
        elif args.live:
            checks.append({"kind": "live", "name": "providers", "ok": False, "skipped": True, "error": "missing required secret"})
        print(json.dumps({"ok": all(item["ok"] for item in checks), "checks": checks}, ensure_ascii=False, indent=2))
        return int(not all(item["ok"] for item in checks))
    if args.command == "smoke":
        return await _run_candidates(config, args.candidate, Track.R0, "smoke")
    if args.command == "run":
        return await _run_candidates(config, args.candidate, Track(args.track), args.suite)
    if args.command == "probe":
        return await _run_candidates(config, args.candidate, Track.P_NATIVE, "probe")
    if args.command == "report":
        created = generate_reports(config)
        print(json.dumps({"created": [str(path) for path in created]}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "integrate":
        from .email_integration import run_email_integration

        return await run_email_integration(config=config, candidate=args.candidate, track=Track(args.track))
    raise AssertionError(args.command)


def main() -> int:
    load_dotenv()
    return asyncio.run(_main_async(_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
