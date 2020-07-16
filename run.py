from script.core import export
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process config path')
    parser.add_argument('--config', dest='config_path', help='Path to the config_mock.yml file', required=True)
    parser.add_argument('--bind', dest='bind', help='Path to the binding file', required=True)
    parser.add_argument('--dry-run', dest='dry_run', default=False, help='Path to the config_mock.yml file',
                        action='store_true')
    args = parser.parse_args()
    export(args.config_path, args.bind, args.dry_run)
