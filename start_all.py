"""
Start both backend and frontend servers together
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Store process references
processes = []

def cleanup():
    """Clean up all processes on exit"""
    print("\n\nShutting down servers...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
    print("All servers stopped.")
    sys.exit(0)

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    cleanup()

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_backend():
    """Check if backend is already running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_frontend():
    """Check if frontend is already running"""
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=2)
        return True
    except:
        return False

def main():
    print("=" * 70)
    print(" " * 15 + "Retail Cortex - Starting All Services")
    print("=" * 70)
    print()
    
    # Check if already running
    if check_backend():
        print("[WARNING] Backend already running on port 8000")
        print("          Skipping backend startup...")
    else:
        print("[1/2] Starting Backend Server...")
        print("      URL: http://localhost:8000")
        print("      API Docs: http://localhost:8000/docs")
        print()
        
        backend_process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(backend_process)
        print("      [OK] Backend process started (PID: {})".format(backend_process.pid))
    
    # Wait for backend to start
    print()
    print("      Waiting for backend to initialize...")
    for i in range(10):
        time.sleep(1)
        if check_backend():
            print("      [OK] Backend is ready!")
            break
        print(f"      Waiting... ({i+1}/10)")
    else:
        print("      [WARNING] Backend may not be ready yet")
    
    print()
    
    # Check frontend
    if check_frontend():
        print("[WARNING] Frontend already running on port 3000")
        print("          Skipping frontend startup...")
    else:
        print("[2/2] Starting Frontend Server...")
        print("      URL: http://localhost:3000")
        print()
        
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print("      [ERROR] Frontend directory not found!")
            cleanup()
            return
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("      Installing frontend dependencies...")
            install_process = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                shell=True
            )
            if install_process.returncode != 0:
                print("      [ERROR] Failed to install dependencies")
                cleanup()
                return
        
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(frontend_process)
        print("      [OK] Frontend process started (PID: {})".format(frontend_process.pid))
    
    print()
    print("=" * 70)
    print(" " * 20 + "✅ All Services Running!")
    print("=" * 70)
    print()
    print("📍 Access Points:")
    print("   Frontend:  http://localhost:3000")
    print("   Backend:   http://localhost:8000")
    print("   API Docs:  http://localhost:8000/docs")
    print()
    print("💡 Tips:")
    print("   - Open http://localhost:3000 in your browser")
    print("   - Register/Login to get started")
    print("   - Set your market categories to see industry trends")
    print("   - Add keywords to track specific products")
    print()
    print("⚠️  Press Ctrl+C to stop all servers")
    print("=" * 70)
    print()
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            for process in processes[:]:
                if process.poll() is not None:
                    print(f"\n[WARNING] Process {process.pid} has stopped")
                    processes.remove(process)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        cleanup()

