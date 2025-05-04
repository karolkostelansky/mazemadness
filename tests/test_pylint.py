from pylint.lint import Run
from pylint.reporters import CollectingReporter


def test_pylint_score():
    files_to_lint = [
        "server.py",
        "client.py",
        "config.py",
        "scenes/scene.py",
        "scenes/login_scene.py",
        "scenes/menu_scene.py",
        "scenes/game_scene.py",
        "widgets/button.py",
        "widgets/entry.py",
        "widgets/chatLog.py",
        "communication/communication.py",
        "communication/message.py",
        "communication/server_utils.py",
        "exceptions/my_exceptions.py",
        "maze/maze_generator.py",
        "maze/player_maze.py"

    ]

    """
         When I run this test on my macbook it passes, but when I tried on linux,
         it fails with score of 0.
         But when ran manually - 
         pylint server.py client.py config.py scenes/*.py widgets/*.py communication/*.py exceptions/*.py maze/*.py
         it gives score of 9.02

    """

    reporter = CollectingReporter()

    pylint_output = Run(files_to_lint, reporter=reporter, exit=False)

    score_threshold = 9.0
    score = pylint_output.linter.stats.global_note

    print(f"Pylint score: {score}")

    assert score >= score_threshold
