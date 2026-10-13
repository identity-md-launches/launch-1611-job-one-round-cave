#!/usr/bin/env python3
"""Run all line checks and offline demonstrations without editing line files."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def checks():
    commands = []
    for number in range(1, 5):
        for folder in sorted(Path(f'line-{number}/tools').iterdir()):
            if list(folder.glob('test_*.py')):
                commands.append((f'line-{number}-{folder.name}-suite',
                    ['-m', 'unittest', 'discover', '-s', str(folder), '-p', 'test_*.py', '-v'], 0))
    commands.extend([
        ('zto-band-demo', ['line-1/tools/zto-band/zto_band.py', '--snapshot', 'line-1/tools/zto-band/observation.json', '--amount', '1'], 0),
        ('zto-path-demo', ['line-1/tools/zto-path/zto_path.py', '--snapshot', 'line-1/tools/zto-path/observation.json'], 0),
        ('zto-path-incomplete', ['line-1/tools/zto-path/zto_path.py', '--snapshot', 'line-1/tools/zto-path/observation.json', '--amount', '1000000000'], 2),
        ('zto-sizes-demo', ['line-1/tools/zto-sizes/zto_sizes.py', '--amount', '1', '--amount', '100000000', '--amount', '1000000000', '--slippage-bps', '100'], 0),
        ('allowance-lens-demo', ['line-2/tools/allowance-lens/allowance_lens.py'], 0),
        ('allowance-changes-demo', ['line-2/tools/allowance-changes/allowance_changes.py'], 0),
        ('permission-gate-demo', ['line-2/tools/permission-gate/permission_gate.py'], 0),
        ('permission-gate-explicit-deny', ['line-2/tools/permission-gate/permission_gate.py', '--observation', 'line-2/tools/permission-gate/live-observation.json', '--policy', 'line-2/tools/permission-gate/demo-policy.json'], 3),
        ('code-lens-demo', ['line-3/tools/code-lens/code_lens.py', '--verify', 'line-3/tools/code-lens/zto-observation.json'], 0),
        ('code-changes-demo', ['line-3/tools/code-changes/code_changes.py', '--before', 'line-3/tools/code-lens/zto-observation.json', '--after', 'line-3/tools/code-changes/zto-after.json'], 0),
        ('code-opcodes-zto', ['line-3/tools/code-opcodes/code_opcodes.py', '--report', 'line-3/tools/code-lens/zto-observation.json'], 0),
        ('code-opcodes-imd', ['line-3/tools/code-opcodes/code_opcodes.py', '--report', 'line-3/tools/code-lens/imd-observation.json'], 0),
        ('call-rehearsal-demo', ['line-4/tools/call-rehearsal/rehearse.py', 'replay', 'line-4/tools/call-rehearsal/zto-observation.json'], 0),
        ('call-rehearsal-revert', ['line-4/tools/call-rehearsal/rehearse.py', 'replay', 'line-4/tools/call-rehearsal/zto-revert-observation.json'], 1),
        ('call-changes-demo', ['line-4/tools/call-changes/call_changes.py', 'demo'], 0),
        ('call-witness-demo', ['line-4/tools/call-witness/call_witness.py', 'demo'], 0),
        ('contract-context-demo', ['shared/contract-context/context.py', 'demo'], 2),
        ('change-context-demo', ['shared/change-context/change_context.py'], 0),
        ('change-context-require-aligned', ['shared/change-context/change_context.py', '--require-aligned'], 2),
    ])
    for folder in sorted(Path('shared').iterdir()):
        if folder.is_dir() and list(folder.glob('test_*.py')):
            commands.append((folder.name + '-suite', ['-m', 'unittest', 'discover', '-s', str(folder), '-p', 'test_*.py', '-v'], 0))
    if Path('shared/witness-context/witness_context.py').exists():
        commands.append(('witness-context-demo', ['shared/witness-context/witness_context.py', 'demo'], 0))
    return commands


def main():
    if not all(Path(f'line-{n}/GOAL.md').is_file() for n in range(1, 5)):
        raise ValueError('run from the workspace root')
    results = []
    for name, args, expected in checks():
        command = [sys.executable, '-B'] + args
        try:
            done = subprocess.run(command, text=True, capture_output=True, timeout=35)
            result = {'name': name, 'command': ['python3', '-B'] + args,
                      'expected_exit': expected, 'exit': done.returncode,
                      'passed': done.returncode == expected, 'stderr': done.stderr}
            if args[0] != '-m':
                output = json.loads(done.stdout) if done.stdout else {}
                result['stdout_sha256'] = hashlib.sha256(done.stdout.encode()).hexdigest()
                result['summary'] = {k: output[k] for k in (
                    'schema', 'status', 'decision', 'verdict', 'candidate_count',
                    'largest_candidate_input_raw', 'verified', 'coherent',
                    'measured_pair_count', 'violating_pair_count', 'missing_pair_count',
                    'block', 'block_number', 'estimate', 'counts', 'summary', 'limits') if k in output}
            results.append(result)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            results.append({'name': name, 'passed': False, 'error': str(exc)})
    print(json.dumps({'schema': 'gathering-local-checks-v2',
        'authority': 'Local contributor checks; no independent certification.',
        'all_passed': all(r['passed'] for r in results), 'checks': results}, indent=2))
    return 0 if all(r['passed'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
