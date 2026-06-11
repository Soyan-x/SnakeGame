import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore

# অ্যান্ড্রয়েড ও ডেস্কটপের জন্য স্ক্রিন সাইজ ফিক্সড করা (৬০০x৪০০ রেট্রিও লুক)
Window.size = (600, 400)

class SnakeGameWidget(Widget):
    def __init__(self, **kwargs):
        super(SnakeGameWidget, self).__init__(**kwargs)
        
        # হাইস্কোর সেভ করার জন্য Kivy JsonStore
        self.store = JsonStore('highscore.json')
        if self.store.exists('score_data'):
            self.high_score = self.store.get('score_data')['high']
        else:
            self.high_score = 0
            self.store.put('score_data', high=0)

        self.BLOCK = 20
        self.reset_game()
        
        # টাচ স্টার্ট পজিশন ট্র্যাকিং
        self.touch_start_pos = None
        
        # গেম লুপ চালু করা (FPS = ১২)
        Clock.schedule_interval(self.update, 1.0 / 12.0)

    def reset_game(self):
        # শুরুতে সাপের শরীর (৩টি ব্লক)
        self.snake = [[300, 200], [280, 200], [260, 200]]
        self.d = [self.BLOCK, 0]  # শুরুর দিক (ডানে)
        self.score = 0
        self.over = False
        self.start_screen = True
        self.spawn_food()

    def spawn_food(self):
        while True:
            # ৬০০x৪০০ গ্রিডের ভেতরে র্যান্ডম পজিশন
            x = random.randrange(0, 600, self.BLOCK)
            y = random.randrange(0, 400, self.BLOCK)
            self.food = [x, y]
            if self.food not in self.snake:
                break

    # টাচ ও সোয়াইপ কন্ট্রোল
    def on_touch_down(self, touch):
        if self.start_screen:
            self.start_screen = False
            return True
        if self.over:
            self.reset_game()
            return True
        
        self.touch_start_pos = touch.pos
        return True

    def on_touch_up(self, touch):
        if self.touch_start_pos and not self.over and not self.start_screen:
            dx = touch.x - self.touch_start_pos[0]
            dy = touch.y - self.touch_start_pos[1]

            if abs(dx) > abs(dy):
                if dx > 30 and self.d != [-self.BLOCK, 0]:
                    self.d = [self.BLOCK, 0]
                elif dx < -30 and self.d != [self.BLOCK, 0]:
                    self.d = [-self.BLOCK, 0]
            else:
                if dy > 30 and self.d != [0, -self.BLOCK]:
                    self.d = [0, self.BLOCK]
                elif dy < -30 and self.d != [0, self.BLOCK]:
                    self.d = [0, -self.BLOCK]
            
            self.touch_start_pos = None
        return True

    # গেম লুপ এবং ড্রয়িং লজিক
    def update(self, dt):
        if not self.over and not self.start_screen:
            # নতুন মাথার পজিশন হিসাব করা
            h = [self.snake[0][0] + self.d[0], self.snake[0][1] + self.d[1]]
            
            # দেয়াল বা নিজের শরীরের সাথে ধাক্কা লাগলে গেম ওভার
            if h[0] < 0 or h[0] >= 600 or h[1] < 0 or h[1] >= 400 or h in self.snake:
                self.over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.store.put('score_data', high=self.high_score)
            else:
                self.snake.insert(0, h)
                # খাবার খেলে স্কোর বাড়বে, না খেলে লেজ কমবে
                if h == self.food:
                    self.score += 1
                    self.spawn_food()
                else:
                    self.snake.pop()

        # স্ক্রিন রিড্র করা (Canvas Clearing & Drawing)
        self.canvas.clear()
        with self.canvas:
            # ব্যাকগ্রাউন্ড (কালো)
            Color(20/255, 20/255, 20/255, 1)
            Rectangle(pos=(0, 0), size=(600, 400))

            if self.start_screen:
                # শুরুর স্ক্রিন টেক্সট (এখানে ক্যানভাসে ড্র করা হচ্ছে না, লেবেল দিয়ে করা যায়, তবে এটি সিম্পল রাখার জন্য)
                pass
            else:
                # ১. খাবার (লাল আপেল) ড্র করা
                Color(220/255, 50/255, 50/255, 1)
                Ellipse(pos=(self.food[0], self.food[1]), size=(self.BLOCK, self.BLOCK))
                # খাবারের সবুজ পাতা
                Color(0, 220/255, 0, 1)
                Ellipse(pos=(self.food[0] + 12, self.food[1] + 14), size=(6, 6))

                # ২. সাপের শরীর (মাথার আগের অংশগুলো)
                for segment in self.snake[1:]:
                    # বাইরের হালকা সবুজ
                    Color(0, 220/255, 0, 1)
                    Ellipse(pos=(segment[0], segment[1]), size=(self.BLOCK, self.BLOCK))
                    # ভেতরের গাঢ় সবুজ শেড
                    Color(0, 170/255, 0, 1)
                    Ellipse(pos=(segment[0] + 3, segment[1] + 3), size=(self.BLOCK - 6, self.BLOCK - 6))

                # ৩. সাপের মাথা (১ পিক্সেল বড়)
                head = self.snake[0]
                Color(0, 220/255, 0, 1)
                Ellipse(pos=(head[0] - 0.5, head[1] - 0.5), size=(self.BLOCK + 1, self.BLOCK + 1))

                # ৪. দিক অনুযায়ী চোখ ড্র করা
                Color(1, 1, 1, 1) # সাদা অংশ
                eye_size = 5
                pupil_size = 2
                
                if self.d == [self.BLOCK, 0]: # ডানে
                    e1_pos, e2_pos = (head[0]+12, head[1]+12), (head[0]+12, head[1]+3)
                elif self.d == [-self.BLOCK, 0]: # বামে
                    e1_pos, e2_pos = (head[0]+3, head[1]+12), (head[0]+3, head[1]+3)
                elif self.d == [0, self.BLOCK]: # ওপরে
                    e1_pos, e2_pos = (head[0]+3, head[1]+12), (head[0]+12, head[1]+12)
                else: # নিচে
                    e1_pos, e2_pos = (head[0]+3, head[1]+3), (head[0]+12, head[1]+3)

                Ellipse(pos=e1_pos, size=(eye_size, eye_size))
                Ellipse(pos=e2_pos, size=(eye_size, eye_size))
                
                Color(0, 0, 0, 1) # কাল মণি
                Ellipse(pos=(e1_pos[0]+1.5, e1_pos[1]+1.5), size=(pupil_size, pupil_size))
                Ellipse(pos=(e2_pos[0]+1.5, e2_pos[1]+1.5), size=(pupil_size, pupil_size))

        # টেক্সট/স্কোর আপডেট (Kivy-র টেক্সট ক্যানভাসের বাইরে লেবেল দিয়ে হ্যান্ডেল করা ভালো, এখানে উইজেট লেভেলে আপডেট দেওয়া হলো)
        self.parent_app.update_labels(self.score, self.high_score, self.over, self.start_screen)

class SnakeApp(App):
    def build(self):
        # মেইন লেআউট
        from kivy.uix.floatlayout import FloatLayout
        self.root_layout = FloatLayout(size=(600, 400))
        
        self.game_widget = SnakeGameWidget()
        self.game_widget.parent_app = self
        self.root_layout.add_widget(self.game_widget)
        
        # স্কোর লেবেল
        self.score_label = Label(text="Score: 0", pos_hint={'x': -0.4, 'y': 0.4}, font_size=20, color=(1, 215/255, 0, 1))
        self.high_label = Label(text=f"High: {self.game_widget.high_score}", pos_hint={'x': 0.4, 'y': 0.4}, font_size=20)
        
        # গেম ওভার এবং স্টার্ট মেসেজ লেবেল
        self.msg_label = Label(text="SNAKE GAME\nTap Screen to Start", font_size=32, halign="center", color=(0, 1, 0, 1))
        
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.high_label)
        self.root_layout.add_widget(self.msg_label)
        
        return self.root_layout

    def update_labels(self, score, high, over, start):
        self.score_label.text = f"Score: {score}"
        self.high_label.text = f"High: {high}"
        
        if start:
            self.msg_label.text = "SNAKE GAME\nTap Screen to Start"
            self.msg_label.color = (0, 1, 0, 1)
        elif over:
            self.msg_label.text = f"GAME OVER\nBest Score: {high}\nTap to Restart"
            self.msg_label.color = (1, 50/255, 50/255, 1)
        else:
            self.msg_label.text = "" # গেম চলাকালীন মেসেজ হাইড থাকবে

if __name__ == '__main__':
    SnakeApp().run()