{
  description = "Native Noctalia Nix management with explicit multi-flake targets";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      each = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
      packageFor = system:
        let pkgs = pkgsFor system;
        in pkgs.stdenvNoCC.mkDerivation {
          pname = "nixdatifier-noctalia";
          version = "0.1.0";
          src = self;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          dontConfigure = true;
          dontBuild = true;
          installPhase = ''
            runHook preInstall
            mkdir -p "$out/lib" "$out/share/noctalia/plugins" "$out/bin"
            cp -r backend/nixdatifier "$out/lib/"
            cp -r nixdatifier-noctalia "$out/share/noctalia/plugins/"
            makeWrapper ${pkgs.python3}/bin/python3 "$out/bin/nixdatifier-noctalia" \
              --add-flags "-m nixdatifier.cli" \
              --prefix PYTHONPATH : "$out/lib" \
              --prefix PATH : ${pkgs.lib.makeBinPath (with pkgs; [ bash nix git coreutils systemd direnv util-linux sudo nixos-rebuild-ng ])}
            substitute bin/nixdatifier-install-plugin "$out/bin/nixdatifier-install-plugin" \
              --subst-var-by pluginPath "$out/share/noctalia/plugins/nixdatifier-noctalia"
            chmod +x "$out/bin/nixdatifier-install-plugin"
            runHook postInstall
          '';
          meta = {
            description = "Nix targets and tools for native Noctalia";
            license = pkgs.lib.licenses.mit;
            platforms = systems;
            mainProgram = "nixdatifier-noctalia";
          };
        };
    in {
      packages = each (system: {
        default = packageFor system;
        backend = packageFor system;
      });
      apps = each (system: {
        default = { type = "app"; program = "${packageFor system}/bin/nixdatifier-noctalia"; };
      });
      checks = each (system:
        let pkgs = pkgsFor system;
        in {
          tests = pkgs.runCommand "nixdatifier-tests" {
            nativeBuildInputs = [ pkgs.python3 pkgs.lua5_4 pkgs.luau ];
          } ''
            cp -r ${self} source
            chmod -R u+w source
            cd source
            patchShebangs bin
            export PYTHONPATH="$PWD/backend"
            export NIXDATIFIER_LUA=${pkgs.lua5_4}/bin/lua
            python3 -m unittest discover -s tests -v
            for file in $(find nixdatifier-noctalia -name '*.luau'); do
              luau-compile "$file" >/dev/null
            done
            mkdir -p "$out"
          '';
          package = packageFor system;
        });
      devShells = each (system:
        let pkgs = pkgsFor system;
        in { default = pkgs.mkShell {
          packages = [ pkgs.python3 pkgs.lua5_4 pkgs.luau pkgs.nixfmt-rfc-style ];
          PYTHONPATH = "${toString ./.}/backend";
        }; });
      nixosModules.default = import ./nix/nixos-module.nix self;
      homeManagerModules.default = import ./nix/home-module.nix self;
      formatter = each (system: (pkgsFor system).nixfmt-rfc-style);
    };
}
