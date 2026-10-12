self: { config, lib, pkgs, ... }:
let
  cfg = config.programs.nixdatifier-noctalia;
  package = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
  json = pkgs.formats.json { };
in {
  options.programs.nixdatifier-noctalia = {
    enable = lib.mkEnableOption "the native Noctalia Nix plugin";
    targets = lib.mkOption {
      type = lib.types.listOf (lib.types.attrsOf lib.types.str);
      default = [ ];
      description = "Explicit targets. Empty enables host/profile autodetection.";
    };
  };
  config = lib.mkIf cfg.enable {
    home.packages = [ package ];
    xdg.dataFile."noctalia/plugins/nixdatifier-noctalia".source = "${package}/share/noctalia/plugins/nixdatifier-noctalia";
    xdg.configFile = lib.mkIf (cfg.targets != [ ]) {
      "nixdatifier-noctalia/targets.json".source = json.generate "nixdatifier-targets.json" {
        schema_version = 1;
        targets = cfg.targets;
      };
    };
  };
}
