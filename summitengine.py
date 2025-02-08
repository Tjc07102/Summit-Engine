import pygame
import sys

class GameObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def update(self):
        pass

class Button(GameObject):
    def __init__(self, x, y, width, height, color, text, text_color, font_size):
        super().__init__(x, y, width, height, color)
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        super().draw(screen)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Label(GameObject):
    def __init__(self, x, y, width, height, color, text, text_color, font_size):
        super().__init__(x, y, width, height, color)
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        super().draw(screen)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class InputBox(GameObject):
    def __init__(self, x, y, width, height, color, text_color, font_size):
        super().__init__(x, y, width, height, color)
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.active = False

    def draw(self, screen):
        super().draw(screen)
        text_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.active:
            cursor_x = self.rect.x + 5 + self.font.size(self.text)[0]
            pygame.draw.line(screen, self.text_color, (cursor_x, self.rect.y + 5), (cursor_x, self.rect.y + self.rect.height - 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                print(f"Input: {self.text}")
                self.text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

class ScrollView(GameObject):
    def __init__(self, x, y, width, height, color, content_height):
        super().__init__(x, y, width, height, color)
        self.content_height = content_height
        self.scroll_y = 0

    def draw(self, screen):
        clip_rect = screen.get_clip()
        screen.set_clip(self.rect)
        super().draw(screen)
        for child in self.children:
            child.rect.y += self.scroll_y
            child.draw(screen)
            child.rect.y -= self.scroll_y
        screen.set_clip(clip_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.scroll_y = min(self.scroll_y + 10, 0)
                if event.button == 5:  # Scroll down
                    self.scroll_y = max(self.scroll_y - 10, -(self.content_height - self.rect.height))

class GameEngine:
    def __init__(self, width, height, title):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_objects = []
        self.ui_elements = []

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)

    def add_ui_element(self, ui_element):
        self.ui_elements.append(ui_element)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for ui_element in self.ui_elements:
                        if isinstance(ui_element, Button) and ui_element.is_clicked(event.pos):
                            print(f"Button '{ui_element.text}' clicked!")
            for ui_element in self.ui_elements:
                if isinstance(ui_element, (InputBox, ScrollView)):
                    ui_element.handle_event(event)

    def update(self):
        for game_object in self.game_objects:
            game_object.update()

    def render(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black
        for game_object in self.game_objects:
            game_object.draw(self.screen)
        for ui_element in self.ui_elements:
            ui_element.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # Limit to 60 FPS
        pygame.quit()
        sys.exit()

# Example usage
if __name__ == "__main__":
    engine = GameEngine(800, 600, "Simple Game Engine with UI")

    player = GameObject(100, 100, 50, 50, (255, 0, 0))
    engine.add_game_object(player)

    start_button = Button(300, 250, 200, 50, (0, 255, 0), "Start Game", (255, 255, 255), 36)
    engine.add_ui_element(start_button)

    title_label = Label(200, 100, 400, 50, (0, 0, 0), "My Awesome Game", (255, 255, 255), 48)
    engine.add_ui_element(title_label)

    input_box = InputBox(300, 350, 200, 40, (255, 255, 255), (0, 0, 0), 32)
    engine.add_ui_element(input_box)

    scroll_view = ScrollView(50, 400, 700, 150, (100, 100, 100), 300)
    scroll_view.children = [Label(50, 410 + i * 30, 200, 30, (0, 0, 0), f"Item {i+1}", (255, 255, 255), 24) for i in range(10)]
    engine.add_ui_element(scroll_view)

    engine.run()
