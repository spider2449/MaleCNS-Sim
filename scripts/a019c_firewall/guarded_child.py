"""Mandatory A019 child entrypoint; verify policy before loading workload."""
import os
import sys


def main():
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
        print('FIREWALL_REQUIRED_BUT_NOT_ACTIVE', file=sys.stderr, flush=True)
        return 78
    try:
        import validation_firewall as guard
        guard.install()
        if not guard.ACTIVE:
            raise RuntimeError('inactive firewall')
    except BaseException:
        print('FIREWALL_REQUIRED_BUT_NOT_ACTIVE', file=sys.stderr, flush=True)
        return 78
    import runpy
    args = sys.argv[1:]
    if not args:
        return 78
    if args[0] == '-c':
        sys.argv = ['-c', *args[2:]]
        exec(compile(args[1], '<guarded-child>', 'exec'), {'__name__': '__main__'})
    elif args[0] == '-m':
        sys.argv = [args[1], *args[2:]]
        runpy.run_module(args[1], run_name='__main__', alter_sys=True)
    elif not args[0].startswith('-'):
        sys.argv = args
        sys.path.insert(0, os.path.dirname(os.path.abspath(args[0])))
        runpy.run_path(args[0], run_name='__main__')
    else:
        return 78
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
