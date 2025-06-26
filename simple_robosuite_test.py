#!/usr/bin/env python3
"""
Simple RoboSuite Test
"""

import numpy as np
import sys
import os

# RoboSuite 경로 추가
robosuite_path = "/home/work/data/JBP/pooling/gr00t_robosuite/robosuite"
if robosuite_path not in sys.path:
    sys.path.insert(0, robosuite_path)

def test_robosuite_import():
    """RoboSuite import 테스트"""
    try:
        import robosuite
        print(f"✅ RoboSuite imported successfully! Version: {robosuite.__version__}")
        return True
    except Exception as e:
        print(f"❌ RoboSuite import failed: {e}")
        return False

def test_environment_creation():
    """환경 생성 테스트"""
    try:
        # 환경 클래스 직접 import
        from robosuite.environments.manipulation.pick_place import PickPlace
        print("✅ PickPlace environment class imported")
        
        # 간단한 설정으로 환경 생성 시도
        env_config = {
            "robots": "Panda",
            "has_renderer": False,  # 렌더러 비활성화
            "has_offscreen_renderer": False,
            "use_camera_obs": False,
            "control_freq": 20,
        }
        
        print("🔄 Creating PickPlace environment...")
        env = PickPlace(**env_config)
        print("✅ Environment created successfully!")
        
        # 환경 리셋 테스트
        obs = env.reset()
        print(f"✅ Environment reset successful! Obs keys: {list(obs.keys())}")
        
        # 액션 공간 확인
        print(f"📊 Action space: {env.action_spec}")
        
        return env
        
    except Exception as e:
        print(f"❌ Environment creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dual_arm_environment():
    """Dual-arm 환경 테스트"""
    try:
        from robosuite.environments.manipulation.two_arm_peg_in_hole import TwoArmPegInHole
        print("✅ TwoArmPegInHole environment class imported")
        
        env_config = {
            "robots": ["Panda", "Panda"],  # 두 개의 팬더 로봇
            "has_renderer": False,
            "has_offscreen_renderer": False,
            "use_camera_obs": False,
            "control_freq": 20,
        }
        
        print("🔄 Creating TwoArmPegInHole environment...")
        env = TwoArmPegInHole(**env_config)
        print("✅ Dual-arm environment created successfully!")
        
        obs = env.reset()
        print(f"✅ Dual-arm environment reset successful!")
        print(f"📊 Observation keys: {list(obs.keys())}")
        print(f"📊 Action dimension: {env.action_spec}")
        
        return env
        
    except Exception as e:
        print(f"❌ Dual-arm environment creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_simulation_step(env):
    """간단한 시뮬레이션 스텝 테스트"""
    if env is None:
        return
        
    try:
        print("🔄 Testing simulation steps...")
        
        for step in range(10):
            # 올바른 액션 생성
            action_low, action_high = env.action_spec
            action = np.random.uniform(action_low, action_high)
            
            # 스텝 실행
            obs, reward, done, info = env.step(action)
            
            print(f"Step {step}: reward={reward:.3f}, done={done}")
            
            if done:
                print("🔄 Environment done, resetting...")
                obs = env.reset()
                
        print("✅ Simulation steps successful!")
        
    except Exception as e:
        print(f"❌ Simulation step failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🤖 RoboSuite Integration Test")
    print("=" * 50)
    
    # Step 1: Import 테스트
    print("\n1️⃣ Testing RoboSuite Import...")
    if not test_robosuite_import():
        print("❌ Cannot proceed without RoboSuite")
        return
    
    # Step 2: 단일 팔 환경 테스트
    print("\n2️⃣ Testing Single-Arm Environment...")
    single_env = test_environment_creation()
    
    if single_env:
        test_simple_simulation_step(single_env)
    
    # Step 3: 이중 팔 환경 테스트
    print("\n3️⃣ Testing Dual-Arm Environment...")
    dual_env = test_dual_arm_environment()
    
    if dual_env:
        test_simple_simulation_step(dual_env)
    
    print("\n📊 Test Summary:")
    print(f"✅ RoboSuite Import: {'Success' if 'robosuite' in sys.modules else 'Failed'}")
    print(f"✅ Single-Arm Env: {'Success' if single_env else 'Failed'}")
    print(f"✅ Dual-Arm Env: {'Success' if dual_env else 'Failed'}")
    
    if dual_env or single_env:
        print("\n🎉 RoboSuite integration successful!")
        print("💡 Ready for bi-manipulator visualization!")
    else:
        print("\n⚠️ RoboSuite integration issues detected")
        print("💡 Falling back to simulation mode")

if __name__ == "__main__":
    main() 