import pygame
import sys

# 1. 初始化
pygame.init()

# 屏幕設置 - 建議用 16:9 比例
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Genshin Impact Launcher")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 2. 資源加載
try:
    # 請確保 logo.png 在同一個文件夾下
    logo = pygame.image.load("download.png").convert_alpha()
    # 調整 Logo 大小
    logo = pygame.transform.smoothscale(logo, (500, 250))
    logo_rect = logo.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
except:
    logo = None
    print("提示：未發現 logo.png，將以文字模式運行")


def main():
    clock = pygame.time.Clock()
    alpha = 0  # Logo 透明度
    progress = 0  # 加載進度 (0 到 100)
    fade_finished = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 背景渲染（經典的純白啟動）
        screen.fill(WHITE)

        # --- 第一階段：Logo 漸變出現 ---
        if logo:
            if alpha < 255:
                alpha += 2  # 漸變速度
                logo.set_alpha(alpha)
            else:
                fade_finished = True
            screen.blit(logo, logo_rect)
        else:
            # 文字備選方案
            font = pygame.font.SysFont("Microsoft YaHei", 50)
            text = font.render("GENSHIN IMPACT", True, BLACK)
            screen.blit(text, (screen_width // 2 - 200, screen_height // 2 - 50))
            fade_finished = True

        # --- 第二階段：進度條渲染 ---
        if fade_finished:
            # 繪製進度條外框
            bar_width, bar_height = 400, 10
            bar_x = (screen_width - bar_width) // 2
            bar_y = screen_height // 2 + 150

            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), 1)

            # 模擬進度增長
            if progress < 100:
                progress += 0.5

                # 繪製填充進度
            current_bar_width = (progress / 100) * bar_width
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, current_bar_width, bar_height))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()