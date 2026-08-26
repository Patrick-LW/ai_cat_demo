import pygame
import sys
import ollama
import  textwrap

#初始化，定义了窗体大小 标题
pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("ai小猫")

#键盘录入初始化
pygame.key.start_text_input()
font = pygame.font.SysFont("simhei", 20) #字体大小设置
input_text=""
#输入光标初始化
cursor_visible = True
last_blink = pygame.time.get_ticks() #后面用于光标闪烁
#图片初始化
current_image = 0
#控制图片刷新速度
counter = 0
delay = 8  # 调图片变换快慢
clock = pygame.time.Clock()
#运行状态
running = True

#加载图片(图片为ai生成，之后考虑修改)
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


# 定义询问ai的函数（这里用了模型的deepseek-r1:1.5b，回答还比较笨，后续可以考虑调换）
def ask_ai(user_msg):
    resp = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=[
            {"role": "system",
             "content": "你的人设是一只软萌可爱的小猫咪，名字是幺鸡。严守规则：1. 回答简短口语化，字数不超过30个字，不要说重复的话；2. 禁止输出思考、推理、内心想法；3. 每句回答末尾必须带上「喵~~」；4. 不要说英文。参考示例：用户：你喜欢小鱼干吗？助手：当然喜欢！小鱼干香香脆脆，我超爱吃喵~~用户：今天外面冷吗？助手：冷冷的，我只想窝在被窝里睡觉喵~~"},
            {"role": "user", "content": user_msg}
        ]
    )
    return resp["message"]["content"]

#ai回答初始化
answer = "你好呀，我是幺鸡喵~~"

#句末强制加喵字
def end_miao(answer):
    answer = answer.strip()
    if not answer.endswith("喵~~"):
        answer = answer + "喵~~"
    return answer

while running:
    #喵咪动图
    counter += 1
    if counter >= delay:
        current_image = (current_image + 1) % len(cat_image)
        counter = 0

    #光标闪烁
    if pygame.time.get_ticks() - last_blink > 500:
        cursor_visible = not cursor_visible
        last_blink = pygame.time.get_ticks()

    #键盘输入（目前只支持英语（输入中文有点难，还没弄懂），之后考虑支持中文输入渲染）
    for event in pygame.event.get():
        #退出键
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        #输入信息
        if event.type == pygame.KEYDOWN:
            #回车打印
            if event.key == pygame.K_RETURN:
                if input_text:
                    answer = end_miao(ask_ai(input_text)) #录入ai生成的回答
                    input_text = "" #初始化
                else: #防止未输入句子
                    answer = "说句话嘛喵~~"
            #退格键
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            #打字
            else:
                input_text += event.unicode
        #后续可以加入一些小游戏


    #画面渲染
    #先覆盖
    screen.fill((35,35,35))
    #图片渲染
    screen.blit(cat_image[current_image], (0, 0))
    #光标+文字渲染
    display_text = f"> {input_text}"+("|"if cursor_visible else "")
    txt_surf=font.render(display_text, True, (255,255,255))
    screen.blit(txt_surf, (0,400))

    #进行分段(暂时只分回答部分，提问部分可后续再补（问太长模型也回答不了））
    lines = textwrap.wrap(answer, width=18)
    y_offset = 430
    for line in lines:
        answer_surf=font.render(line, True, (255,255,255))
        screen.blit(answer_surf, (3,y_offset))
        y_offset += 25
    pygame.display.update()

    clock.tick(30) #限制游戏帧率

pygame.quit()