# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.docker
    pkgs.docker-compose
  ];

  # Sets environment variables in the workspace
  env = {
    # Set the PORT environment variable for the web preview
    PORT = "5000";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
      "ms-azuretools.vscode-docker"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # This will be the name of the preview
        web = {
          # The command to run your application
          command = [ "python" "main.py" ];
          # What to do with the output of the command
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        install-deps = "pip install -r requirements.txt";
        create-db-dir = "mkdir -p database";
      };
    };
  };

  # Enable the docker service
  services.docker = {
    enable = true;
  };
}
