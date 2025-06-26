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
        self.fig = plt.figure(figsize=(16, 12))
        
        # 4개 서브플롯으로 확장
        self.ax_3d = self.fig.add_subplot(221, projection='3d')
        self.ax_top = self.fig.add_subplot(222)
        self.ax_metrics = self.fig.add_subplot(223)
        self.ax_ai = self.fig.add_subplot(224)
        
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
        
        # AI 상태 추가
        self.ai_strategy = "Bilateral_Coordination"
        self.confidence = 0.8
        self.cooperation_score = 0.0
        
        # 기록 추가
        self.history = {
            'time': [], 'cooperation': [], 'efficiency': [], 'ai_confidence': []
        }
        
    def draw_arm(self, base, end, color, label):
        """팔 그리기"""
        # 간단한 3링크 팔
        mid1 = base + (end - base) * 0.4
        mid2 = base + (end - base) * 0.7
        
        positions = np.array([base, mid1, mid2, end])
        
        self.ax_3d.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
                        color=color, linewidth=4, marker='o', markersize=6, label=label)
        return positions
        
    def update_positions(self):
        """위치 업데이트"""
        dt = 0.1
        self.time += dt
        
        # AI 의사결정
        self.ai_decision_making()
        
        # 협력 점수 계산
        cooperation = self.calculate_cooperation_score()
        
        # 효율성 계산
        efficiency = max(0, 1.0 - np.linalg.norm(self.object_pos - self.target_pos) / 0.6)
        
        # 기록 업데이트
        self.history['time'].append(self.time)
        self.history['cooperation'].append(cooperation)
        self.history['efficiency'].append(efficiency)
        self.history['ai_confidence'].append(self.confidence)
        
        # 메모리 관리
        if len(self.history['time']) > 100:
            for key in self.history:
                self.history[key].pop(0)
        
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
                
    def calculate_cooperation_score(self):
        """협력 점수 계산"""
        obj_center = self.object_pos
        left_vec = self.left_pos - obj_center
        right_vec = self.right_pos - obj_center
        
        if np.linalg.norm(left_vec) > 0 and np.linalg.norm(right_vec) > 0:
            # 대칭성 점수
            symmetry = 1.0 - abs(np.linalg.norm(left_vec) - np.linalg.norm(right_vec)) / 0.3
            
            # 각도 점수 (180도가 이상적)
            cos_angle = np.dot(left_vec, right_vec) / (np.linalg.norm(left_vec) * np.linalg.norm(right_vec))
            angle_score = abs(cos_angle + 1.0)
            
            self.cooperation_score = np.clip((symmetry + angle_score) / 2, 0, 1)
        else:
            self.cooperation_score = 0
            
        return self.cooperation_score
        
    def ai_decision_making(self):
        """AI 의사결정 시스템"""
        left_to_obj = np.linalg.norm(self.left_pos - self.object_pos)
        right_to_obj = np.linalg.norm(self.right_pos - self.object_pos)
        
        if left_to_obj < 0.1 and right_to_obj < 0.1:
            self.ai_strategy = "Precision_Grasping"
            self.confidence = 0.95
        elif min(left_to_obj, right_to_obj) < 0.15:
            self.ai_strategy = "Coordinated_Approach"
            self.confidence = 0.85
        else:
            self.ai_strategy = "Bilateral_Coordination"
            self.confidence = 0.7

    def visualize_3d(self):
        """3D 시각화"""
        self.ax_3d.clear()
        
        # 제목
        self.ax_3d.set_title(f'Advanced Bi-Manipulator - {self.phase}', 
                            fontsize=14, weight='bold')
        
        # 팔 그리기
        left_joints = self.draw_arm(self.left_base, self.left_pos, 'blue', 'Left Arm')
        right_joints = self.draw_arm(self.right_base, self.right_pos, 'red', 'Right Arm')
        
        # 객체
        obj_color = 'orange' if self.grasping else 'green'
        self.ax_3d.scatter(*self.object_pos, color=obj_color, s=300, marker='s', 
                          label=f'Object {"(Grasped)" if self.grasping else ""}')
        
        # 목표
        self.ax_3d.scatter(*self.target_pos, color='purple', s=200, marker='^', 
                          alpha=0.7, label='Target')
        
        # 베이스
        self.ax_3d.scatter(*self.left_base, color='darkblue', s=150, marker='D')
        self.ax_3d.scatter(*self.right_base, color='darkred', s=150, marker='D')
        
        # 궤적 (간단히)
        if hasattr(self, 'obj_trail'):
            trail = np.array(self.obj_trail)
            if len(trail) > 1:
                self.ax_3d.plot(trail[:, 0], trail[:, 1], trail[:, 2], 
                               'gray', alpha=0.5, linewidth=2, linestyle='--')
        else:
            self.obj_trail = []
            
        self.obj_trail.append(self.object_pos.copy())
        if len(self.obj_trail) > 50:  # 궤적 길이 제한
            self.obj_trail.pop(0)
        
        # 설정
        self.ax_3d.set_xlim([-0.5, 0.5])
        self.ax_3d.set_ylim([-0.4, 0.4])
        self.ax_3d.set_zlim([0, 0.3])
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        self.ax_3d.legend()
        
    def visualize_top_view(self):
        """탑뷰 시각화"""
        self.ax_top.clear()
        self.ax_top.set_title('Top-Down Coordination View', fontsize=12, weight='bold')
        
        # 현재 위치
        self.ax_top.scatter(self.left_pos[0], self.left_pos[1], color='blue', s=150, 
                           marker='o', label='Left EEF')
        self.ax_top.scatter(self.right_pos[0], self.right_pos[1], color='red', s=150, 
                           marker='o', label='Right EEF')
        self.ax_top.scatter(self.object_pos[0], self.object_pos[1], color='green', s=200, 
                           marker='s', label='Object')
        self.ax_top.scatter(self.target_pos[0], self.target_pos[1], color='purple', s=150, 
                           marker='^', label='Target')
        
        # 협력 영역 표시
        circle = plt.Circle((self.object_pos[0], self.object_pos[1]), 0.15, 
                           fill=False, color='gray', linestyle='--', alpha=0.5)
        self.ax_top.add_patch(circle)
        
        self.ax_top.set_xlim([-0.6, 0.6])
        self.ax_top.set_ylim([-0.5, 0.5])
        self.ax_top.legend()
        self.ax_top.grid(True, alpha=0.3)
        
    def visualize_metrics(self):
        """성능 지표 시각화"""
        self.ax_metrics.clear()
        self.ax_metrics.set_title('Performance Metrics', fontsize=12, weight='bold')
        
        if len(self.history['time']) > 1:
            times = self.history['time'][-30:]
            coop = self.history['cooperation'][-30:]
            eff = self.history['efficiency'][-30:]
            conf = self.history['ai_confidence'][-30:]
            
            self.ax_metrics.plot(times, coop, 'purple', linewidth=2, label='Cooperation')
            self.ax_metrics.plot(times, eff, 'green', linewidth=2, label='Efficiency')
            self.ax_metrics.plot(times, conf, 'orange', linewidth=2, label='AI Confidence')
            
            # 임계값 선
            self.ax_metrics.axhline(y=0.8, color='green', linestyle=':', alpha=0.5)
            self.ax_metrics.axhline(y=0.6, color='orange', linestyle=':', alpha=0.5)
            self.ax_metrics.axhline(y=0.4, color='red', linestyle=':', alpha=0.5)
        
        self.ax_metrics.set_ylim([0, 1])
        self.ax_metrics.set_ylabel('Score')
        self.ax_metrics.legend()
        self.ax_metrics.grid(True, alpha=0.3)
        
    def visualize_ai_status(self):
        """AI 상태 시각화"""
        self.ax_ai.clear()
        self.ax_ai.set_title('AI Decision System', fontsize=12, weight='bold')
        
        # 상태 정보
        left_dist = np.linalg.norm(self.left_pos - self.object_pos)
        right_dist = np.linalg.norm(self.right_pos - self.object_pos)
        
        status_text = f"""
Strategy: {self.ai_strategy}
Phase: {self.phase}
Confidence: {self.confidence:.2f}
Cooperation: {self.cooperation_score:.3f}

Left Distance: {left_dist:.3f}m
Right Distance: {right_dist:.3f}m

Time: {self.time:.1f}s
        """
        
        self.ax_ai.text(0.1, 0.9, status_text, transform=self.ax_ai.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 거리 바 차트
        distances = [left_dist, right_dist]
        labels = ['Left-Obj', 'Right-Obj']
        colors = ['blue', 'red']
        
        bars = self.ax_ai.bar(labels, distances, color=colors, alpha=0.7)
        for bar, dist in zip(bars, distances):
            height = bar.get_height()
            self.ax_ai.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{dist:.3f}m', ha='center', va='bottom', fontsize=9)
        
        self.ax_ai.set_ylim([0, 0.5])
        self.ax_ai.set_ylabel('Distance (m)')
        
    def visualize_all(self):
        """모든 시각화 업데이트"""
        self.visualize_3d()
        self.visualize_top_view()
        self.visualize_metrics()
        self.visualize_ai_status()
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
            robot.visualize_all()
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