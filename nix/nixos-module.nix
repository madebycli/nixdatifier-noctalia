self: { config, lib, pkgs, ... }:
let
  cfg = config.programs.nixdatifier-noctalia;
  package = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
in {
  options.programs.nixdatifier-noctalia = {
    enable = lib.mkEnableOption "the native Noctalia Nix backend";
  };
  config = lib.mkIf cfg.enable {
    environment.systemPackages = [ package ];
    # Register this directory as a Noctalia path source, or use the Home Manager module.
    environment.pathsToLink = [ "/share/noctalia/plugins" ];
  };
}
