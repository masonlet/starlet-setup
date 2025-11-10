import sys
import subprocess
from pathlib import Path

def main():
  if len(sys.argv) != 2:
    print("Usage: python starlet-setup.py <github-repo-url>")
    sys.exit(1)

  repo_url = sys.argv[1]
  repo_name = Path(repo_url).stem.replace('.git','')

  print(f"Cloning {repo_name}")
  subprocess.run(["git", "clone", repo_url], check=True)
  print("")

  print("Create build directory")
  build_path = Path(repo_name) / "build"
  build_path.mkdir(exist_ok=True)
  print("")

  print("Generating build files")
  subprocess.run(["cmake", ".."], cwd=build_path, check=True)
  print("")

  print("Building project")
  subprocess.run(["cmake", "--build", "."], cwd=build_path, check=True)
  print("")

  print(f"Finished, Project built in {repo_name}/build")

if __name__ == "__main__":
  main()
