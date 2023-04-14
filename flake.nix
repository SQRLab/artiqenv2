{
  inputs.artiq.url = "git+https://github.com/m-labs/artiq.git?ref=release-7";
  inputs.extrapkg.url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git?ref=release-7";
  inputs.extrapkg.inputs.artiq.follows = "artiq";
  outputs = { self, artiq, extrapkg}:
    let
      pkgs = artiq.inputs.nixpkgs.legacyPackages.x86_64-linux;
      aqmain = artiq.packages.x86_64-linux;
      aqextra = extrapkg.packages.x86_64-linux;
      daxVersion = "6.10";#adding dax
      daxSrc = builtins.fetchGit {
        url = "https://gitlab.com/duke-artiq/dax.git";
        ref = "refs/tags/v${daxVersion}";
      };

    in {
      defaultPackage.x86_64-linux = pkgs.buildEnv {
        name = "artiq-env";
        paths = [
          # ========================================
          # EDIT BELOW
          # ========================================
          (pkgs.python3.withPackages(ps: [
            # List desired Python packages here.
            aqmain.artiq
            aqextra.flake8-artiq


            # The NixOS package collection contains many other packages that you may find
            # interesting. Here are some examples:
            ps.pandas
            ps.numpy
            ps.scipy
            ps.matplotlib
            # DAX
            aqextra.dax
            aqextra.dax-applets
          ]))
          # List desired non-Python packages here
          aqmain.openocd-bscanspi # needed if and only if flashing boards
          # Other potentially interesting packages from the NixOS package collection:
          pkgs.gtkwave
          #pkgs.julia #julia package does not currently work
          # ========================================
          # EDIT ABOVE
          # ========================================
        ];
      };
    };
}

