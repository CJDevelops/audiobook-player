# Audiobook Player


This project is an Audiobook Player that allows you to listen to your audiobook collection. It provides basic functionality for playing audiobooks, keeping track of the current position, and selecting audiobooks or series to play.

## Features

- Play audiobooks from your collection.
- Resume playback from the last stopped position.
- Select individual audiobooks or series to play.
- Automatically keeps track of the current position in each audiobook.

## Getting Started

### Prerequisites

To run this Audiobook Player, you need to have the following software installed:

- Python 3
- VLC media player

### Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/audiobook-player.git
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Place your audiobook files in the following folder structure, and modify the `LIBRARY_LOCATION` variable to your root folder
```scss
    root/
        author name/
            book title/
                (01) chapter name.mp3
                (02) chapter name.mp3
                author - title.jpg
                ...
            book title/
                (01) chapter name.mp3
                (02) chapter name.mp3
                author - title.jpg
                ...
        author name/
            series name/
                [01] book title/
                    (01) chapter name.mp3
                    (02) chapter name.mp3
                    author - title.jpg
                    ...
                [02] book title/
                    (01) chapter name.mp3
                    (02) chapter name.mp3                   
                    author - title.jpg
                    ...
            series name/
                [01] book title/
                    (01) chapter name.mp3
                    (02) chapter name.mp3
                    author - title.jpg
                    ...
```

### Usage
To start the Audiobook Player, run the following command:

```bash
python main.py
```

Once the Audiobook Player is running, you can use the main menu to interact with the player. Use the number keys to select options, and follow the on-screen instructions. `CTR + C ` to break out of the playing loop and return to the main menu

### Contributing
Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or create a pull request. Partically anyone that wants to make a UI for this!

