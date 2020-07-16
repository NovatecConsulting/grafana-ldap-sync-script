from script.core import export
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process config path')
    parser.add_argument('--config', dest='config_path', default="config_mock.yml", help='Path to the config_mock.yml file')
    args = parser.parse_args()
    export(args.config_path)
