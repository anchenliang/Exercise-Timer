import pygame
import sys
import time
import math
import os

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 1300, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("运动训练计时器")

# 颜色定义
BACKGROUND = (25, 25, 35)
TEXT_COLOR = (220, 220, 220)
ACTIVE_COLOR = (76, 175, 80)  # 绿色 - 活跃项目
INACTIVE_COLOR = (80, 80, 90)  # 灰色 - 非活跃项目
REST_COLOR = (255, 193, 7)  # 黄色 - 休息状态
ACCENT_COLOR = (33, 150, 243)  # 蓝色 - 高亮
TIMER_COLOR = (255, 87, 34)  # 橙色 - 计时器
GROUP_COLOR = (156, 39, 176)  # 紫色 - 组数
NEXT_COLOR = (255, 152, 0)  # 橙色 - 下一个项目

# 尝试加载中文字体
def load_font(font_paths, size):
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                print(f"无法加载字体: {font_path}")
    
    # 如果找不到中文字体，使用默认字体
    print("警告: 未找到中文字体，将使用默认字体")
    return pygame.font.Font(None, size)

# 常见中文字体路径
font_paths = [
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "simhei.ttf",
    "msyh.ttc",
]

# 加载字体
title_font = load_font(font_paths, 60)
exercise_font = load_font(font_paths, 32)
timer_font = load_font(font_paths, 80)
info_font = load_font(font_paths, 30)
small_font = load_font(font_paths, 26)

# 运动项目定义
exercises = [
    "1. 胯下击掌",
    "2. 提膝下压（左）",
    "3. 提膝下压（右）",
    "4. 原地深蹲",
    "5. 小碎步跑",
    "6. 单侧提膝"
]

# 计时参数
EXERCISE_DURATION = 20  # 每个项目20秒
REST_DURATION = 10      # 休息10秒

def clamp_color_value(value):
    """确保颜色值在0-255范围内"""
    return max(0, min(255, value))

def adjust_color(color, adjustment):
    """调整颜色亮度"""
    return tuple(clamp_color_value(c + adjustment) for c in color)

class ExerciseTimer:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.current_exercise = 0
        self.is_resting = False
        # 延迟到按下开始键时再初始化时间，避免启动前就计时
        self.start_time = None
        self.exercise_start_time = None
        self.total_groups = 0
        self.running = False
        self.completed_exercises = 0
        self.total_exercise_time = 0
        self.paused = False
        self.pause_time = 0
        self.pause_remaining_time = 0  # 用于存储暂停时的剩余时间
        
    def start(self):
        if self.paused:
            # 从暂停中恢复
            pause_duration = time.time() - self.pause_time
            if self.exercise_start_time is not None:
                self.exercise_start_time += pause_duration
            if self.start_time is not None:
                self.start_time += pause_duration
            self.paused = False
        else:
            # 第一次开始或重置后重新开始
            now = time.time()
            self.start_time = now
            self.exercise_start_time = now
        self.running = True
        
    def pause(self):
        if self.running and not self.paused:
            self.paused = True
            self.pause_time = time.time()
            # 保存暂停时的剩余时间
            self.pause_remaining_time = self.get_current_time()
            self.running = False
        
    def update(self):
        if not self.running or self.paused:
            return
            
        current_time = time.time()
        elapsed = current_time - self.exercise_start_time
        
        if self.is_resting:
            if elapsed >= REST_DURATION:
                self.is_resting = False
                self.exercise_start_time = current_time
                self.current_exercise = (self.current_exercise + 1) % len(exercises)
                
                # 如果完成一轮，增加组数
                if self.current_exercise == 0:
                    self.total_groups += 1
        else:
            if elapsed >= EXERCISE_DURATION:
                self.is_resting = True
                self.exercise_start_time = current_time
                self.completed_exercises += 1
                self.total_exercise_time += EXERCISE_DURATION
                
    def get_current_time(self):
        if not self.running and self.paused:
            # 暂停时返回暂停时的剩余时间
            return self.pause_remaining_time
            
        if not self.running and not self.paused:
            return 0
            
        current_time = time.time()
        elapsed = current_time - self.exercise_start_time
        
        if self.is_resting:
            remaining = max(0, REST_DURATION - elapsed)
            return remaining
        else:
            remaining = max(0, EXERCISE_DURATION - elapsed)
            return remaining
    
    def get_total_time(self):
        if not self.running or self.paused:
            return 0
        return time.time() - self.start_time

def draw_exercise_box(screen, text, center_x, center_y, width, height, active, is_next=False):
    """绘制运动项目框"""
    x = center_x - width // 2
    y = center_y - height // 2
    
    # 计算颜色
    if active:
        color = ACTIVE_COLOR
        border_color = adjust_color(color, 40)
    elif is_next:
        color = adjust_color(NEXT_COLOR, -40)
        border_color = NEXT_COLOR
    else:
        color = INACTIVE_COLOR
        border_color = adjust_color(color, 20)
    
    # 绘制圆角矩形
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=12)
    pygame.draw.rect(screen, border_color, (x, y, width, height), 3, border_radius=12)
    
    # 绘制文本
    text_surface = exercise_font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

def draw_arrow(screen, start_pos, end_pos, active):
    """绘制箭头"""
    color = REST_COLOR if active else INACTIVE_COLOR
    line_width = 8 if active else 5
    
    # 绘制箭头线
    pygame.draw.line(screen, color, start_pos, end_pos, line_width)
    
    # 绘制箭头头部
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    angle = math.atan2(dy, dx)
    
    arrow_length = 20
    left_angle = angle + math.pi/6
    right_angle = angle - math.pi/6
    
    left_point = (
        end_pos[0] - arrow_length * math.cos(left_angle),
        end_pos[1] - arrow_length * math.sin(left_angle)
    )
    right_point = (
        end_pos[0] - arrow_length * math.cos(right_angle),
        end_pos[1] - arrow_length * math.sin(right_angle)
    )
    
    pygame.draw.polygon(screen, color, [end_pos, left_point, right_point])

def draw_center_timer(screen, timer_obj, current_time):
    """绘制中间的状态计时器"""
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 20
    
    # 计时器背景
    timer_bg_width = 240
    timer_bg_height = 240
    timer_bg = pygame.Rect(
        center_x - timer_bg_width // 2,
        center_y - timer_bg_height // 2,
        timer_bg_width,
        timer_bg_height
    )
    
    # 根据状态选择背景色
    if timer_obj.paused:
        bg_color = (60, 60, 80)
        border_color = (150, 150, 150)
    elif timer_obj.is_resting:
        bg_color = (40, 30, 20)  # 深黄色背景
        border_color = REST_COLOR
    else:
        bg_color = (20, 40, 20)  # 深绿色背景
        border_color = ACTIVE_COLOR
    
    pygame.draw.rect(screen, bg_color, timer_bg, border_radius=15)
    pygame.draw.rect(screen, border_color, timer_bg, 4, border_radius=15)
    
    # 计时器数字 - 修复bug：暂停时显示当前剩余时间
    if timer_obj.paused and timer_obj.pause_remaining_time > 0:
        # 使用暂停时保存的剩余时间
        display_time = timer_obj.pause_remaining_time
    else:
        display_time = current_time
        
    time_text = f"{int(display_time):02d}"
    timer_surface = timer_font.render(time_text, True, TIMER_COLOR)
    timer_rect = timer_surface.get_rect(center=(center_x, center_y - 20))
    screen.blit(timer_surface, timer_rect)
    
    # 状态文本
    if timer_obj.paused:
        state_text = "已暂停"
        state_color = (150, 150, 150)
    elif timer_obj.is_resting:
        state_text = "休息中"
        state_color = REST_COLOR
    else:
        state_text = "运动中"
        state_color = ACTIVE_COLOR
    
    state_surface = info_font.render(state_text, True, state_color)
    state_rect = state_surface.get_rect(center=(center_x, center_y + 55))
    screen.blit(state_surface, state_rect)
    
    # 显示当前阶段总时长
    if timer_obj.paused:
        duration_text = ""
    elif timer_obj.is_resting:
        duration_text = f"休息时间: {REST_DURATION}s"
    else:
        duration_text = f"运动时间: {EXERCISE_DURATION}s"
    
    if duration_text:
        duration_surface = small_font.render(duration_text, True, (180, 180, 180))
        duration_rect = duration_surface.get_rect(center=(center_x, center_y + 90))
        screen.blit(duration_surface, duration_rect)

def draw_top_info(screen, total_time, groups, completed_exercises):
    """绘制顶部的统计信息"""
    # 背景
    top_bg = pygame.Rect(0, 0, WIDTH, 100)
    pygame.draw.rect(screen, (35, 35, 45), top_bg)
    pygame.draw.line(screen, ACCENT_COLOR, (0, 100), (WIDTH, 100), 2)
    
    # 标题
    title = title_font.render("运动训练计时器", True, ACCENT_COLOR)
    title_rect = title.get_rect(center=(WIDTH//2, 30))
    screen.blit(title, title_rect)
    
    # 统计信息
    total_minutes = int(total_time) // 60
    total_seconds = int(total_time) % 60
    time_str = f"{total_minutes:02d}:{total_seconds:02d}"
    
    # 总时间
    total_time_surface = info_font.render(f"总时间: {time_str}", True, TEXT_COLOR)
    total_time_rect = total_time_surface.get_rect(midleft=(WIDTH//2 - 320, 70))
    screen.blit(total_time_surface, total_time_rect)
    
    # 完成组数
    groups_surface = info_font.render(f"完成组数: {groups}", True, GROUP_COLOR)
    groups_rect = groups_surface.get_rect(center=(WIDTH//2, 70))
    screen.blit(groups_surface, groups_rect)
    
    # 完成项目数
    completed_surface = info_font.render(f"完成项目: {completed_exercises}", True, ACCENT_COLOR)
    completed_rect = completed_surface.get_rect(midright=(WIDTH//2 + 320, 70))
    screen.blit(completed_surface, completed_rect)

def main():
    timer = ExerciseTimer()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if timer.running and not timer.paused:
                        timer.pause()
                    else:
                        timer.start()
                elif event.key == pygame.K_r:
                    timer.reset()
        
        # 更新计时器
        timer.update()
        
        # 绘制背景
        screen.fill(BACKGROUND)
        
        # 绘制顶部的统计信息
        total_time = timer.get_total_time()
        draw_top_info(screen, total_time, timer.total_groups, timer.completed_exercises)
        
        # 绘制运动项目（增加间距的矩形布局）
        box_width = 280
        box_height = 85
        center_x = WIDTH // 2
        center_y = HEIGHT // 2 + 20
        
        # 第一行位置（项目1, 2, 3） - 增加水平间距
        row1_y = center_y - 180
        row1_positions = [
            (center_x - 400, row1_y),  # 项目1 - 左上
            (center_x, row1_y),        # 项目2 - 中上
            (center_x + 400, row1_y)   # 项目3 - 右上
        ]
        
        # 第二行位置（项目4, 5, 6） - 增加水平间距
        row2_y = center_y + 180
        row2_positions = [
            (center_x + 400, row2_y),  # 项目4 - 右下
            (center_x, row2_y),        # 项目5 - 中下
            (center_x - 400, row2_y)   # 项目6 - 左下
        ]
        
        # 合并位置
        positions = row1_positions + row2_positions
        
        exercise_rects = []
        for i, (pos, exercise) in enumerate(zip(positions, exercises)):
            active = (i == timer.current_exercise and not timer.is_resting)
            is_next = (i == (timer.current_exercise + 1) % len(exercises) and timer.is_resting)
            
            rect = draw_exercise_box(screen, exercise, pos[0], pos[1], box_width, box_height, active, is_next)
            exercise_rects.append(rect)
        
        # 绘制箭头连接（形成循环）
        arrow_pairs = [
            (0, 1),  # 1 -> 2
            (1, 2),  # 2 -> 3
            (2, 3),  # 3 -> 4
            (3, 4),  # 4 -> 5
            (4, 5),  # 5 -> 6
            (5, 0)   # 6 -> 1
        ]
        
        for start_idx, end_idx in arrow_pairs:
            # 获取开始和结束位置
            if start_idx < 3:  # 第一行
                start_pos = (exercise_rects[start_idx].right, exercise_rects[start_idx].centery)
            else:  # 第二行
                start_pos = (exercise_rects[start_idx].left, exercise_rects[start_idx].centery)
            
            if end_idx < 3:  # 第一行
                end_pos = (exercise_rects[end_idx].left, exercise_rects[end_idx].centery)
            else:  # 第二行
                end_pos = (exercise_rects[end_idx].right, exercise_rects[end_idx].centery)
            
            # 调整箭头位置以避免重叠
            if (start_idx == 2 and end_idx == 3):  # 3 -> 4（右上到右下）
                # 使用直线箭头，从项目3底部中心到项目4顶部中心
                start_pos = (exercise_rects[2].centerx, exercise_rects[2].bottom)
                end_pos = (exercise_rects[3].centerx, exercise_rects[3].top)
                
            elif (start_idx == 5 and end_idx == 0):  # 6 -> 1（左下到左上）
                # 使用直线箭头，从项目6顶部中心到项目1底部中心
                start_pos = (exercise_rects[5].centerx, exercise_rects[5].top)
                end_pos = (exercise_rects[0].centerx, exercise_rects[0].bottom)
            
            # 判断箭头是否应该高亮（休息状态）
            arrow_active = (timer.is_resting and start_idx == timer.current_exercise)
            
            # 绘制箭头
            draw_arrow(screen, start_pos, end_pos, arrow_active)
        
        # 绘制中间的状态计时器
        current_time = timer.get_current_time()
        draw_center_timer(screen, timer, current_time)
        
        # 在屏幕左下角显示操作提示（简洁版）
        tips = info_font.render("空格键: 开始/暂停  |  R键: 重置", True, (120, 120, 120))
        tips_rect = tips.get_rect(bottomleft=(20, HEIGHT - 20))
        screen.blit(tips, tips_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()