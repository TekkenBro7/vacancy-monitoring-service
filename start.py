import subprocess
import sys
from subprocess import Popen


def run_fastapi_server() -> Popen:
    print("Starting FastAPI server...")
    process = subprocess.Popen(
        ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="backend",
    )
    return process


def run_react_server() -> Popen:
    print("Starting React server...")
    process = subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    return process


def main() -> None:
    fastapi_proc: Popen | None = None
    react_proc: Popen | None = None
    try:
        fastapi_proc = run_fastapi_server()
        react_proc = run_react_server()

        fastapi_proc.wait()
        react_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down servers...")
        if fastapi_proc:
            fastapi_proc.kill()
        if react_proc:
            react_proc.kill()
        sys.exit(0)


if __name__ == "__main__":
    main()
