import random
import tkinter as tk
import time


# Define the main game class
class Game(tk.Tk):

    def __init__(self):
        super().__init__()
        # Initialize game elements
        self.create_background()
        self.player = Player(self.canvas)
        self.NPC = NPC(self.canvas, self.bg.width()-50, self.bg.height()-30)
        self.food = self.add_food()
        self.bind_all_events()

        # Set initial game time
        self.time = 25
        self.game_started = time.time()
        # Create labels for time and boost
        self.time_label = self.canvas.create_text(self.bg.width()-50, 30, text="00:00", font="airal 30", fill="orangered")
        self.boost_label = self.canvas.create_text(self.bg.width()-50, 70, text="boost = 0", font="airal 15", fill="orangered")

    # Display remaining game time
    def display_game_time(self):
        t = self.time - int(time.time() - self.game_started)
        minutes = t // 60
        seconds = t % 60
        time_string = "{:02d}:{:02d}".format(minutes, seconds)
        self.canvas.itemconfig(self.time_label, text=time_string)
        return t

    # Display the current boost value
    def display_boost(self):
        boost_text = "boost = {}".format(str(self.player.total_boost))
        self.canvas.itemconfig(self.boost_label, text=boost_text)

    # Create the game background
    def create_background(self):
        self.bg = tk.PhotoImage(file="background.png")
        self.canvas = tk.Canvas(width=self.bg.width(), height=self.bg.height())
        self.canvas.pack()
        self.canvas.create_image(self.bg.width() / 2, self.bg.height() / 2, image=self.bg)

    # Get the current player position
    def get_player_position(self):
        return self.player.x, self.player.y

    # Bind keyboard events
    def bind_all_events(self):
        self.canvas.bind_all("<KeyPress-Right>", self.player.keypress_right)
        self.canvas.bind_all("<KeyRelease-Right>", self.player.keyrelease_right)
        self.canvas.bind_all("<KeyPress-Left>", self.player.keypress_left)
        self.canvas.bind_all("<KeyRelease-Left>", self.player.keyrelease_left)
        self.canvas.bind_all("<KeyPress-Up>", self.player.keypress_up)
        self.canvas.bind_all("<KeyRelease-Up>", self.player.keyrelease_up)
        self.canvas.bind_all("<KeyPress-Down>",self.player.keypress_down)
        self.canvas.bind_all("<KeyRelease-Down>",self.player.keyrelease_down)

    # Add a random food to the game
    def add_food(self):
        food_list = [Flake, Flake, Flake, Flake, Worm1, Worm1, Worm2, Pellet]
        food_type = random.choice(food_list)
        food = food_type(self.canvas)
        return food

    # Main game timer function
    def timer(self):
        self.player.tik()
        self.food.tik()
        self.NPC.tik()

        # Check if the current food is destroyed and add a new one
        if self.food.destroyed:
            self.food = self.add_food()
        # Check if the player eats the current food
        if self.player.eat(self.food):
            self.time += self.food.value
            self.player.add_to_speed_boost_list(self.food)
            self.food = self.add_food()

        # Check if the NPC eats the player
        if self.NPC.eat(self.player):
            self.game_over()

        # Update and display remaining game time and boost
        t = self.display_game_time()
        self.display_boost()

        # Check if the game time is up
        if t <= 0:
            self.game_over()
        else:
            # Call the timer function again after a delay
            self.canvas.after(40, self.timer)

    # Function called when the game is over
    def game_over(self):
        # Destroy player, food, and NPC
        self.player.destroy()
        self.food.destroy()
        self.NPC.destroy()

        # Display "GAME OVER" message
        self.canvas.create_text(self.bg.width()/2, 100, text="GAME OVER",
                                font="arial 60", fill="orangered")

        # Count and display statistics of eaten food
        f = w1 = w2 = p = 0
        for food in self.player.eaten_food:
            if isinstance(food, Flake):
                f += 1
            elif isinstance(food, Worm1):
                w1 += 1
            elif isinstance(food, Worm2):
                w2 += 1
            elif isinstance(food, Pellet):
                p += 1

        # Display food statistics
        self.f = self.display_food_statistics("food/flake_icon.png", f, 300)
        self.w1 = self.display_food_statistics("food/worm1_icon.png", w1, 350)
        self.w2 = self.display_food_statistics("food/worm2_icon.png", w2, 400)
        self.p = self.display_food_statistics("food/pellet_icon.png", p, 450)

    # Display food statistics
    def display_food_statistics(self, file_path, count, position):
        img = tk.PhotoImage(file=file_path)
        self.canvas.create_image(self.bg.width()/2, position, image=img)
        self.canvas.create_text(self.bg.width()/2+50, position, text=str(count), font="arial 20", fill="orangered")
        return img


# Base class for game sprites
class BaseSprite:
    def __init__(self, canvas, x, y):
        # Initialize sprite attributes
        self.canvas = canvas
        self.x, self.y = x, y
        # Create an image on the canvas at the specified coordinates
        self.id = self.canvas.create_image(x, y)
        # Flag to indicate if the sprite is destroyed
        self.destroyed = False

    # Load sprites from an image file
    def load_sprites(self, file_path, rows, cols):
        sprite_img = tk.PhotoImage(file=file_path)
        sprites = []
        # Calculate dimensions of each sprite
        height = sprite_img.height() // rows
        width = sprite_img.width() // cols
        for row in range(rows):
            for col in range(cols):
                l = col * width
                t = row * height
                r = (col + 1) * width
                b = (row + 1) * height
                # Create subimage for each sprite
                subimage = self.create_subimage(sprite_img, l, t, r, b)
                sprites.append(subimage)
        return sprites

    # Create a subimage from the original image
    def create_subimage(self, img, left, top, right, bottom):
        subimage = tk.PhotoImage()
        subimage.tk.call(subimage, "copy", img, "-from", left, top, right, bottom, "-to", 0, 0)
        return subimage

    # Destroy the sprite on the canvas
    def destroy(self):
        self.destroyed = True
        self.canvas.delete(self.id)


# Base class for food items, inheriting from BaseSprite
class Food(BaseSprite):
    value = 0
    speed = 0
    boost = 0
    boost_duration = 0

    # Constructor with canvas parameter, sets initial coordinates
    def __init__(self, canvas):
        x = random.randrange(100,1100)
        y = 0
        super().__init__(canvas, x, y)

    # Move the food item on the canvas, destroy if it reaches the bottom
    def move(self):
        y = self.y + self.speed
        if y <= self.canvas.winfo_height() - 20:
            self.y = y
        else:
            self.destroy()
        self.canvas.coords(self.id, self.x, self.y)

    # Update function for the food item
    def tik(self):
        self.move()


# Subclasses for different types of food items
class Worm1(Food):
    value = 5
    speed = 5
    boost = -2
    boost_duration = 3

    # Constructor, inherits from Food and sets sprite image
    def __init__(self, canvas):
        super().__init__(canvas)
        self.sprites = self.load_sprites("food/worm1.png", 1, 1)
        self.canvas.itemconfig(self.id, image=self.sprites[0])


class Worm2(Food):
    value = 6
    speed = 6
    boost = -1.5
    boost_duration = 3

    # Constructor, inherits from Food and sets sprite image
    def __init__(self, canvas):
        super().__init__(canvas)
        self.sprites = self.load_sprites("food/worm2.png", 1, 1)
        self.canvas.itemconfig(self.id, image=self.sprites[0])

class Pellet(Food):
    value = 9
    speed = 7
    boost = -2.5
    boost_duration = 3

    # Constructor, inherits from Food and sets sprite image
    def __init__(self, canvas):
        super().__init__(canvas)
        self.sprites = self.load_sprites("food/pellet.png", 1, 1)
        self.canvas.itemconfig(self.id, image=self.sprites[0])


class Flake(Food):
    value = 3
    speed = 3
    boost = 3
    boost_duration = 3
    flakes = ["food/flake1.png", "food/flake2.png", "food/flake3.png", "food/flake4.png", "food/flake5.png", ]

    # Constructor, inherits from Food and sets random flake sprite image
    def __init__(self, canvas):
        super().__init__(canvas)
        file_path = random.choice(self.flakes)
        self.sprites = self.load_sprites(file_path, 1, 1)
        self.canvas.itemconfig(self.id, image=self.sprites[0])


# Player class inheriting from BaseSprite
class Player(BaseSprite):
    LEFT = "left"
    RIGHT = "right"
    SWIM = "swim"
    IDLE = "idle"

    # Constructor with default position (x=100, y=100)
    def __init__(self, canvas, x=100, y=100):
        super().__init__(canvas, x, y)

        # Load sprites
        self.sprite_sheet = self.load_all_sprites()
        # Animations
        self.movement = self.IDLE
        self.direction = self.RIGHT
        self.sprite_idx = 0
        # Movement
        self.dx = self.dy = 0
        self.keys_pressed = 0
        self.eaten_food = []
        # Boost
        self.total_boost = 0
        self.speed_boost_list = []

    # Boost
    def add_to_speed_boost_list(self, food):
        # Add speed boost information to the list
        boost = food.boost
        duration = food.boost_duration
        duration_end = time.time() + food.boost_duration
        self.speed_boost_list.append({"boost": boost, "duration": duration, "duration_end": duration_end})
        self.calculate_total_boost()

    def calculate_total_boost(self):
        # Calculate total boost based on active boosts and remove expired boosts
        speed_boost_list_copy = self.speed_boost_list[:]
        for duration_end in speed_boost_list_copy:
            t = time.time()
            if duration_end["duration_end"] <= t:
                self.speed_boost_list.remove(duration_end)

        sum_boost = 0
        for boost in self.speed_boost_list:
            sum_boost += boost["boost"]
        self.total_boost = sum_boost
        return self.total_boost

    def eat(self, food):
        # Check if player is close enough to food, eat it, and add to eaten_food list
        dst = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
        if dst < 50:
            self.eaten_food.append(food)
            food.destroy()
            return True
        return False

    # Sprites
    def load_all_sprites(self):
        # Load player sprites for different movements and directions
        sprite_sheet = {
            self.IDLE: {
                self.LEFT: [],
                self.RIGHT: []
            },
            self.SWIM: {
                self.LEFT: [],
                self.RIGHT: []
            }
        }

        # Load individual sprites for idle and swimming animations
        sprite_sheet["idle"]["left"] = self.load_sprites("player/left_idle.png", 5, 4)  # rows, cols,
        sprite_sheet["idle"]["right"] = self.load_sprites("player/right_idle.png", 5, 4)  # rows, cols,
        sprite_sheet["swim"]["left"] = self.load_sprites("player/left_swim.png", 3, 4)  # rows, cols,
        sprite_sheet["swim"]["right"] = self.load_sprites("player/right_swim.png", 3, 4)  # rows, cols,

        return sprite_sheet

    def next_animation_index(self, idx):
        # Get the next animation index, looping back to 0 if it exceeds the maximum index
        idx += 1
        max_idx = len(self.sprite_sheet[self.movement][self.direction])
        idx = idx % max_idx
        return idx


    def tik(self):
        # Update sprite index and image during each animation cycle
        self.sprite_idx = self.next_animation_index(self.sprite_idx)
        img = self.sprite_sheet[self.movement][self.direction][self.sprite_idx]
        self.canvas.itemconfig(self.id, image=img)
        self.calculate_total_boost()
        if self.movement == self.SWIM:
            self.move()

    # Movement
    def move(self):
        # Move the player based on the current speed and direction
        x = self.x + self.dx
        y = self.y + self.dy
        if 55 <= x <= self.canvas.winfo_width() - 55 and 55 <= y <= self.canvas.winfo_height() - 35:
            self.x = x
            self.y = y
        self.canvas.coords(self.id, x, y)

    # Key events for movement
    def keypress_right(self, event):
        # Handle keypress event for moving right
        self.calculate_total_boost()
        self.keys_pressed += 1
        self.direction = self.RIGHT
        self.movement = self.SWIM
        self.dx = 5 + self.calculate_total_boost()

    def keyrelease_right(self, event):
        # Handle keyrelease event for moving right
        self.calculate_total_boost()
        self.keys_pressed -= 1
        self.dx = 0
        if self.keys_pressed < 1:
            self.movement = self.IDLE

    def keypress_left(self, event):
        # Handle keypress event for moving left
        self.calculate_total_boost()
        self.keys_pressed += 1
        self.direction = self.LEFT
        self.movement = self.SWIM
        self.dx = -5 - self.calculate_total_boost()

    def keyrelease_left(self, event):
        # Handle keyrelease event for moving left
        self.keys_pressed -= 1
        self.dx = 0
        if self.keys_pressed < 1:
            self.movement = self.IDLE

    def keypress_up(self, event):
        # Handle keypress event for moving up
        self.calculate_total_boost()
        self.keys_pressed += 1
        self.dy = -5 - self.calculate_total_boost()
        self.movement = self.SWIM

    def keyrelease_up(self, event):
        # Handle keyrelease event for moving up
        self.keys_pressed -= 1
        self.dy = 0
        if self.keys_pressed < 1:
            self.movement = self.IDLE

    def keypress_down(self, event):
        # Handle keypress event for moving down
        self.calculate_total_boost()
        self.keys_pressed += 1
        self.dy = +5 + self.calculate_total_boost()
        self.movement = self.SWIM

    def keyrelease_down(self, event):
        # Handle keyrelease event for moving down
        self.keys_pressed -= 1
        self.dy = 0
        if self.keys_pressed < 1:
            self.movement = self.IDLE


# NPC class inheriting from Player
class NPC(Player):

    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y)
        self.movement = self.SWIM
        self.direction = self.LEFT
        self.dx = 0
        self.dy = 0
        self.SPEED = 2.5

    # Sprites
    def load_all_sprites(self):
        # Load NPC sprites for different movements and directions
        sprite_sheet = {
            self.IDLE: {
                self.LEFT: [],
                self.RIGHT: []
            },
            self.SWIM: {
                self.LEFT: [],
                self.RIGHT: []
            }
        }

        # Load individual sprites for idle and swimming animations
        sprite_sheet["idle"]["left"] = self.load_sprites("npc/left_idle.png", 5, 4)  # rows, cols,
        sprite_sheet["idle"]["right"] = self.load_sprites("npc/right_idle.png", 5, 4)  # rows, cols,
        sprite_sheet["swim"]["left"] = self.load_sprites("npc/left_swim.png", 3, 4)  # rows, cols,
        sprite_sheet["swim"]["right"] = self.load_sprites("npc/right_swim.png", 3, 4)  # rows, cols,
        return sprite_sheet

    # Movement
    def move_towards_player(self):
        # Move NPC towards the player's position
        x, y = game.get_player_position()

        # Horizontal movement
        if x < self.x:
            self.dx = -self.SPEED
            self.direction = self.LEFT
            self.x += self.dx
        elif x > self.x:
            self.dx = self.SPEED
            self.direction = self.RIGHT
            self.x += self.dx
        elif x == self.x:
            self.dx = self.SPEED
            self.x += self.dx

        # Vertical movement
        if y < self.y:
            self.dy = -self.SPEED
            self.y += self.dy
        elif y > self.y:
            self.dy = self.SPEED
            self.y += self.dy

        # Update NPC position on the canvas
        self.canvas.coords(self.id, self.x, self.y)

    def eat(self, player):
        # Check if NPC is close enough to the player to eat
        dst = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        if dst < 50:
            return True
        return False

    def tik(self):
        # Update sprite index and image during each animation cycle
        self.sprite_idx = self.next_animation_index(self.sprite_idx)
        img = self.sprite_sheet[self.movement][self.direction][self.sprite_idx]
        self.canvas.itemconfig(self.id, image=img)
        self.move_towards_player()


game = Game()
game.timer()

game.mainloop()
