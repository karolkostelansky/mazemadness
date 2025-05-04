import pygame
from communication import communication, message
import config
from widgets.chatlog import Chatlog

from .scene import Scene


class MenuScene(Scene):
    def __init__(self, switch_scene_callback):
        """
            Initializes the menu scene with various UI elements like player list,
            challenges, and chatlog.
        """
        super().__init__()
        self.switch_scene_callback = switch_scene_callback
        self.font = pygame.font.Font(None, 36)
        self.players = set()

        self.player_scroll_offset = 0
        self.challenges_scroll_offset = 0

        self.scroll_speed = 20
        self.max_scroll = 0

        self.player_rects = []
        self.challenges_rects = []

        self.text_start_offset = 20
        self.space_between_list_items = 40

        self.chatlog = Chatlog(config.window_width * (2 / 3), 75, config.window_width,
                               config.window_height)

    def handle_loaded_object(self, loaded_message):
        """
        Handles server responses based on the loaded message.
        """
        match loaded_message.info:
            case "user_count_change":
                self.user_count_change(loaded_message.data)

            case "received_challenge":
                config.challenges_received.add(loaded_message.data)

            case "delete_challenge":
                try:
                    config.challenges_received.remove(loaded_message.data)
                except KeyError:
                    ...

            case "accepted_challenge":

                config.scene_manager.scenes["GameScene"].set_opponent(loaded_message.data[0])
                config.scene_manager.scenes["GameScene"].set_maze(loaded_message.data[1])

                config.scene_manager.switch_scene("GameScene")

            case "left_game":
                ...

            case "player_has_won_a_game":

                config.scores[loaded_message.data] += 1

            case "public_message":
                self.chatlog.add_message(loaded_message.data)

            case "challenge_no_longer_valid":
                self.remove_challenges(loaded_message.data)

            case _:
                ...

    def remove_challenges(self, players):
        """When challenge becomes invalid - the player started playing other game,
           function removes those two players from received challenges."""
        config.challenges_received = config.challenges_received - set(players)

    def send_public_message(self):
        """
        Sends the most recent public message to the server.
        """
        message_to_send = message.Message()
        message_to_send.info = "public_message"
        message_to_send.data = self.chatlog.messages[-1]

        communication.send_object(message_to_send, config.client)

    def start_game(self):
        """
        Switches to the game scene.
        """
        self.switch_scene_callback("GameScene")

    def set_players(self, player_names):
        """
        Updates the list of players to display.
        """
        self.players = player_names

    def create_challenge(self, opponent):
        """
        Sends a challenge to the specified opponent.
        """
        config.challenges_send.add(opponent)

        challenge = message.Message()
        challenge.info = "create_challenge"
        challenge.data = opponent
        communication.send_object(challenge, config.client)

    def delete_challenge(self, opponent):
        """
        Deletes a challenge to the specified opponent.
        """
        config.challenges_send.remove(opponent)

        challenge = message.Message()
        challenge.info = "delete_challenge"
        challenge.data = opponent
        communication.send_object(challenge, config.client)

    def accept_challenge(self, opponent):
        """
        Accepts a challenge from the specified opponent.
        """
        answer = message.Message()
        answer.info = "accept_challenge"
        answer.data = opponent

        communication.send_object(answer, config.client)

    def draw_players(self, screen):
        """
        Draws the list of players on the screen.
        """
        self.player_rects.clear()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        y_offset = 85 - self.player_scroll_offset
        self.max_scroll = max(0, (len(config.users_names) * self.space_between_list_items) - (
                screen.get_height() - 180))

        for (player, score) in sorted(config.scores.items(), key=lambda item: item[1],
                                      reverse=True):

            player_text_color = (0, 0, 0) if player != config.CLIENT_NAME else (0, 180, 0)
            player_text = self.font.render(f"{score}. {player}", True,
                                           player_text_color)

            text_rect = player_text.get_rect(topleft=(self.text_start_offset, y_offset))

            if text_rect.collidepoint(mouse_x, mouse_y):
                player_text = self.font.render(f"{score}. {player}", True,
                                               (0, 255, 0))

            if y_offset >= 80:
                screen.blit(player_text, (self.text_start_offset, y_offset))
                self.player_rects.append((text_rect, player))
            y_offset += self.space_between_list_items

        if len(config.users_names) == 0:
            player_text = self.font.render("No online players :(", True, (200, 0, 0))
            screen.blit(player_text, (self.text_start_offset, y_offset))

    def draw_challenges(self, screen):
        """
        Draws the list of challenges on the screen.
        """
        self.challenges_rects.clear()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        y_offset = 85 - self.challenges_scroll_offset

        try:
            for position, challenge in enumerate(config.challenges_received):
                challenge_text = self.font.render(f"{position + 1}. {challenge}", True,
                                                  config.BLACK)

                text_rect = challenge_text.get_rect(
                    topleft=(config.window_width / 3 + self.text_start_offset, y_offset))

                if text_rect.collidepoint(mouse_x, mouse_y):
                    challenge_text = self.font.render(f"{position + 1}. {challenge}", True,
                                                      config.GREEN)

                if y_offset >= 80:
                    screen.blit(challenge_text,
                                (config.window_width / 3 + self.text_start_offset, y_offset))
                    self.challenges_rects.append((text_rect, challenge))
                y_offset += self.space_between_list_items

            if len(config.challenges_received) == 0:
                player_text = self.font.render("No challenges", True, (200, 0, 0))
                screen.blit(player_text, (config.window_width / 3 + self.text_start_offset, 85))

        except RuntimeError:
            pass

    def handle_event(self, event):
        """
        Handles events such as mouse clicks or scrolls.
        """
        self.chatlog.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if event.button == 4:
                if mouse_x < config.window_width / 3:
                    self.player_scroll_offset = max(0,
                                                    self.player_scroll_offset - self.scroll_speed)

                elif config.window_width / 3 <= mouse_x <= 2 * config.window_width / 3:
                    self.challenges_scroll_offset = max(0, self.challenges_scroll_offset -
                                                        self.scroll_speed)

            elif event.button == 5:
                if mouse_x < config.window_width / 3:
                    self.player_scroll_offset = min(self.max_scroll,
                                                    self.player_scroll_offset + self.scroll_speed)

                elif config.window_width / 3 <= mouse_x <= 2 * config.window_width / 3:
                    self.challenges_scroll_offset = min(self.max_scroll,
                                                        self.challenges_scroll_offset +
                                                        self.scroll_speed)

            elif event.button == 1:
                if mouse_x < config.window_width / 3:
                    for text_rect, player in self.player_rects:
                        if player != config.CLIENT_NAME and text_rect.collidepoint(mouse_x,
                                                                                   mouse_y):
                            if player in config.challenges_send:
                                self.delete_challenge(player)
                            else:
                                self.create_challenge(player)
                            break

                elif config.window_width / 3 <= mouse_x <= 2 * config.window_width / 3:
                    for text_rect, challenge in self.challenges_rects:
                        if text_rect.collidepoint(mouse_x, mouse_y):
                            self.accept_challenge(challenge)

    def update(self, dt):
        """
        Updates the state of the scene, such as the chatlog.
        """
        self.chatlog.update(dt)

    def draw_menu(self, screen, titles):
        """
        Draws the menu with sections for players, challenges, and chat log.
        """
        y_position = 37

        pygame.draw.rect(screen, (0, 0, 255), (0, 0, screen.get_width(), 75))
        one_part = int(config.window_width / len(titles))
        for iteration, title in enumerate(titles):
            render_text = self.font.render(title, True, config.WHITE)
            want_x = int(one_part * (iteration + 1 / 2))
            x, y = config.center_text(render_text, want_x, y_position)

            pygame.draw.rect(screen, (200, 200, 200),
                             (want_x + one_part / 2, 0, 2, config.window_height))

            screen.blit(render_text, (x, y))

    def draw(self, screen):
        """
        Draws the scene, including the chatlog, players, challenges, and menu.
        """
        screen.fill(config.WHITE)

        self.chatlog.draw(screen)
        self.draw_menu(screen, ["Online Players", "Challenges", "Chat log"])

        self.draw_players(screen)
        self.draw_challenges(screen)

    def on_enter(self):
        """
        Called when the scene becomes active.
        """

        self.chatlog.set_messages(config.public_messages)
        self.chatlog.entry.active = True

        if config.AUTOMATIC_TESTING:
            for player in config.users_names:
                if player != config.CLIENT_NAME:
                    self.create_challenge(player)
