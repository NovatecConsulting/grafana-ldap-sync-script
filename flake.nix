{
  description = "Basic template for a dev shell";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    devenv.inputs.nixpkgs.follows = "nixpkgs";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs =
    {
      self,
      nixpkgs,
      devenv,
      systems,
      ...
    }@inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      packages = forEachSystem (system: {
        devenv-up = self.devShells.${system}.default.config.procfileScript;
      });
      devShells = forEachSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            config.allowBroken = true;
          };
          setupScript = pkgs.writeShellScriptBin "setup-env" ''
            [ ! -f .env ] || export $(grep -v '^#' .env | xargs)
          '';
        in
        {
          default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules = [
              {
                name = "Basic development shell";
                dotenv.disableHint = true;

                languages = with pkgs; {
                  nix.enable = true;
                  nix.lsp.package = nixd;
                  terraform.enable = true;
                  opentofu.enable = true;
                  python.enable = true;
                  python.package = python313Full;
                  python.venv.enable = true;
                };

                packages =
                  with pkgs;
                  [
                    biome
                    terraformer
                    terraforming
                    tflint
                    terraform-providers.grafana
                  ]
                  ++ lib.optionals stdenv.isDarwin (
                    with darwin.apple_sdk.frameworks;
                    [
                      Cocoa
                      CoreFoundation
                      CoreServices
                      Security
                    ]
                  );

                enterShell = ''
                  ${setupScript}/bin/setup-env
                '';
              }
            ];
          };
        }
      );
    };
}