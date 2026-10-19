# Add inputs.nixdatifier-noctalia.url = "github:madebycli/nixdatifier-noctalia/main";
# Import this module from modules/features/default.nix, then update the lock and build.
{ inputs, ... }: {
  imports = [ inputs.nixdatifier-noctalia.nixosModules.default ];
  programs.nixdatifier-noctalia.enable = true;
  home-manager.sharedModules = [
    inputs.nixdatifier-noctalia.homeManagerModules.default
    { programs.nixdatifier-noctalia.enable = true; }
  ];
}
