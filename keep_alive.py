#!/usr/bin/env python3
"""
保持 E2B Sandbox 运行
运行方式: python keep_alive.py <sandbox_id>
"""
import os
import sys
import time
from e2b_code_interpreter import Sandbox

if len(sys.argv) < 2:
    print("Usage: python keep_alive.py <sandbox_id>")
    print("\nExample:")
    print("  python keep_alive.py sbx_abc123def456")
    exit(1)

SANDBOX_ID = sys.argv[1]
E2B_API_KEY = os.getenv("E2B_API_KEY")

if not E2B_API_KEY:
    print("❌ E2B_API_KEY not set")
    print("Run: export E2B_API_KEY=e2b_xxx")
    exit(1)

print(f"🔄 Keeping sandbox {SANDBOX_ID} alive...")
print("💡 Press Ctrl+C to stop\n")

try:
    # 连接到已存在的 sandbox
    # API Key 从环境变量 E2B_API_KEY 自动读取
    sandbox = Sandbox.connect(SANDBOX_ID)
    print(f"✅ Connected to sandbox: {SANDBOX_ID}\n")
    
    while True:
        try:
            sandbox.keep_alive()
            print(f"💓 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Keepalive ping sent")
            time.sleep(300)  # 每 5 分钟 ping 一次
        except Exception as e:
            print(f"❌ Keepalive failed: {e}")
            print("Trying to reconnect...")
            time.sleep(10)
            try:
                sandbox = Sandbox.connect(SANDBOX_ID)
                print("✅ Reconnected")
            except:
                print("❌ Could not reconnect. Sandbox may be closed.")
                break
                
except KeyboardInterrupt:
    print("\n\n👋 Stopped keepalive")
    try:
        sandbox.close()
    except:
        pass
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)

