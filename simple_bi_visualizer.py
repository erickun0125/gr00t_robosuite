#!/usr/bin/env python3
"""
간단한 Bi-Manipulator 시각화
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

class SimpleBiManipulator:
    def __init__(self):
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # 초기 위치
        self.left_base = np.array([-0.3, 0, 0])
        self.right_base = np.array([0.3, 0, 0])
        self.left_pos = np.array([-0.2, -0.3, 0.2])
        self.right_pos = np.array([0.2, -0.3, 0.2])
        self.object_pos = np.array([0, -0.2, 0.1])
        self.target_pos = np.array([0, 0.3, 0.15])
        
        # 상태
        self.phase = "Approaching"
        self.grasping = False
        self.time = 0
        
    def draw_arm(self, base, end, color, label):
        """팔 그리기"""
        # 간단한 3링크 팔
        mid1 = base + (end - base) * 0.4
        mid2 = base + (end - base) * 0.7
        
        positions = np.array([base, mid1, mid2, end])
        
        self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
                    color=color, linewidth=4, marker='o', markersize=6, label=label)
        return positions
        
    def update_positions(self):
        """위치 업데이트"""
        dt = 0.1
        self.time += dt
        
        # 단계별 동작
        if self.phase == "Approaching":
            # 객체 양쪽으로 접근
            left_target = self.object_pos + np.array([-0.08, 0, 0])
            right_target = self.object_pos + np.array([0.08, 0, 0])
            
            self.left_pos += (left_target - self.left_pos) * 0.2
            self.right_pos += (right_target - self.right_pos) * 0.2
            
            # 거리 체크
            if (np.linalg.norm(self.left_pos - left_target) < 0.02 and 
                np.linalg.norm(self.right_pos - right_target) < 0.02):
                self.phase = "Grasping"
                self.grasping = True
                
        elif self.phase == "Grasping":
            # 잠시 대기 후 들어올리기
            if self.time > 5:
                self.phase = "Moving"
                
        elif self.phase == "Moving":
            # 목표 위치로 이동
            move_vec = (self.target_pos - self.object_pos) * 0.03
            
            self.object_pos += move_vec
            self.left_pos += move_vec
            self.right_pos += move_vec
            
            # 목표 도달 체크
            if np.linalg.norm(self.object_pos - self.target_pos) < 0.05:
                self.phase = "Completed"
                self.grasping = False
                
    def visualize(self):
        """시각화"""
        self.ax.clear()
        
        # 제목 (한글 제거하고 영어로)
        self.ax.set_title(f'Bi-Manipulator Robot - {self.phase} (t={self.time:.1f}s)', 
                         fontsize=16, pad=20)
        
        # 팔 그리기
        left_joints = self.draw_arm(self.left_base, self.left_pos, 'blue', 'Left Arm')
        right_joints = self.draw_arm(self.right_base, self.right_pos, 'red', 'Right Arm')
        
        # 객체
        obj_color = 'orange' if self.grasping else 'green'
        self.ax.scatter(*self.object_pos, color=obj_color, s=300, marker='s', 
                       label=f'Object {"(Grasped)" if self.grasping else ""}')
        
        # 목표
        self.ax.scatter(*self.target_pos, color='purple', s=200, marker='^', 
                       alpha=0.7, label='Target')
        
        # 베이스
        self.ax.scatter(*self.left_base, color='darkblue', s=150, marker='D')
        self.ax.scatter(*self.right_base, color='darkred', s=150, marker='D')
        
        # 궤적 (간단히)
        if hasattr(self, 'obj_trail'):
            trail = np.array(self.obj_trail)
            if len(trail) > 1:
                self.ax.plot(trail[:, 0], trail[:, 1], trail[:, 2], 
                           'gray', alpha=0.5, linewidth=2, linestyle='--')
        else:
            self.obj_trail = []
            
        self.obj_trail.append(self.object_pos.copy())
        if len(self.obj_trail) > 50:  # 궤적 길이 제한
            self.obj_trail.pop(0)
        
        # 설정
        self.ax.set_xlim([-0.5, 0.5])
        self.ax.set_ylim([-0.4, 0.4])
        self.ax.set_zlim([0, 0.3])
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        
        # 범례
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 정보 텍스트
        info_text = f"""
        Phase: {self.phase}
        Time: {self.time:.1f}s
        Left-Object: {np.linalg.norm(self.left_pos - self.object_pos):.3f}m
        Right-Object: {np.linalg.norm(self.right_pos - self.object_pos):.3f}m
        Object-Target: {np.linalg.norm(self.object_pos - self.target_pos):.3f}m
        """
        
        self.ax.text2D(0.02, 0.98, info_text, transform=self.ax.transAxes,
                      fontsize=10, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()

def main():
    print("🤖 Bi-Manipulator Visualization Started!")
    
    # 시각화 객체 생성
    robot = SimpleBiManipulator()
    
    # 대화형 모드
    plt.ion()
    
    try:
        # 시뮬레이션 루프
        for step in range(200):  # 20초간
            robot.update_positions()
            robot.visualize()
            plt.pause(0.1)
            
            if robot.phase == "Completed" and step > 100:
                print("✅ Task Completed!")
                break
                
            if step % 50 == 0:
                print(f"🔄 Progress... {step/10:.1f}s")
        
        print("\n📊 Simulation Complete")
        print(f"⏱️ Total Time: {robot.time:.1f}s")
        print(f"🎯 Final Phase: {robot.phase}")
        
        final_error = np.linalg.norm(robot.object_pos - robot.target_pos)
        print(f"📍 Final Error: {final_error:.3f}m")
        
        if final_error < 0.05:
            print("🎉 Successfully Completed!")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        plt.ioff()
        plt.close()

if __name__ == "__main__":
    main() 