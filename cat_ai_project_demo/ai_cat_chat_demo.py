import os #读取输入法
os.environ["SDL_IME_SHOW_UI"] = "1"
import pygame
import sys
import ollama #读取大模型
import  textwrap #分段
import threading #分支

#初始化，定义了窗体大小 标题
pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("ai小猫")

#输入法出现位置
input_rect=pygame.Rect(5,400,380,30)
pygame.key.set_text_input_rect(input_rect)

#键盘录入初始化
pygame.key.start_text_input()
font = pygame.font.SysFont("simhei", 20) #字体大小设置
input_text=""
maxlenth = 30 #输入最大字数
#输入光标初始化（用户的和ai的）
cursor_visible = True
last_blink = pygame.time.get_ticks() #后面用于光标闪烁
ai_last_blink = pygame.time.get_ticks()
ai_underscore_visible = True

#图片初始化
current_image = 0
#控制图片刷新速度
counter = 0
delay = 8  # 调图片变换快慢
clock = pygame.time.Clock()

#运行状态
running = True

#ai回答初始化
answer = "幺鸡：你好呀，我是幺鸡喵~~"
temp_answer = ""
ai_thinking = False #检测ai是否在思考
is_asking = False #检测是否已经询问问题

#加载图片
cat_image = [
    pygame.transform.scale(pygame.image.load("sprites/idle_0.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_1.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_2.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_3.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_4.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_5.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_4.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_3.png").convert_alpha(), (400, 390)),
    pygame.transform.scale(pygame.image.load("sprites/idle_2.png").convert_alpha(), (400, 390)),
]


# 定义询问ai并回答的函数（这里用了模型的qwen2.5:1.5b）
def ask_ai(user_msg):
    global ai_thinking, temp_answer,is_asking
    try:
        ai_thinking = True #ai开始思考
        resp = ollama.chat(
            model="qwen2.5:1.5b",
            messages=[
                {"role": "system",
                 "content": "你的人设是一只软萌可爱的小猫咪，可说人话，名字是幺鸡。严守规则："
                            "1. 回答简短口语化，字数不超过50个字，不要说重复的话；"
                            "2. 禁止输出思考、推理、内心想法；"
                            "3. 每句回答后必须带上「喵~~」；"
                            "4. 不要说英文。"
                            "5.用户说再见是要回应再见。"
                            "参考示例："
                            "用户：你喜欢小鱼干吗？助手：当然喜欢！小鱼干香香脆脆，我超爱吃喵~~"
                            "用户：今天外面冷吗？助手：冷冷的，我只想窝在被窝里睡觉喵~~"
                            "用户：再见。助手：嗯，再见，期待和你再次聊天喵~~"},
                {"role": "user", "content": user_msg}
            ]
        )
        temp_answer = resp["message"]["content"]
        temp_answer = temp_answer.strip()
        #强制末尾加喵~~
        if not temp_answer.endswith("喵~~"):
            temp_answer = temp_answer + "喵~~"
        #ai回答出错输出内容
    except Exception:
        temp_answer = "哎呀，我有点懵喵~~"
        #初始化
    finally:
        ai_thinking = False
        is_asking = False

while running:
    #喵咪动图
    counter += 1
    if counter >= delay:
        current_image = (current_image + 1) % len(cat_image)
        counter = 0

    #光标闪烁(用户的和ai的)
    if pygame.time.get_ticks() - last_blink > 500:
        cursor_visible = not cursor_visible
        last_blink = pygame.time.get_ticks()
    if pygame.time.get_ticks() - ai_last_blink> 600:
        ai_underscore_visible = not ai_underscore_visible
        ai_last_blink = pygame.time.get_ticks()

    #键盘输入
    for event in pygame.event.get():
        #退出键
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        #输入信息
        if len(input_text) <= maxlenth: #检测是否输入内容超出最大值
            if event.type == pygame.TEXTINPUT:
                input_text += event.text
        if event.type == pygame.KEYDOWN:
            #回车打印
            if event.key == pygame.K_RETURN:
                if input_text and not is_asking:
                    is_asking = True
                    #后台子线程，防止动画卡顿
                    t = threading.Thread(target=ask_ai, args=(input_text,))
                    t.daemon=True
                    t.start()
                    input_text = "" #初始化
                else: #防止未输入句子
                    answer = "幺鸡：说句话嘛喵~~"
            #退格键
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
    #ai未回答时输出思考中
    if ai_thinking:
        answer = "(小猫思考中...)"
    else:
        #防止输入空值出错
        if temp_answer!="":
            answer = "幺鸡：" + temp_answer
            temp_answer = ""
    #后续可以加入一些小游戏


    #画面渲染
    #先覆盖
    screen.fill((220,220,220))
    #图片渲染
    screen.blit(cat_image[current_image], (0, 0))
    #光标+文字渲染
    display_text = f"> {"用户:"+input_text}"+("|"if cursor_visible else "")
    #输入文字分段
    input_lines = textwrap.wrap(display_text, width=19)
    input_y_offset = 400
    for input_line in input_lines:
        txt_surf=font.render(input_line, True, (0,0,0))
        screen.blit(txt_surf, (0,input_y_offset))
        input_y_offset += 25

    #分割线
    gap = font.render("-----------------------------------------", True, (0,128,0))
    screen.blit(gap, (0,450))

    #光标+ai回答分段
    display_answer = answer+("__"if ai_underscore_visible else "")
    lines = textwrap.wrap(display_answer, width=19)
    y_offset = 475
    for line in lines:
        answer_surf=font.render(line, True, (102,0,204))
        screen.blit(answer_surf, (20,y_offset))
        y_offset += 25

    pygame.display.update()

    clock.tick(30) #限制帧率

pygame.quit()